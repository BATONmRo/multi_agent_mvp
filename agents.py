import json
import re
from typing import Any, Dict, List, Optional, Union
from tools import tool_find_methods, check_reagents
from memory import build_memory_summary

from llm import call_llm
from prompts import (
    TASK_PARSER_SYSTEM_PROMPT,
    ROUTE_AGENT_SYSTEM_PROMPT,
    SAFETY_AGENT_SYSTEM_PROMPT,
    BASELINE_SYSTEM_PROMPT,
    PAIRWISE_JUDGE_SYSTEM_PROMPT,
)
from schemas import (
    TaskParserOutput,
    RouteAgentOutput,
    SafetyAssessmentOutput,
    BaselineOutput,
    RouteCandidate,
    RouteStep,
)

# ----------------------------
# LLM as a judje
# ----------------------------

def build_user_prompt(task, baseline_answer, mas_answer, reference_context=""):
    return f"""
Task:
{task}

Reference_context:
{reference_context}

Baseline_answer:
{baseline_answer}

MAS_answer:
{mas_answer}
""".strip()


def run_judge(llm_client, task, baseline_answer, mas_answer, reference_context=""):
    user_prompt = build_user_prompt(
        task=task,
        baseline_answer=baseline_answer,
        mas_answer=mas_answer,
        reference_context=reference_context
    )

    try:
        response = llm_client.chat.completions.create(
            model="openrouter/free",
            temperature=0,
            messages=[
                {"role": "system", "content": PAIRWISE_JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        raw = response.choices[0].message.content
        return extract_json(raw)

    except Exception as e:
        print("[JUDGE ERROR]", e)
        return {"error": "judge_failed"}
    
# ----------------------------
# Helpers
# ----------------------------

def extract_json(text: str) -> dict:
    """
    Пытается аккуратно вытащить JSON-объект из ответа модели.
    Поддерживает:
    - чистый JSON
    - ```json ... ```
    - JSON, обёрнутый в поясняющий текст
    """
    if not text or not text.strip():
        raise ValueError("Модель вернула пустой ответ")

    cleaned = text.strip()

    # Убираем markdown fenced blocks
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    # Если весь ответ уже JSON
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return json.loads(cleaned)

    # Ищем первый JSON-объект
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError(f"Не удалось извлечь JSON из ответа модели:\n{text}")


def _safe_llm_json(system_prompt: str, user_payload: Union[str, dict]) -> dict:
    """
    Унифицированный вызов LLM с безопасным парсингом JSON.
    """
    if isinstance(user_payload, dict):
        payload = json.dumps(user_payload, ensure_ascii=False, indent=2)
    else:
        payload = user_payload

    raw = call_llm(system_prompt, payload)

    print(f"RAW LLM RESPONSE ({system_prompt[:40]}...):")
    print(raw)

    data = extract_json(raw)

    if data.get("error") == "llm_failed":
        raise ValueError("LLM returned error=llm_failed")

    return data


# ----------------------------
# Fallback builders
# ----------------------------

def _fallback_task_parser(task: str) -> TaskParserOutput:
    return TaskParserOutput(
        task_type="single_route_assessment",
        original_task=task,
        target=task,
        starting_materials=[],
        constraints={},
        confidence=0.0,
    )


def _fallback_route(task_or_target: str) -> RouteAgentOutput:
    return RouteAgentOutput(
        target=task_or_target,
        routes=[
            RouteCandidate(
                id="route_fallback",
                summary="LLM route generation failed",
                steps=[
                    RouteStep(
                        reaction="fallback_route",
                        reagents=["unknown"],
                        conditions="llm_failed",
                    )
                ],
            )
        ],
        route_count=1,
        confidence=0.0,
    )


def _fallback_safety(route_result: RouteAgentOutput) -> SafetyAssessmentOutput:
    route_ids = [route.id for route in route_result.routes] if route_result.routes else []

    return SafetyAssessmentOutput(
        target=route_result.target,
        overall_assessment="unable_to_assess",
        recommended_route_id=route_ids[0] if route_ids else None,
        route_assessments=[
            {
                "route_id": route_id,
                "risk_level": "unknown",
                "score": 0.0,
                "hazardous_components": [],
                "process_risks": ["safety_llm_failed"],
                "justification": "Не удалось выполнить safety assessment",
            }
            for route_id in route_ids
        ],
    )


# ----------------------------
# Agents
# ----------------------------

def task_parser_agent(task: str) -> TaskParserOutput:
    """
    Разбирает пользовательскую задачу в структурированный формат:
    - target
    - starting_materials
    - constraints
    - режим single_route_assessment / multi_route_ranking
    """
    try:
        data = _safe_llm_json(TASK_PARSER_SYSTEM_PROMPT, task)
        return TaskParserOutput(**data)
    except Exception as e:
        print(f"[task_parser_agent ERROR] {e}")
        return _fallback_task_parser(task)


def route_agent(parsed_task: Union[str, TaskParserOutput, dict], memory=None) -> RouteAgentOutput:
    """
    Генерирует 1 или несколько маршрутов синтеза в структурированном виде.
    Можно передать:
    - строку task
    - TaskParserOutput
    - dict
    """
    try:
        if isinstance(parsed_task, str):
            payload = {"task": parsed_task}
            fallback_target = parsed_task
        elif isinstance(parsed_task, TaskParserOutput):
            payload = parsed_task.model_dump()
            fallback_target = parsed_task.target
        else:
            payload = parsed_task
            fallback_target = payload.get("target", "unknown_target")

        if memory:
            payload["memory_summary"] = build_memory_summary(memory)
            payload["memory_context"] = {
                "parsed_task": memory.get("parsed_task"),
                "methods_result": memory.get("methods_result"),
                "reagents_result": memory.get("reagents_result"),
                "history": memory.get_history(),
            }

        data = _safe_llm_json(ROUTE_AGENT_SYSTEM_PROMPT, payload)
        result = RouteAgentOutput(**data)

        if memory:
            memory.set("route_result", result.model_dump())
            memory.add_event("route_agent", "success", result.model_dump())

        return result

    except Exception as e:
        print(f"[route_agent ERROR] {e}")
        fallback = _fallback_route(fallback_target)

        if memory:
            memory.add_event("route_agent", "fallback", fallback.model_dump())

        return fallback


def safety_agent(
    route_result: RouteAgentOutput,
    methods_context: Optional[Any] = None,
    reagents_context: Optional[Any] = None,
    memory=None,
) -> SafetyAssessmentOutput:
    """
    Оценивает маршрут(ы) по safety-критериям.
    На вход получает:
    - route_result
    - опционально methods_context из RAG/tool_find_methods
    - опционально reagents_context из check_reagents
    """
    try:
        payload = {
            "route_result": route_result.model_dump(),
            "methods_context": methods_context,
            "reagents_context": reagents_context,
        }

        if memory:
            payload["memory_summary"] = build_memory_summary(memory)
            payload["memory_context"] = {
                "parsed_task": memory.get("parsed_task"),
                "route_result": memory.get("route_result"),
                "methods_result": memory.get("methods_result"),
                "reagents_result": memory.get("reagents_result"),
                "extracted_reagents": memory.get("extracted_reagents"),
                "history": memory.get_history(),
            }

        data = _safe_llm_json(SAFETY_AGENT_SYSTEM_PROMPT, payload)
        result = SafetyAssessmentOutput(**data)

        if memory:
            memory.set("safety_result", result.model_dump())
            memory.add_event("safety_agent", "success", result.model_dump())

        return result

    except Exception as e:
        print(f"[safety_agent ERROR] {e}")
        fallback = _fallback_safety(route_result)

        if memory:
            memory.add_event("safety_agent", "fallback", fallback.model_dump())

        return fallback


def validator_agent(route_result: RouteAgentOutput) -> SafetyAssessmentOutput:
    """
    Backward compatibility:
    старый validator_agent теперь ведёт на safety_agent.
    """
    return safety_agent(route_result)


def baseline_agent(task: str) -> BaselineOutput:
    """
    Базовый single-agent ответ для сравнения с multi-agent pipeline.
    """
    raw = call_llm(BASELINE_SYSTEM_PROMPT, task)
    return BaselineOutput(task=task, answer=raw)


# ----------------------------
# Tool wrappers
# ----------------------------

def methods_agent(query: str):
    """
    Tool/RAG слой: поиск методов синтеза / процедур / справочного контекста.
    """
    try:
        return tool_find_methods(query)
    except Exception as e:
        print(f"[methods_agent ERROR] {e}")
        return {
            "status": "error",
            "query": query,
            "results": [],
            "message": str(e),
        }


def reagents_agent(reagents: List[str]):
    """
    Tool/RAG слой: проверка опасностей реагентов.
    """
    try:
        return check_reagents(reagents)
    except Exception as e:
        print(f"[reagents_agent ERROR] {e}")
        return {
            "status": "error",
            "reagents": reagents,
            "results": [],
            "message": str(e),
        }

