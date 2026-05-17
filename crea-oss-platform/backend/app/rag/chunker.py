"""
Document chunking utilities for RAG.

Splits documents into overlapping chunks for embedding.
"""
from typing import List
import re

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentChunker:
    """
    Chunker for splitting documents into smaller pieces.

    Uses simple sliding window with overlap.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        """
        Initialize the chunker.

        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
        """
        self.chunk_size = chunk_size or settings.rag_chunk_size
        self.chunk_overlap = chunk_overlap or settings.rag_chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        # Simple word-based splitting (for production, use proper tokenization)
        words = text.split()

        if len(words) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunks.append(" ".join(chunk_words))

            # Move start forward, accounting for overlap
            start = end - self.chunk_overlap
            if start >= len(words):
                break

        return chunks

    def chunk_by_sentences(self, text: str, max_sentences: int = 10) -> List[str]:
        """
        Split text by sentences, grouping into chunks.

        Args:
            text: Text to chunk
            max_sentences: Maximum sentences per chunk

        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)

        if len(sentences) <= max_sentences:
            return [text]

        chunks = []
        for i in range(0, len(sentences), max_sentences):
            chunk_sentences = sentences[i:i + max_sentences]
            chunks.append(" ".join(chunk_sentences))

        return chunks
