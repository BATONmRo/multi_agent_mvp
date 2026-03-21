
import json
import re
from llm import call_llm
from prompts import ROUTE_AGENT_SYSTEM_PROMPT, VALIDATOR_SYSTEM_PROMPT, BASELINE_SYSTEM_PROMPT
from schemas import RouteAgentOutput, ValidationOutput, BaselineOutput
from tools import tool_find_methods, check_reagents


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

