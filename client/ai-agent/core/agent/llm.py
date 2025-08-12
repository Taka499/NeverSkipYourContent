# core/agent/llm.py

from langchain_openai import ChatOpenAI

from core.config import get_settings

_model = None


def get_llm() -> ChatOpenAI:
    global _model
    llm_settings = get_settings()
    if _model is None:
        _model = ChatOpenAI(
            api_key=llm_settings.OPENAI_API_KEY,
            model=llm_settings.OPENAI_MODEL,
        )
    return _model
