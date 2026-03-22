import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("VSEGPT_API_KEY")
if not api_key:
    raise ValueError("Не найден VSEGPT_API_KEY в .env")

MODEL_NAME = os.getenv("VSEGPT_MODEL", "openai/gpt-5.1-chat")  
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1200"))

client = OpenAI(
    api_key=api_key,
    base_url="https://api.vsegpt.ru/v1"
)

def call_llm(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=MAX_TOKENS
        )

        if not response or not getattr(response, "choices", None):
            raise ValueError(f"Пустой или некорректный ответ: {response}")

        content = response.choices[0].message.content
        if not content:
            raise ValueError(f"Ответ без content: {response}")

        return content

    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return json.dumps({"error": "llm_failed", "details": str(e)}, ensure_ascii=False)