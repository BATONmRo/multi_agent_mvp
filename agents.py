import json
from llm import call_llm
from prompts import ROUTE_AGENT_SYSTEM_PROMPT
from schemas import RouteAgentOutput
from prompts import VALIDATOR_SYSTEM_PROMPT
from schemas import ValidationOutput


import json
from llm import call_llm
from prompts import ROUTE_AGENT_SYSTEM_PROMPT, VALIDATOR_SYSTEM_PROMPT
from schemas import RouteAgentOutput, ValidationOutput


def route_agent(target: str) -> RouteAgentOutput:
    user_prompt = f"Целевая задача: {target}"

    raw = call_llm(ROUTE_AGENT_SYSTEM_PROMPT, user_prompt)

    print("RAW route_agent response:")
    print(raw)

    try:
        data = json.loads(raw)
    except Exception:
        print("Ошибка парсинга JSON в route_agent")
        raise

    return RouteAgentOutput(**data)


def validator_agent(route_output: RouteAgentOutput) -> ValidationOutput:
    user_prompt = f"""
Проверь следующий маршрут:
{route_output.model_dump_json(indent=2, ensure_ascii=False)}
"""

    raw = call_llm(VALIDATOR_SYSTEM_PROMPT, user_prompt)

    print("RAW validator_agent response:")
    print(raw)

    try:
        data = json.loads(raw)
    except Exception:
        print("Ошибка парсинга JSON в validator_agent")
        raise

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
