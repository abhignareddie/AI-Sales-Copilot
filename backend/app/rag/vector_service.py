import uuid
from typing import List, Dict, Any, Optional
import chromadb
from app.core.config import settings
from app.core.logging import logger
from app.rag.embeddings import EmbeddingFactory

class VectorService:
    """Service to interact with ChromaDB supporting namespaces, versioning, and incremental updates."""
    
    def __init__(self, host: str = None, port: int = None, embedding_provider: str = "local"):
        self.host = host or settings.CHROMA_HOST
        self.port = port or settings.CHROMA_PORT
        self.embeddings = EmbeddingFactory.get_embeddings(embedding_provider)
        self.client = None
        
        if getattr(settings, "MOCK_EMBEDDINGS", False):
            try:
                self.client = chromadb.EphemeralClient()
                logger.info("MOCK_EMBEDDINGS enabled. Forced local ChromaDB EphemeralClient to prevent port conflicts.")
            except Exception as ex:
                logger.error(f"Failed to initialize EphemeralClient: {ex}")
            return

        try:
            self.client = chromadb.HttpClient(host=self.host, port=self.port)
            logger.info(f"Connected to ChromaDB server at {self.host}:{self.port}")
        except Exception as e:
            logger.warning(f"Could not connect to ChromaDB server: {e}. Operating in mock/in-memory mode.")
            try:
                self.client = chromadb.EphemeralClient()
                logger.info("ChromaDB EphemeralClient initialized as fallback.")
            except Exception as ex:
                logger.error(f"Failed to create EphemeralClient: {ex}")
                self.client = None

    def _get_collection_name(self, namespace: str, version: Optional[str] = None) -> str:
        """Resolve collection name based on namespace and optional version."""
        # Chroma naming rules: 3-63 chars, alphanumeric, underscore or hyphen
        clean_ns = namespace.lower().replace("-", "_")
        clean_ns = "".join(c for c in clean_ns if c.isalnum() or c == "_")
        
        # Clip if too long
        base_name = f"ns_{clean_ns}"[:45]
        if version:
            clean_ver = version.lower().replace(".", "_")
            clean_ver = "".join(c for c in clean_ver if c.isalnum() or c == "_")
            return f"{base_name}_v{clean_ver}"[:63]
        return base_name

    def _get_collection(self, namespace: str, version: Optional[str] = None):
        """Get or create a ChromaDB collection for the namespace."""
        if not self.client:
            return None
        col_name = self._get_collection_name(namespace, version)
        try:
            return self.client.get_or_create_collection(
                name=col_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            logger.error(f"Error getting/creating collection {col_name}: {e}")
            return None

    def add_document_chunks(self, namespace: str, doc_id: str, chunks: List[Dict[str, Any]], version: Optional[str] = None) -> bool:
        """Add or update document chunks incrementally. Deletes previous chunks for the doc_id first."""
        collection = self._get_collection(namespace, version)
        if not collection:
            return False
            
        # First, delete existing chunks for this document to ensure clean incremental update
        self.delete_document(namespace, doc_id, version)
        
        ids = []
        documents = []
        embeddings = []
        metadatas = []
        
        for chunk in chunks:
            chunk_id = f"{doc_id}_chunk_{chunk['metadata'].get('chunk_index', uuid.uuid4().hex)}"
            text = chunk["text"]
            
            ids.append(chunk_id)
            documents.append(text)
            metadatas.append({
                **chunk.get("metadata", {}),
                "doc_id": str(doc_id),
                "namespace": namespace
            })
            
        # Generate embeddings in batch
        if documents:
            try:
                embeddings = self.embeddings.embed_documents(documents)
                collection.upsert(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                logger.info(f"Successfully upserted {len(documents)} chunks for doc_id {doc_id} in namespace {namespace}")
                return True
            except Exception as e:
                logger.error(f"Error adding chunks to vector db: {e}", exc_info=True)
                return False
        return True

    def delete_document(self, namespace: str, doc_id: str, version: Optional[str] = None) -> bool:
        """Delete all chunks belonging to a specific document ID from a namespace."""
        collection = self._get_collection(namespace, version)
        if not collection:
            return False
            
        try:
            # We filter by metadata "doc_id"
            collection.delete(where={"doc_id": str(doc_id)})
            logger.info(f"Deleted chunks for doc_id {doc_id} in namespace {namespace}")
            return True
        except Exception as e:
            logger.error(f"Error deleting chunks for doc_id {doc_id}: {e}")
            return False

    def search(
        self, 
        namespace: str, 
        query: str, 
        top_k: int = 5, 
        filters: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search vector database in the namespace."""
        collection = self._get_collection(namespace, version)
        if not collection:
            return []
            
        try:
            query_emb = self.embeddings.embed_query(query)
            
            kwargs = {
                "query_embeddings": [query_emb],
                "n_results": top_k,
            }
            if filters:
                kwargs["where"] = filters
                
            results = collection.query(**kwargs)
            
            hits = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                    dist = results["distances"][0][i] if results.get("distances") else 0.5
                    hits.append({
                        "content": doc,
                        "metadata": meta,
                        "similarity_score": round(1.0 - dist, 4)
                    })
            return hits
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
            
    def delete_namespace(self, namespace: str, version: Optional[str] = None) -> bool:
        """Delete an entire namespace / collection."""
        if not self.client:
            return False
        col_name = self._get_collection_name(namespace, version)
        try:
            self.client.delete_collection(col_name)
            logger.info(f"Deleted collection {col_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {col_name}: {e}")
            return False
