import os
import pytest
import tempfile
from pathlib import Path

from app.rag.document_processor import DocumentProcessor
from app.rag.chunker import (
    FixedSizeChunker, RecursiveCharacterChunker, 
    SlidingWindowChunker, HeadingAwareChunker, SemanticChunker
)
from app.rag.embeddings import EmbeddingFactory
from app.rag.vector_service import VectorService
try:
    from app.rag.hybrid_search import HybridSearcher, BM25Index, ReciprocalRankFusion
except ImportError:
    HybridSearcher = BM25Index = ReciprocalRankFusion = None

@pytest.fixture
def sample_md_file():
    content = """# Title of Doc
This is an introductory paragraph.

## Section 1: Pricing
Pricing is $100 per user per month. This is standard pricing.

## Section 2: Policies
Refunds are allowed within 30 days of purchase.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(content)
        return f.name

def test_document_processor_md(sample_md_file):
    parsed = DocumentProcessor.parse(sample_md_file)
    assert parsed["metadata"]["title"] == "Title of Doc"
    assert "Pricing" in parsed["content"]
    assert len(parsed["metadata"]["headings"]) >= 2
    os.unlink(sample_md_file)

def test_chunkers():
    text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
    
    # FixedSizeChunker
    fixed = FixedSizeChunker(chunk_size=3, chunk_overlap=1)
    chunks = fixed.split(text)
    assert len(chunks) > 1
    
    # RecursiveCharacterChunker
    rec = RecursiveCharacterChunker(chunk_size=30, chunk_overlap=5)
    chunks_rec = rec.split(text)
    assert len(chunks_rec) > 1
    
    # SlidingWindowChunker
    sliding = SlidingWindowChunker(chunk_size=4, chunk_overlap=2)
    chunks_slide = sliding.split(text)
    assert len(chunks_slide) > 1

@pytest.mark.skipif(BM25Index is None, reason="hybrid_search module not available")
def test_bm25_search():
    index = BM25Index()
    docs = [
        {"content": "Standard pricing is $100.", "metadata": {"doc_id": "1", "type": "policy"}},
        {"content": "Sales rep guidelines and discovery questions.", "metadata": {"doc_id": "2", "type": "sales"}},
        {"content": "VP approval is required for discounts.", "metadata": {"doc_id": "3", "type": "policy"}}
    ]
    index.index_documents(docs)
    
    # Search term "pricing"
    results = index.search("pricing", top_k=2)
    assert len(results) > 0
    assert "Standard pricing" in results[0]["content"]
    
    # Search with filter
    filtered_results = index.search("discount", top_k=2, filters={"type": "policy"})
    assert len(filtered_results) > 0
    assert "VP approval" in filtered_results[0]["content"]

@pytest.mark.skipif(HybridSearcher is None, reason="hybrid_search module not available")
def test_hybrid_rrf():
    # Setup test vectors
    vector_results = [
        {"content": "Pricing guidelines.", "metadata": {"doc_id": "1"}, "similarity_score": 0.9},
        {"content": "VP discounts.", "metadata": {"doc_id": "2"}, "similarity_score": 0.8}
    ]
    bm25_results = [
        {"content": "VP discounts.", "metadata": {"doc_id": "2"}, "bm25_score": 4.5},
        {"content": "Sales team onboarding.", "metadata": {"doc_id": "3"}, "bm25_score": 2.1}
    ]
    
    # Instantiate searcher with mocked vector service
    from unittest.mock import MagicMock
    vec_service = MagicMock()
    searcher = HybridSearcher(vec_service)
    
    rrf_results = searcher._reciprocal_rank_fusion(vector_results, bm25_results)
    # VP discounts should rank highly because it's in both
    assert rrf_results[0]["content"] == "VP discounts."
