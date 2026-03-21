import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("Не найден OPENROUTER_API_KEY в .env")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        if response is None:
            raise ValueError("Пустой ответ от LLM")

        if not hasattr(response, "choices") or not response.choices:
            raise ValueError(f"Ответ без choices: {response}")

        message = response.choices[0].message
        if message is None or message.content is None:
            raise ValueError(f"Ответ без message.content: {response}")

        return message.content

    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return '{"error": "llm_failed"}'