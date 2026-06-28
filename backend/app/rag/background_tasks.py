from app.database.session import async_session_factory
from app.rag.manager import RAGManager
from app.core.logging import logger

async def async_index_document(doc_id: int, namespace: str = "default", chunk_strategy: str = "recursive"):
    """Background task to run document processing and vector database indexing."""
    logger.info(f"Starting background processing for document ID: {doc_id}")
    
    async with async_session_factory() as db:
        try:
            # We commit inside RAGManager
            manager = RAGManager(db)
            success = await manager.process_and_index(
                doc_id=doc_id, 
                namespace=namespace, 
                chunk_strategy=chunk_strategy
            )
            if success:
                logger.info(f"Successfully finished background indexing of document ID: {doc_id}")
            else:
                logger.error(f"Background indexing of document ID {doc_id} failed.")
        except Exception as e:
            logger.error(f"Error in background indexing task for document ID {doc_id}: {e}", exc_info=True)
