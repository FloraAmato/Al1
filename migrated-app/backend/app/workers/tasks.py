"""
Celery worker tasks for async operations.
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "crea_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="solve_dispute_async")
def solve_dispute_async(dispute_id: str) -> dict:
    """
    Solve dispute asynchronously for large problems.

    Args:
        dispute_id: UUID of dispute to solve

    Returns:
        Solution dictionary
    """
    # Import here to avoid circular imports
    from app.services.optimizer import OptimizationService
    from app.db.session import AsyncSessionLocal
    import asyncio

    async def _solve():
        async with AsyncSessionLocal() as db:
            optimizer = OptimizationService(db)
            solution = await optimizer.solve_dispute(dispute_id)
            return solution.model_dump()

    return asyncio.run(_solve())


@celery_app.task(name="send_email_async")
def send_email_async(to_email: str, subject: str, template_name: str, context: dict) -> bool:
    """
    Send email asynchronously.

    Args:
        to_email: Recipient email
        subject: Email subject
        template_name: Template name
        context: Template context

    Returns:
        True if sent successfully
    """
    from app.services.email_service import EmailService
    import asyncio

    async def _send():
        email_service = EmailService()
        return await email_service.send_email(to_email, subject, template_name, context)

    return asyncio.run(_send())
