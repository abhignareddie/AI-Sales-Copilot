"""Core interfaces for the Enterprise Agentic AI Framework."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class BaseLLMProvider(ABC):
    """Abstract interface for LLM interaction."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text from LLM."""
        pass


class BaseVectorStore(ABC):
    """Abstract interface for RAG document chunk storage and retrieval."""

    @abstractmethod
    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Index a document chunk."""
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant document chunks."""
        pass


class BaseMemoryProvider(ABC):
    """Abstract interface for long-term agent memory."""

    @abstractmethod
    async def store(self, key: str, memory_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store memory under a unique key and category."""
        pass

    @abstractmethod
    async def retrieve(self, key: str, memory_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve memory records matching criteria."""
        pass


class BaseTool(ABC):
    """Abstract interface for reusable LangChain/Framework tools."""

    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Run tool action."""
        pass


class BaseAgent(ABC):
    """Abstract interface for workflow agents."""

    name: str
    description: str

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent business logic on the state."""
        pass
