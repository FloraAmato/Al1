"""
Test RAG components.
"""
import pytest
from app.rag import DocumentChunker, EmbeddingModel


def test_document_chunker():
    """Test document chunking."""
    chunker = DocumentChunker(chunk_size=10, chunk_overlap=2)

    text = " ".join([f"word{i}" for i in range(30)])
    chunks = chunker.chunk_text(text)

    assert len(chunks) > 1
    # Check overlap
    for i in range(len(chunks) - 1):
        # Should have some words in common
        words_i = chunks[i].split()
        words_next = chunks[i + 1].split()
        # At least one word should overlap
        assert len(set(words_i) & set(words_next)) > 0


def test_embedding_model():
    """Test embedding model."""
    model = EmbeddingModel(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Test document embedding
    texts = ["This is a test document.", "Another test document."]
    embeddings = model.embed_documents(texts)

    assert len(embeddings) == 2
    assert all(isinstance(emb, list) for emb in embeddings)
    assert all(len(emb) == model.dimension for emb in embeddings)

    # Test query embedding
    query = "test query"
    query_emb = model.embed_query(query)

    assert isinstance(query_emb, list)
    assert len(query_emb) == model.dimension
