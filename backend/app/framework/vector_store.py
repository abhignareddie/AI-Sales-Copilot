"""Vector Store implementations supporting ChromaDB and a Mock in-memory database fallback."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.framework.interfaces import BaseVectorStore
from app.core.config import settings
from app.core.logging import logger


class ChromaVectorStore(BaseVectorStore):
    """Production vector store implementation using HTTP Client to query ChromaDB server."""

    def __init__(self):
        self._client = None
        self._collection = None
        self._embedder = None

    def _get_embedder(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._embedder

    def _get_collection(self):
        if self._collection is None:
            import chromadb
            self._client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
            self._collection = self._client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        collection = self._get_collection()
        embedder = self._get_embedder()
        embedding = embedder.encode([text])[0].tolist()

        collection.upsert(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata or {}],
        )
        logger.info(f"[ChromaStore] Inserted doc_id: {doc_id}")

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        collection = self._get_collection()
        embedder = self._get_embedder()
        query_embedding = embedder.encode([query])[0].tolist()

        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        if filters:
            kwargs["where"] = filters

        results = collection.query(**kwargs)
        documents = []
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                dist = results["distances"][0][i] if results.get("distances") else 0.5
                documents.append({
                    "content": doc,
                    "metadata": meta,
                    "source": meta.get("source", "unknown"),
                    "similarity_score": round(1.0 - dist, 4),
                })
        return documents


class MockVectorStore(BaseVectorStore):
    """In-memory vector store mock. Simulates semantic search via simple keyword mapping."""

    def __init__(self):
        self.store: Dict[str, Dict[str, Any]] = {}
        # Prepopulate with dummy sales guidelines
        self.add_document("doc1", "Discount rule: 10% max for standard accounts, up to 20% for Enterprise with VP approval.", {"document_type": "policy"})
        self.add_document("doc2", "Sales playbook: Focus on discovery phase, ask about timeline, pain points, and current tools.", {"document_type": "playbook"})
        self.add_document("doc3", "Pricing: Premium tier is $150/user/month. Basic tier is $50/user/month.", {"document_type": "pricing"})

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.store[doc_id] = {
            "content": text,
            "metadata": metadata or {},
        }

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        q = query.lower()
        matches = []
        for doc_id, doc in self.store.items():
            # Basic keyword score
            score = 0.1
            words = q.split()
            for w in words:
                if w in doc["content"].lower():
                    score += 0.25
            
            # Apply type filters if requested
            if filters and doc["metadata"].get("document_type") != filters.get("document_type"):
                continue

            matches.append({
                "content": doc["content"],
                "metadata": doc["metadata"],
                "source": doc["metadata"].get("source", doc_id),
                "similarity_score": min(score, 1.0),
            })
        
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:top_k]


class VectorStoreFactory:
    """Factory to retrieve vector store instance depending on service configuration."""

    @classmethod
    def get_store(cls, mock: bool = False) -> BaseVectorStore:
        if mock:
            return MockVectorStore()
        try:
            return ChromaVectorStore()
        except Exception as e:
            logger.warning(f"Could not connect to ChromaDB, using mock store: {e}")
            return MockVectorStore()
