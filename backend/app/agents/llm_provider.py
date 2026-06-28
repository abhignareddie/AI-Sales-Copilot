"""LLM provider factory — shared by all agents.

Provides OpenAI as primary and Gemini as fallback.
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from app.core.config import settings
from app.core.logging import logger


def get_llm(
    temperature: float = 0.2,
    model: str | None = None,
    provider: str = "auto",
) -> BaseChatModel:
    """
    Get an LLM instance.

    Args:
        temperature: Sampling temperature.
        model: Override model name.
        provider: 'openai', 'gemini', or 'auto' (try openai first).

    Returns:
        A LangChain chat model instance.
    """
    if provider == "auto":
        if settings.OPENAI_API_KEY:
            provider = "openai"
        elif settings.GEMINI_API_KEY:
            provider = "gemini"
        else:
            logger.warning("No API key configured — using mock responses")
            provider = "openai"  # Will fail gracefully in agents

    if provider == "openai":
        return ChatOpenAI(
            model=model or settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature,
            request_timeout=settings.AGENT_TIMEOUT,
        )
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=model or settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
