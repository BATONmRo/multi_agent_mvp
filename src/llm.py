import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLMConfigError(Exception):
    pass


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise LLMConfigError(
            "OPENROUTER_API_KEY not found. Put it into .env"
        )

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-OpenRouter-Title": "multi-agent-mvp",
        },
    )


def get_default_model() -> str:
    return os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")