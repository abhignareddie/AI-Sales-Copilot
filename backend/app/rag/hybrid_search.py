import math
import re
from typing import List, Dict, Any, Optional
from collections import Counter
from app.core.logging import logger
from app.rag.vector_service import VectorService

class BM25Index:
    """In-memory BM25 retriever for local keyword search."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_count = 0
        self.avg_doc_len = 0.0
        self.doc_lens = []
        self.vocab = {}
        self.idf = {}
        self.doc_term_freqs = []
        self.documents = []  # holds list of dicts with content and metadata

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    def index_documents(self, docs: List[Dict[str, Any]]) -> None:
        """Indexes a list of documents. doc is expected to have 'content' and 'metadata'."""
        self.documents = docs
        self.doc_count = len(docs)
        if self.doc_count == 0:
            return
            
        self.doc_lens = []
        self.doc_term_freqs = []
        df = Counter()
        
        total_len = 0
        for doc in docs:
            tokens = self._tokenize(doc["content"])
            doc_len = len(tokens)
            self.doc_lens.append(doc_len)
            total_len += doc_len
            
            tf = Counter(tokens)
            self.doc_term_freqs.append(tf)
            
            for term in tf.keys():
                df[term] += 1
                
        self.avg_doc_len = total_len / self.doc_count if self.doc_count > 0 else 0.0
        
        # Calculate IDF
        for term, freq in df.items():
            # Standard Lucene BM25 IDF
            self.idf[term] = math.log(1.0 + (self.doc_count - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search BM25 index with optional metadata filtering."""
        query_tokens = self._tokenize(query)
        if not query_tokens or self.doc_count == 0:
            return []
            
        scores = []
        for i, doc in enumerate(self.documents):
            # Apply metadata filters if present
            if filters:
                match = True
                for fk, fv in filters.items():
                    if doc["metadata"].get(fk) != fv:
                        match = False
                        break
                if not match:
                    continue
                    
            score = 0.0
            doc_len = self.doc_lens[i]
            tf = self.doc_term_freqs[i]
            
            for term in query_tokens:
                if term not in self.idf:
                    continue
                term_tf = tf.get(term, 0)
                # BM25 formula
                numerator = term_tf * (self.k1 + 1.0)
                denominator = term_tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                score += self.idf[term] * (numerator / denominator)
                
            if score > 0:
                scores.append((score, doc))
                
        scores.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scores[:top_k]:
            results.append({
                "content": doc["content"],
                "metadata": doc["metadata"],
                "bm25_score": round(score, 4)
            })
        return results

class CrossEncoderReranker:
    """Lightweight CrossEncoder re-ranking simulation."""
    
    def __init__(self):
        self.model = None
        if getattr(settings, "MOCK_EMBEDDINGS", False):
            logger.info("MOCK_EMBEDDINGS enabled. Bypassing CrossEncoder model load.")
            return
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("Successfully loaded SentenceTransformers CrossEncoder model.")
        except Exception as e:
            logger.warning(f"Could not load CrossEncoder model ({e}). Using simulated fallback scoring.")

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """Reranks the top candidates using a CrossEncoder or heuristic alignment."""
        if not documents:
            return []
            
        if self.model:
            try:
                pairs = [[query, doc["content"]] for doc in documents]
                scores = self.model.predict(pairs)
                for i, score in enumerate(scores):
                    documents[i]["rerank_score"] = float(score)
            except Exception as e:
                logger.error(f"CrossEncoder prediction failed: {e}. Falling back to simulated scoring.")
                self._simulated_rerank(query, documents)
        else:
            self._simulated_rerank(query, documents)
            
        documents.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        return documents[:top_n]

    def _simulated_rerank(self, query: str, documents: List[Dict[str, Any]]) -> None:
        """Fallback scoring using phrase matching, case-insensitive keyword proximity and overlap."""
        q_clean = query.lower()
        q_words = set(re.findall(r"\w+", q_clean))
        
        for doc in documents:
            content_clean = doc["content"].lower()
            
            # Phrase match bonus
            phrase_bonus = 0.0
            if q_clean in content_clean:
                phrase_bonus = 2.0
            
            # Term overlap count
            overlap = len(q_words.intersection(re.findall(r"\w+", content_clean)))
            overlap_ratio = overlap / len(q_words) if q_words else 0.0
            
            # Combine similarity_score or bm25_score with overlap metrics
            base_score = doc.get("similarity_score", doc.get("bm25_score", 0.1))
            
            doc["rerank_score"] = round(base_score * 0.4 + overlap_ratio * 0.4 + phrase_bonus * 0.2, 4)

class HybridSearcher:
    """Orchestrates keyword (BM25) and semantic (Vector) search using RRF merging and CrossEncoder re-ranking."""
    
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
        self.bm25_index = BM25Index()

    def rebuild_bm25(self, all_chunks: List[Dict[str, Any]]) -> None:
        """Build BM25 index over a static list of chunks."""
        self.bm25_index.index_documents(all_chunks)

    def search(
        self, 
        namespace: str, 
        query: str, 
        top_k: int = 5, 
        filters: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Performs Hybrid search using RRF and CrossEncoder rerank."""
        # 1. Fetch top candidates from Vector DB
        vector_results = self.vector_service.search(
            namespace=namespace,
            query=query,
            top_k=20,
            filters=filters,
            version=version
        )
        
        # 2. Fetch top candidates from BM25 (built or dynamically compiled)
        bm25_results = self.bm25_index.search(
            query=query,
            top_k=20,
            filters=filters
        )
        
        # 3. Reciprocal Rank Fusion (RRF)
        rrf_results = self._reciprocal_rank_fusion(vector_results, bm25_results, k=60)
        
        # 4. Rerank top 20 using CrossEncoder
        reranker = CrossEncoderReranker()
        final_results = reranker.rerank(query, rrf_results[:20], top_n=top_k)
        
        return final_results

    def _reciprocal_rank_fusion(
        self, 
        vector_results: List[Dict[str, Any]], 
        bm25_results: List[Dict[str, Any]], 
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """Merges vector and BM25 search results using RRF score formula."""
        rrf_scores = {}
        merged_docs = {}
        
        # Helper to generate unique doc keys
        def doc_key(doc: Dict[str, Any]) -> str:
            return doc["content"]
            
        for rank, doc in enumerate(vector_results):
            key = doc_key(doc)
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (k + rank + 1))
            merged_docs[key] = doc
            merged_docs[key]["vector_rank"] = rank + 1
            
        for rank, doc in enumerate(bm25_results):
            key = doc_key(doc)
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (k + rank + 1))
            if key not in merged_docs:
                merged_docs[key] = doc
            merged_docs[key]["bm25_rank"] = rank + 1
            
        # Compile score lists
        output_docs = []
        for key, score in rrf_scores.items():
            doc = merged_docs[key]
            doc["rrf_score"] = round(score, 6)
            output_docs.append(doc)
            
        output_docs.sort(key=lambda x: x["rrf_score"], reverse=True)
        return output_docs
