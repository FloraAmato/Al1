"""
RAGService for document ingestion and retrieval.
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.logging import get_logger
from app.models import Document, DocumentChunk
from app.rag import EmbeddingModel, DocumentChunker, VectorStore, SearchResult

logger = get_logger(__name__)


class RAGService:
    """
    Service for Retrieval-Augmented Generation.

    Handles document ingestion, chunking, embedding, and retrieval.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the service."""
        self.db = db
        self.embedding_model = EmbeddingModel()
        self.chunker = DocumentChunker()
        self.vector_store = VectorStore()

    async def ingest_document(
        self,
        title: str,
        content: str,
        content_type: str = "text/plain",
        category: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Ingest a document: chunk, embed, and store.

        Args:
            title: Document title
            content: Document text content
            content_type: MIME type
            category: Optional category (e.g., "laws", "cases")
            source: Optional source URL or file path
            metadata: Optional metadata dict

        Returns:
            Created Document object
        """
        logger.info(f"Ingesting document: {title}")

        # Create document record
        document = Document(
            title=title,
            source=source,
            content_type=content_type,
            category=category,
            metadata=str(metadata) if metadata else None,
        )
        self.db.add(document)
        await self.db.flush()

        # Chunk the document
        chunks = self.chunker.chunk_text(content)
        logger.info(f"Created {len(chunks)} chunks for document {document.id}")

        # Embed chunks
        embeddings = self.embedding_model.embed_documents(chunks)

        # Store in vector database
        chunk_ids = [f"doc_{document.id}_chunk_{i}" for i in range(len(chunks))]
        chunk_metadatas = [
            {
                "document_id": document.id,
                "title": title,
                "category": category or "",
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        self.vector_store.add_documents(
            ids=chunk_ids,
            embeddings=embeddings,
            contents=chunks,
            metadatas=chunk_metadatas,
        )

        # Store chunk records
        for i, (chunk_text, chunk_id) in enumerate(zip(chunks, chunk_ids)):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
                vector_id=chunk_id,
            )
            self.db.add(chunk)

        await self.db.commit()
        await self.db.refresh(document)

        logger.info(f"Document {document.id} ingested successfully")
        return document

    async def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Retrieve relevant context for a query.

        Args:
            query: User query
            top_k: Number of results to return
            category: Optional category filter

        Returns:
            List of search results
        """
        logger.info(f"Retrieving context for query: {query[:50]}...")

        # Embed query
        query_embedding = self.embedding_model.embed_query(query)

        # Search vector store
        filters = {"category": category} if category else None
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )

        logger.info(f"Retrieved {len(results)} results")
        return results

    async def delete_document(self, document_id: int):
        """Delete a document and its chunks."""
        logger.info(f"Deleting document {document_id}")

        # Load document
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Get chunk vector IDs
        chunks_result = await self.db.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        chunks = chunks_result.scalars().all()
        vector_ids = [c.vector_id for c in chunks if c.vector_id]

        # Delete from vector store
        if vector_ids:
            self.vector_store.delete_documents(vector_ids)

        # Delete from database (cascade will delete chunks)
        await self.db.delete(document)
        await self.db.commit()

        logger.info(f"Document {document_id} deleted")
