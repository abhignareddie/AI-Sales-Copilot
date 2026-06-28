import os
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.knowledge_document import KnowledgeDocument
from app.rag.document_processor import DocumentProcessor
from app.rag.vector_service import VectorService
from app.rag.hybrid_search import HybridSearcher
from app.core.logging import logger
from app.core.config import settings

class ChunkerFactory:
    """Helper factory for chunkers."""
    @classmethod
    def get_chunker(cls, strategy: str = "recursive", chunk_size: int = None, overlap: int = None):
        from app.rag.chunker import (
            FixedSizeChunker, RecursiveCharacterChunker, 
            SlidingWindowChunker, HeadingAwareChunker, SemanticChunker
        )
        chunk_size = chunk_size or settings.RAG_CHUNK_SIZE
        overlap = overlap or settings.RAG_CHUNK_OVERLAP
        
        if strategy == "fixed":
            return FixedSizeChunker(chunk_size, overlap)
            
        if strategy == "sliding":
            return SlidingWindowChunker(chunk_size, overlap)
            
        if strategy == "heading":
            return HeadingAwareChunker(chunk_size, overlap)
            
        if strategy == "semantic":
            return SemanticChunker(chunk_size, overlap)
            
        return RecursiveCharacterChunker(chunk_size, overlap)

class RAGManager:
    """Orchestrates metadata DB storage, ingestion pipelines, version control, and search."""
    
    def __init__(self, db: AsyncSession, embedding_provider: str = "local"):
        self.db = db
        self.vector_service = VectorService(embedding_provider=embedding_provider)
        self.hybrid_searcher = HybridSearcher(self.vector_service)

    async def check_duplicate(self, file_hash: str) -> Optional[KnowledgeDocument]:
        """Check if a document with this hash already exists in database."""
        stmt = select(KnowledgeDocument).where(
            and_(
                KnowledgeDocument.file_hash == file_hash,
                KnowledgeDocument.is_archived == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_document_metadata(
        self, 
        title: str, 
        doc_type: str, 
        file_path: str, 
        uploaded_by: int, 
        file_hash: str
    ) -> KnowledgeDocument:
        """Create or version-update a KnowledgeDocument in SQL database."""
        # Check if same title exists to auto-version increment
        stmt = select(KnowledgeDocument).where(
            and_(
                KnowledgeDocument.title == title,
                KnowledgeDocument.is_archived == False
            )
        ).order_by(KnowledgeDocument.version.desc())
        result = await self.db.execute(stmt)
        existing_doc = result.scalars().first()
        
        version = 1
        if existing_doc:
            version = existing_doc.version + 1
            
        doc = KnowledgeDocument(
            title=title,
            document_type=doc_type,
            uploaded_file=file_path,
            uploaded_by=uploaded_by,
            file_hash=file_hash,
            version=version,
            status="pending",
            is_archived=False
        )
        
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def process_and_index(
        self, 
        doc_id: int, 
        namespace: str = "default", 
        chunk_strategy: str = "recursive"
    ) -> bool:
        """Parse, chunk, extract KG, generate embeddings, and index document."""
        stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
        result = await self.db.execute(stmt)
        doc = result.scalar_one_or_none()
        
        if not doc:
            logger.error(f"Document with ID {doc_id} not found.")
            return False
            
        try:
            doc.status = "processing"
            await self.db.commit()
            
            # 1. Parse document
            parsed = DocumentProcessor.parse(doc.uploaded_file)
            content = parsed["content"]
            metadata = parsed["metadata"]
            
            # 2. Extract Knowledge Graph entities & relationships
            from app.rag.knowledge_graph import KnowledgeGraphExtractor
            kg_extractor = KnowledgeGraphExtractor()
            kg_data = kg_extractor.extract(content)
            
            # 3. Create chunker and split
            chunker = ChunkerFactory.get_chunker(chunk_strategy)
            chunks = chunker.split(content, metadata)
            
            # Add KG context metadata to chunks
            for chunk in chunks:
                chunk["metadata"].update({
                    "doc_title": doc.title,
                    "doc_version": doc.version,
                    "entities": ", ".join([e["name"] for e in kg_data["entities"][:5]]),
                    "relations_count": len(kg_data["relations"])
                })
                
            # 4. Index into Vector Store
            success = self.vector_service.add_document_chunks(
                namespace=namespace,
                doc_id=str(doc.id),
                chunks=chunks,
                version=str(doc.version)
            )
            
            if success:
                doc.status = "indexed"
                # Rebuild BM25 index on the searcher for instant queries
                # In production this would fetch all active chunks from DB/vector-store
                self.hybrid_searcher.rebuild_bm25(chunks)
            else:
                doc.status = "failed"
                
            await self.db.commit()
            return success
            
        except Exception as e:
            logger.error(f"Failed to process and index document {doc_id}: {e}", exc_info=True)
            doc.status = "failed"
            await self.db.commit()
            return False

    async def archive_document(self, doc_id: int, namespace: str = "default") -> bool:
        """Soft-delete/archive document: mark is_archived in SQL, remove from Vector DB."""
        stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
        result = await self.db.execute(stmt)
        doc = result.scalar_one_or_none()
        
        if not doc:
            return False
            
        doc.is_archived = True
        doc.status = "archived"
        await self.db.commit()
        
        # Deletes from vector service
        self.vector_service.delete_document(namespace, str(doc.id), version=str(doc.version))
        return True

    async def restore_document(self, doc_id: int, namespace: str = "default") -> bool:
        """Restore archived document and trigger re-processing to add to Vector DB."""
        stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
        result = await self.db.execute(stmt)
        doc = result.scalar_one_or_none()
        
        if not doc:
            return False
            
        doc.is_archived = False
        doc.status = "pending"
        await self.db.commit()
        
        # Re-trigger indexing
        return await self.process_and_index(doc.id, namespace)
