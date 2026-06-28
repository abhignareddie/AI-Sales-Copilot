"""Vector Tool — RAG pipeline: document chunking, embedding, ChromaDB storage/retrieval."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging import logger


class VectorTool:
    """
    RAG pipeline for chunking documents, generating embeddings,
    and storing/retrieving from ChromaDB.
    """

    def __init__(self):
        self._client = None
        self._collection = None
        self._embedder = None

    def _get_embedder(self):
        """Lazy-load sentence-transformers model."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
            except Exception as e:
                logger.error(f"Failed to load embedder: {e}")
                raise
        return self._embedder

    def _get_collection(self):
        """Lazy-load ChromaDB collection."""
        if self._collection is None:
            try:
                import chromadb
                self._client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=settings.CHROMA_PORT,
                )
                self._collection = self._client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info(f"ChromaDB collection '{settings.CHROMA_COLLECTION}' ready")
            except Exception as e:
                logger.error(f"ChromaDB unavailable: {e}")
                raise
        return self._collection

    # ─── Document Processing ─────────────────────────────

    def _read_pdf(self, file_path: str) -> str:
        """Extract text from PDF."""
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _read_docx(self, file_path: str) -> str:
        """Extract text from DOCX."""
        from docx import Document
        doc = Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)

    def _read_txt(self, file_path: str) -> str:
        """Read plain text file."""
        return Path(file_path).read_text(encoding="utf-8")

    def read_document(self, file_path: str) -> str:
        """Read a document based on its extension."""
        ext = Path(file_path).suffix.lower()
        readers = {
            ".pdf": self._read_pdf,
            ".docx": self._read_docx,
            ".txt": self._read_txt,
            ".csv": self._read_txt,
        }
        reader = readers.get(ext)
        if not reader:
            raise ValueError(f"Unsupported file type: {ext}")
        return reader(file_path)

    # ─── Chunking ─────────────────────────────────────────

    def chunk_text(
        self,
        text: str,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> list[str]:
        """Split text into overlapping chunks."""
        size = chunk_size or settings.RAG_CHUNK_SIZE
        overlap = chunk_overlap or settings.RAG_CHUNK_OVERLAP

        if len(text) <= size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunk = text[start:end]
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(".")
                last_newline = chunk.rfind("\n")
                break_point = max(last_period, last_newline)
                if break_point > size * 0.5:
                    chunk = text[start : start + break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return [c for c in chunks if c]

    # ─── Embedding & Storage ──────────────────────────────

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        embedder = self._get_embedder()
        embeddings = embedder.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def ingest_document(
        self,
        file_path: str,
        metadata: dict | None = None,
    ) -> dict:
        """Full pipeline: read → chunk → embed → store in ChromaDB."""
        text = self.read_document(file_path)
        chunks = self.chunk_text(text)
        embeddings = self.generate_embeddings(chunks)
        collection = self._get_collection()

        # Generate deterministic IDs
        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        ids = [f"{file_hash}_chunk_{i}" for i in range(len(chunks))]

        # Build metadata for each chunk
        base_meta = metadata or {}
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_meta = {
                **base_meta,
                "source": file_path,
                "chunk_index": i,
                "total_chunks": len(chunks),
            }
            metadatas.append(chunk_meta)

        collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info(
            f"Ingested '{file_path}': {len(chunks)} chunks into "
            f"'{settings.CHROMA_COLLECTION}'"
        )
        return {
            "file_path": file_path,
            "chunks_created": len(chunks),
            "collection": settings.CHROMA_COLLECTION,
        }

    # ─── Retrieval ────────────────────────────────────────

    def search(
        self,
        query: str,
        top_k: int | None = None,
        where: dict | None = None,
    ) -> list[dict]:
        """Semantic search over ChromaDB collection."""
        k = top_k or settings.RAG_TOP_K
        collection = self._get_collection()
        query_embedding = self.generate_embeddings([query])[0]

        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": k,
        }
        if where:
            kwargs["where"] = where

        results = collection.query(**kwargs)

        documents = []
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 0
                documents.append({
                    "content": doc,
                    "metadata": meta,
                    "source": meta.get("source", "unknown"),
                    "similarity_score": round(1 - distance, 4),
                    "chunk_index": meta.get("chunk_index", 0),
                })

        logger.info(f"Vector search: '{query[:50]}...' returned {len(documents)} results")
        return documents

    def hybrid_search(
        self,
        query: str,
        keyword_query: str | None = None,
        top_k: int | None = None,
        where: dict | None = None,
    ) -> list[dict]:
        """Combined semantic + keyword search."""
        semantic_results = self.search(query, top_k=top_k, where=where)

        # If keyword query provided, also search by document content
        if keyword_query:
            collection = self._get_collection()
            try:
                keyword_results = collection.query(
                    query_texts=[keyword_query],
                    n_results=top_k or settings.RAG_TOP_K,
                )
                if keyword_results and keyword_results.get("documents"):
                    existing_sources = {
                        (d.get("source"), d.get("chunk_index"))
                        for d in semantic_results
                    }
                    for i, doc in enumerate(keyword_results["documents"][0]):
                        meta = keyword_results["metadatas"][0][i] if keyword_results.get("metadatas") else {}
                        key = (meta.get("source"), meta.get("chunk_index"))
                        if key not in existing_sources:
                            distance = keyword_results["distances"][0][i] if keyword_results.get("distances") else 0
                            semantic_results.append({
                                "content": doc,
                                "metadata": meta,
                                "source": meta.get("source", "unknown"),
                                "similarity_score": round(1 - distance, 4),
                                "chunk_index": meta.get("chunk_index", 0),
                            })
            except Exception as e:
                logger.warning(f"Keyword search failed: {e}")

        # Sort by similarity and limit
        semantic_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return semantic_results[: (top_k or settings.RAG_TOP_K)]
