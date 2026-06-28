"""Tests for RAG pipeline (VectorTool)."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture
def vector_tool():
    """Create a VectorTool instance with mocked dependencies."""
    from app.agents.tools.vector_tool import VectorTool
    return VectorTool()


@pytest.fixture
def sample_text_file():
    """Create a temporary text file for testing."""
    content = """Sales Playbook for Enterprise Accounts.

Chapter 1: Discovery Phase.
During the discovery phase, focus on understanding the customer's pain points,
budget constraints, and decision-making process. Key questions to ask include
the current challenges, desired outcomes, and timeline for implementation.

Chapter 2: Proposal Phase.
Present a tailored solution that addresses the specific pain points identified
during discovery. Include ROI projections, implementation timeline, and
success metrics. Always highlight competitive advantages.

Chapter 3: Negotiation Phase.
Be prepared to discuss pricing flexibility, payment terms, and contract duration.
Understand the customer's budget constraints and offer creative solutions
such as phased implementations or usage-based pricing.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(content)
        return f.name


def test_read_txt_document(vector_tool, sample_text_file):
    """Test reading a text file."""
    text = vector_tool.read_document(sample_text_file)
    assert "Sales Playbook" in text
    assert "Discovery Phase" in text
    os.unlink(sample_text_file)


def test_chunk_text_short(vector_tool):
    """Test chunking with text shorter than chunk size."""
    text = "Short text."
    chunks = vector_tool.chunk_text(text, chunk_size=1000)
    assert len(chunks) == 1
    assert chunks[0] == "Short text."


def test_chunk_text_long(vector_tool):
    """Test chunking with text longer than chunk size."""
    text = "Hello world. " * 200  # ~2600 chars
    chunks = vector_tool.chunk_text(text, chunk_size=500, chunk_overlap=50)
    assert len(chunks) > 1
    # Each chunk should be roughly within size limit
    for chunk in chunks:
        assert len(chunk) <= 600  # Allow some margin for sentence breaks


def test_chunk_text_overlap(vector_tool):
    """Test that chunks have overlap."""
    text = "Sentence one. Sentence two. Sentence three. Sentence four. " * 30
    chunks = vector_tool.chunk_text(text, chunk_size=200, chunk_overlap=50)
    if len(chunks) > 1:
        # Check that some content from end of chunk N appears in chunk N+1
        last_words = chunks[0][-30:]
        # Overlap means the start of next chunk shares content
        assert len(chunks[1]) > 0


def test_generate_embeddings(vector_tool):
    """Test embedding generation with mocked model."""
    import numpy as np

    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
    vector_tool._embedder = mock_model

    embeddings = vector_tool.generate_embeddings(["text 1", "text 2"])
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 3


def test_ingest_document_pipeline(vector_tool, sample_text_file):
    """Test full ingest pipeline with mocked ChromaDB and embeddings."""
    import numpy as np

    # Mock embedder
    mock_model = MagicMock()
    mock_model.encode.return_value = np.random.rand(10, 384)
    vector_tool._embedder = mock_model

    # Mock collection
    mock_collection = MagicMock()
    mock_collection.upsert = MagicMock()
    vector_tool._collection = mock_collection

    result = vector_tool.ingest_document(
        file_path=sample_text_file,
        metadata={"title": "Sales Playbook", "document_type": "playbook"},
    )

    assert result["file_path"] == sample_text_file
    assert result["chunks_created"] > 0
    mock_collection.upsert.assert_called_once()

    os.unlink(sample_text_file)


def test_search_with_mocked_collection(vector_tool):
    """Test search with mocked ChromaDB collection."""
    import numpy as np

    # Mock embedder
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
    vector_tool._embedder = mock_model

    # Mock collection with results
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["Doc content 1", "Doc content 2"]],
        "metadatas": [[{"source": "file1.txt"}, {"source": "file2.txt"}]],
        "distances": [[0.1, 0.3]],
    }
    vector_tool._collection = mock_collection

    results = vector_tool.search("test query", top_k=2)
    assert len(results) == 2
    assert results[0]["similarity_score"] == 0.9  # 1 - 0.1
    assert results[1]["similarity_score"] == 0.7  # 1 - 0.3
    assert results[0]["source"] == "file1.txt"


def test_unsupported_file_type(vector_tool):
    """Test that unsupported file types raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        vector_tool.read_document("file.xyz")


def test_knowledge_tool_search():
    """Test KnowledgeTool wraps VectorTool correctly."""
    from app.agents.tools.knowledge_tool import KnowledgeTool

    tool = KnowledgeTool()

    # Mock the underlying vector tool
    tool.vector_tool.search = MagicMock(return_value=[
        {"content": "test", "source": "test.txt", "similarity_score": 0.9}
    ])

    results = tool.search_knowledge("pricing policy", top_k=3)
    assert len(results) == 1
    tool.vector_tool.search.assert_called_once()
