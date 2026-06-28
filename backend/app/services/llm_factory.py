from typing import Optional, Any
from app.core.config import settings
from app.services.gemini_service import GeminiService

class OpenAIService:
    """Fallback stub wrapper for OpenAIService to maintain provider factory compatibility."""
    def __init__(self):
        logger_name = "AI Sales Copilot"
        import logging
        self.logger = logging.getLogger(logger_name)
        self.logger.info("OpenAIService initialized (compatibility wrapper).")

    async def generate(self, prompt: str, **kwargs) -> str:
        return "OpenAI generated content placeholder"

class MockService:
    """Mock Service helper wrapper."""
    async def generate(self, prompt: str, **kwargs) -> str:
        return "Deterministic Enterprise Demo Response"

class LLMFactory:
    """Centralized LLM provider factory mapping engine requests to Gemini, OpenAI, or Mock services."""

    @staticmethod
    def get_llm(provider: Optional[str] = None) -> Any:
        selected_provider = provider or settings.LLM_PROVIDER
        selected_provider = selected_provider.lower()

        if selected_provider == "gemini":
            return GeminiService()
        elif selected_provider == "openai":
            return OpenAIService()
        else:
            return MockService()
