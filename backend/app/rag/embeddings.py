from typing import List, Union
import numpy as np
from app.core.config import settings
from app.core.logging import logger

class BaseEmbeddings:
    """Interface for generating text embeddings."""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents."""
        raise NotImplementedError
        
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query."""
        raise NotImplementedError

class SentenceTransformerEmbeddings(BaseEmbeddings):
    """Local HuggingFace embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = None):
        model_name = model_name or settings.EMBEDDING_MODEL
        if getattr(settings, "MOCK_EMBEDDINGS", False):
            logger.info("MOCK_EMBEDDINGS enabled. Bypassing SentenceTransformer local load.")
            self.model = None
            return
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            logger.info(f"Initialized SentenceTransformer with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}. Falling back to mock embeddings.")
            self.model = None
            
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.model:
            return [self._mock_embed(text) for text in texts]
        embeddings = self.model.encode(texts)
        return [emb.tolist() for emb in embeddings]
        
    def embed_query(self, text: str) -> List[float]:
        if not self.model:
            return self._mock_embed(text)
        embedding = self.model.encode([text])[0]
        return embedding.tolist()
        
    def _mock_embed(self, text: str) -> List[float]:
        # Generate stable mock embedding of size 384 based on hash of text
        h = hash(text)
        np.random.seed(h & 0xFFFFFFFF)
        return np.random.uniform(-1, 1, 384).tolist()

class OpenAIEmbeddings(BaseEmbeddings):
    """OpenAI API embeddings."""
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI Client for Embeddings: {e}")
                
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.client:
            # Fallback to SentenceTransformers
            logger.warning("OpenAI key not configured or client failed, falling back to local embeddings.")
            fallback = SentenceTransformerEmbeddings()
            return fallback.embed_documents(texts)
            
        try:
            response = self.client.embeddings.create(input=texts, model=self.model)
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI Embeddings error: {e}. Falling back to mock.")
            fallback = SentenceTransformerEmbeddings()
            return fallback.embed_documents(texts)
            
    def embed_query(self, text: str) -> List[float]:
        if not self.client:
            logger.warning("OpenAI key not configured or client failed, falling back to local embeddings.")
            fallback = SentenceTransformerEmbeddings()
            return fallback.embed_query(text)
            
        try:
            response = self.client.embeddings.create(input=[text], model=self.model)
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI Embeddings error: {e}. Falling back to mock.")
            fallback = SentenceTransformerEmbeddings()
            return fallback.embed_query(text)

class EmbeddingFactory:
    """Factory to get the configured embedding implementation."""
    
    @classmethod
    def get_embeddings(cls, provider: str = "local") -> BaseEmbeddings:
        if provider == "openai":
            return OpenAIEmbeddings()
        return SentenceTransformerEmbeddings()
