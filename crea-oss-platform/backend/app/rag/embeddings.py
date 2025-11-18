"""
Embedding model for document and query vectorization.

Uses open-source sentence-transformers models.
"""
from typing import List
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingModel:
    """
    Wrapper for open-source embedding models.

    Uses sentence-transformers for consistent embeddings.
    """

    def __init__(self, model_name: str = None):
        """
        Initialize the embedding model.

        Args:
            model_name: Name of the model (defaults to config setting)
        """
        self.model_name = model_name or settings.embedding_model_name
        self.model = None
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of the model."""
        if self._initialized:
            return

        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name,
                device=settings.embedding_device,
            )
            self._initialized = True
            logger.info(f"Embedding model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.

        Args:
            texts: List of text documents to embed

        Returns:
            List of embedding vectors
        """
        self._initialize()

        if not texts:
            return []

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=settings.embedding_batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        self._initialize()

        try:
            embedding = self.model.encode(
                text,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Query embedding failed: {e}")
            raise

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        self._initialize()
        return self.model.get_sentence_embedding_dimension()
