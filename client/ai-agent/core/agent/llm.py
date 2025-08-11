# core/agent/llm.py

from langchain_openai import OpenAI

from core.config import get_settings

_model = None


def get_llm() -> OpenAI:
    global _model
    llm_settings = get_settings()
    if _model is None:
        _model = OpenAI(
            api_key=llm_settings.OPENAI_API_KEY,
            model=llm_settings.OPENAI_MODEL,
        )
    return _model
