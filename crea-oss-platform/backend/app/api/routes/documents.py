"""Document management API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.schemas.document import DocumentCreate, DocumentRead
from app.services import RAGService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentRead)
async def create_document(
    document_data: DocumentCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create and ingest a document.

    The document will be chunked, embedded, and indexed for RAG.
    """
    try:
        service = RAGService(db)
        document = await service.ingest_document(
            title=document_data.title,
            content=document_data.content,
            content_type=document_data.content_type,
            category=document_data.category,
            source=document_data.source,
        )

        return document

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(None),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Upload a document file.

    Supports text files and PDFs (basic implementation).
    """
    try:
        # Read file content
        content_bytes = await file.read()

        # Decode text (simple handling)
        if file.content_type == "text/plain" or file.filename.endswith(".txt"):
            content = content_bytes.decode("utf-8")
        else:
            # For other types, would need proper parsing (pdf, docx, etc.)
            raise HTTPException(
                status_code=400,
                detail="Only text files supported in this demo"
            )

        service = RAGService(db)
        document = await service.ingest_document(
            title=title,
            content=content,
            content_type=file.content_type or "text/plain",
            category=category,
            source=file.filename,
        )

        return document

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Delete a document and its embeddings."""
    try:
        service = RAGService(db)
        await service.delete_document(document_id)
        return {"status": "deleted", "document_id": document_id}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
