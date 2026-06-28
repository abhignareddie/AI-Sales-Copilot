"""Knowledge Tool — Searches enterprise knowledge base via ChromaDB."""

from __future__ import annotations

from app.agents.tools.vector_tool import VectorTool
from app.core.logging import logger


class KnowledgeTool:
    """
    Searches the enterprise knowledge base stored in ChromaDB.
    Wraps VectorTool for knowledge-specific queries.
    """

    def __init__(self):
        self.vector_tool = VectorTool()

    def search_knowledge(
        self,
        query: str,
        top_k: int = 5,
        document_type: str | None = None,
    ) -> list[dict]:
        """
        Search enterprise knowledge base.

        Categories include: Sales Playbook, Pricing Policy, Discount Rules,
        Product Documentation, Competitor Guides, FAQs.
        """
        where = None
        if document_type:
            where = {"document_type": document_type}

        results = self.vector_tool.search(query=query, top_k=top_k, where=where)
        logger.info(f"Knowledge search: '{query[:50]}...' → {len(results)} results")
        return results

    def search_with_context(
        self,
        query: str,
        customer_context: str = "",
        top_k: int = 5,
    ) -> list[dict]:
        """Search with additional customer context for better relevance."""
        enriched_query = f"{query}\nCustomer context: {customer_context}" if customer_context else query
        return self.vector_tool.hybrid_search(
            query=enriched_query,
            keyword_query=query,
            top_k=top_k,
        )

    def ingest_knowledge_document(
        self,
        file_path: str,
        title: str = "",
        document_type: str = "general",
    ) -> dict:
        """Ingest a document into the knowledge base."""
        metadata = {
            "title": title,
            "document_type": document_type,
        }
        return self.vector_tool.ingest_document(file_path=file_path, metadata=metadata)
