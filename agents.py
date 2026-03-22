
import json
import re
from llm import call_llm
from schemas import RouteAgentOutput, ValidationOutput, BaselineOutput, RouteStep
from tools import tool_find_methods, check_reagents


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
# LLM as a judge
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
    if not text or not text.strip():
        raise ValueError("Модель вернула пустой ответ")

    cleaned = text.strip()

    # Убираем markdown-блоки ```json ... ```
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    # Если весь ответ уже JSON-объект
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return json.loads(cleaned)

    # Ищем первый JSON-объект в тексте
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError(f"Не удалось извлечь JSON из ответа модели:\n{text}")


def route_agent(task: str) -> RouteAgentOutput:
    raw = call_llm(ROUTE_AGENT_SYSTEM_PROMPT, task)
    print("RAW route_agent response:")
    print(raw)

    try:
        data = json.loads(raw)
    except Exception:
        return RouteAgentOutput(
            target=task,
            steps=[
                RouteStep(
                    reaction="fallback_route",
                    reagents=["unknown"],
                    conditions="llm_failed"
                )
            ],
            confidence=0.0
        )

    if data.get("error") == "llm_failed":
        return RouteAgentOutput(
            target=task,
            steps=[
                RouteStep(
                    reaction="fallback_route",
                    reagents=["unknown"],
                    conditions="llm_failed"
                )
            ],
            confidence=0.0
        )

    return RouteAgentOutput(**data)


def validator_agent(route_result: RouteAgentOutput) -> ValidationOutput:
    raw = call_llm(VALIDATOR_SYSTEM_PROMPT, route_result.model_dump_json(ensure_ascii=False))
    print("RAW validator_agent response:")
    print(raw)

    try:
        data = json.loads(raw)
    except Exception:
        return ValidationOutput(
            valid=False,
            issues=["validator_llm_failed"],
            suggestions=["Проверить API / модель OpenRouter"]
        )

    if data.get("error") == "llm_failed":
        return ValidationOutput(
            valid=False,
            issues=["validator_llm_failed"],
            suggestions=["Проверить API / модель OpenRouter"]
        )

    return ValidationOutput(**data)

def baseline_agent(task: str) -> BaselineOutput:
    raw = call_llm(BASELINE_SYSTEM_PROMPT, task)
    return BaselineOutput(task=task, answer=raw)

def methods_agent(query):
    result = tool_find_methods(query)
    return result


def reagents_agent(reagents):
    result = check_reagents(reagents)
    return result

