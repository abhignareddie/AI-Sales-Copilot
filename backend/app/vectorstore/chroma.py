"""ChromaDB Vector Store — Full RAG service for the application."""

from __future__ import annotations

from app.agents.tools.vector_tool import VectorTool
from app.core.config import settings
from app.core.logging import logger


# Singleton vector tool instance
_vector_tool: VectorTool | None = None


def get_vector_tool() -> VectorTool:
    """Get the shared VectorTool singleton."""
    global _vector_tool
    if _vector_tool is None:
        _vector_tool = VectorTool()
    return _vector_tool


def get_chroma_client():
    """Get ChromaDB client for direct access."""
    try:
        import chromadb
        client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )
        logger.info("ChromaDB client initialized")
        return client
    except Exception as e:
        logger.warning(f"ChromaDB not available: {e}")
        return None
