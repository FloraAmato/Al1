"""
Vector store abstraction for RAG.

Supports Qdrant as the primary vector database.
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """Result from vector search."""
    id: str
    score: float
    content: str
    metadata: Dict[str, Any]


class VectorStore:
    """
    Vector store for document embeddings.

    Uses Qdrant for storage and retrieval.
    """

    def __init__(self, collection_name: str = None):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the collection
        """
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.client = None
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of Qdrant client."""
        if self._initialized:
            return

        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            logger.info(f"Connecting to Qdrant at {settings.qdrant_url}")

            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
            )

            # Create collection if it doesn't exist
            collections = self.client.get_collections().collections
            collection_exists = any(
                c.name == self.collection_name for c in collections
            )

            if not collection_exists:
                from app.rag.embeddings import EmbeddingModel
                embedding_model = EmbeddingModel()
                vector_size = embedding_model.dimension

                logger.info(f"Creating collection {self.collection_name} with dimension {vector_size}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE,
                    ),
                )

            self._initialized = True
            logger.info(f"Vector store initialized: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        contents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Add documents to the vector store.

        Args:
            ids: Document IDs
            embeddings: Embedding vectors
            contents: Document contents
            metadatas: Optional metadata dicts
        """
        self._initialize()

        if not ids or len(ids) != len(embeddings) != len(contents):
            raise ValueError("IDs, embeddings, and contents must have the same length")

        from qdrant_client.models import PointStruct

        if metadatas is None:
            metadatas = [{}] * len(ids)

        points = []
        for i, (doc_id, embedding, content, metadata) in enumerate(
            zip(ids, embeddings, contents, metadatas)
        ):
            payload = {
                "content": content,
                **metadata,
            }
            points.append(
                PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            logger.info(f"Added {len(points)} documents to vector store")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def search(
        self,
        query_embedding: List[float],
        top_k: int = None,
        score_threshold: float = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            filters: Optional metadata filters

        Returns:
            List of search results
        """
        self._initialize()

        top_k = top_k or settings.rag_top_k
        score_threshold = score_threshold or settings.rag_score_threshold

        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            query_filter = None
            if filters:
                # Simple filter construction (can be extended)
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                if conditions:
                    query_filter = Filter(must=conditions)

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=query_filter,
            )

            search_results = []
            for result in results:
                search_results.append(
                    SearchResult(
                        id=str(result.id),
                        score=result.score,
                        content=result.payload.get("content", ""),
                        metadata={
                            k: v for k, v in result.payload.items() if k != "content"
                        },
                    )
                )

            logger.info(f"Found {len(search_results)} results for query")
            return search_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def delete_documents(self, ids: List[str]):
        """Delete documents by IDs."""
        self._initialize()

        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids,
            )
            logger.info(f"Deleted {len(ids)} documents from vector store")
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise
