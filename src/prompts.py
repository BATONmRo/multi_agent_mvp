import json
from typing import Any, Dict

from llm import get_client, get_default_model


def chat_json(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    temperature: float = 0.2,
) -> Dict[str, Any]:
    client = get_client()
    model_name = model or get_default_model()

    response = client.chat.completions.create(
        model=model_name,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content or ""

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "status": "fail",
            "result": {"raw_text": content},
            "reason": "Model did not return valid JSON",
        }