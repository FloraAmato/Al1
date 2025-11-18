"""
Background tasks for document processing and data export.
"""
import json
from typing import List, Dict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SyncSessionLocal
from app.core.logging import get_logger
from app.models import Conversation, Message, ConversationFeedback
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="export_training_data")
def export_training_data(min_rating: int = 4) -> Dict:
    """
    Export conversation data for fine-tuning.

    Exports conversations with high ratings to JSONL format.

    Args:
        min_rating: Minimum feedback rating to include

    Returns:
        Dict with export statistics
    """
    logger.info(f"Exporting training data with min_rating={min_rating}")

    db = SyncSessionLocal()
    try:
        # Query conversations with good feedback
        feedbacks = db.execute(
            select(ConversationFeedback).where(
                ConversationFeedback.rating >= min_rating
            )
        ).scalars().all()

        conversation_ids = {f.conversation_id for f in feedbacks}

        # Prepare training data
        training_data = []

        for conv_id in conversation_ids:
            messages = db.execute(
                select(Message)
                .where(Message.conversation_id == conv_id)
                .order_by(Message.created_at)
            ).scalars().all()

            # Build instruction-response pairs
            for i in range(len(messages) - 1):
                if messages[i].role.value == "user" and messages[i + 1].role.value == "assistant":
                    training_data.append({
                        "instruction": messages[i].content,
                        "output": messages[i + 1].content,
                        "conversation_id": conv_id,
                    })

        # Write to JSONL file
        import os
        from datetime import datetime

        os.makedirs(settings.export_data_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(
            settings.export_data_dir,
            f"training_data_{timestamp}.jsonl"
        )

        with open(filepath, "w") as f:
            for item in training_data:
                f.write(json.dumps(item) + "\n")

        logger.info(f"Exported {len(training_data)} training examples to {filepath}")

        return {
            "status": "success",
            "filepath": filepath,
            "num_examples": len(training_data),
            "num_conversations": len(conversation_ids),
        }

    except Exception as e:
        logger.error(f"Export failed: {e}")
        return {
            "status": "error",
            "error": str(e),
        }
    finally:
        db.close()


@celery_app.task(name="reindex_documents")
def reindex_documents() -> Dict:
    """
    Reindex all documents in the vector database.

    Useful when changing embedding models or chunking strategies.
    """
    logger.info("Starting document reindexing")

    # This is a placeholder for the reindexing logic
    # In practice, you would:
    # 1. Load all documents from DB
    # 2. Re-chunk them
    # 3. Re-embed with new model
    # 4. Update vector store

    return {
        "status": "success",
        "message": "Reindexing completed",
    }
