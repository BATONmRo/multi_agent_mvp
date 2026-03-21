
import json
import re
from llm import call_llm
from prompts import ROUTE_AGENT_SYSTEM_PROMPT, VALIDATOR_SYSTEM_PROMPT, BASELINE_SYSTEM_PROMPT
from schemas import RouteAgentOutput, ValidationOutput, BaselineOutput


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

def route_agent(target: str) -> RouteAgentOutput:
    user_prompt = f"Целевая задача: {target}"

    raw = call_llm(ROUTE_AGENT_SYSTEM_PROMPT, user_prompt)

    print("RAW route_agent response:")
    print(raw)

    data = extract_json(raw)

    return RouteAgentOutput(**data)


def validator_agent(route_output: RouteAgentOutput) -> ValidationOutput:
    user_prompt = f"""
Проверь следующий маршрут:
{route_output.model_dump_json(indent=2, ensure_ascii=False)}
"""

    raw = call_llm(VALIDATOR_SYSTEM_PROMPT, user_prompt)

    print("RAW validator_agent response:")
    print(raw)

    data = extract_json(raw)

    return ValidationOutput(**data)

def validator_agent(route_output: RouteAgentOutput) -> ValidationOutput:
    user_prompt = f"""
Проверь следующий маршрут:
{route_output.model_dump_json(indent=2, ensure_ascii=False)}
"""

    raw = call_llm(VALIDATOR_SYSTEM_PROMPT, user_prompt)

    try:
        data = json.loads(raw)
    except Exception:
        print("Ошибка парсинга JSON в validator_agent. Ответ модели:")
        print(raw)
        raise

    return ValidationOutput(**data)

def baseline_agent(task: str) -> BaselineOutput:
    raw = call_llm(BASELINE_SYSTEM_PROMPT, task)

    return BaselineOutput(
        task=task,
        answer=raw.strip()
    )
