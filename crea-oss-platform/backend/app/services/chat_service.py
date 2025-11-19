"""
ChatService for conversational interactions.

Integrates LLM, RAG, caching, and dispute resolution tools.
"""
import hashlib
import json
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import get_logger
from app.models import Conversation, Message, MessageRole
from app.llm_backends import Message as LLMMessage
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.cache_service import CacheService
from app.services.optimizer_service import OptimizerService

logger = get_logger(__name__)


class ChatService:
    """
    Service for chat interactions.

    Orchestrates LLM, RAG, caching, and tool calls.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the service."""
        self.db = db
        self.llm_service = LLMService(db)
        self.rag_service = RAGService(db)
        self.cache_service = CacheService()
        self.optimizer_service = OptimizerService(db)

    async def chat(
        self,
        user_id: int,
        session_id: str,
        message: str,
        model_id: Optional[str] = None,
        use_rag: bool = True,
        dispute_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Process a chat message and generate a response.

        Args:
            user_id: User ID
            session_id: Conversation session ID
            message: User message
            model_id: Optional model to use
            use_rag: Whether to use RAG for context
            dispute_id: Optional dispute context

        Returns:
            Dict with answer and sources
        """
        logger.info(f"Processing chat message for session {session_id}")

        # Get or create conversation
        conversation = await self._get_or_create_conversation(
            user_id, session_id, model_id
        )

        # Load chat history
        history = await self._load_history(conversation.id)

        # Retrieve RAG context if enabled
        sources = []
        rag_context = ""
        context_hash = None

        if use_rag and message:
            results = await self.rag_service.retrieve_context(
                query=message,
                top_k=settings.rag_top_k,
            )
            sources = [
                {
                    "content": r.content,
                    "score": r.score,
                    "metadata": r.metadata,
                }
                for r in results
            ]

            if results:
                rag_context = "\n\n".join(
                    [f"Source {i+1}:\n{r.content}" for i, r in enumerate(results)]
                )
                context_hash = hashlib.md5(rag_context.encode()).hexdigest()

        # Build prompt messages
        system_message = self._build_system_prompt(rag_context, dispute_id)
        prompt_messages = [
            LLMMessage(role="system", content=system_message),
            *[
                LLMMessage(role=h["role"], content=h["content"])
                for h in history[-10:]  # Last 10 messages
            ],
            LLMMessage(role="user", content=message),
        ]

        # Check cache
        model_to_use = model_id or conversation.model_id or settings.default_model_id
        cached_response = await self.cache_service.get_cached_response(
            model_id=model_to_use,
            messages=[m.dict() for m in prompt_messages],
            context_hash=context_hash,
        )

        if cached_response:
            logger.info("Using cached response")
            answer = cached_response
        else:
            # Generate response
            answer = await self.llm_service.generate(
                messages=prompt_messages,
                model_id=model_to_use,
            )

            # Cache response
            await self.cache_service.set_cached_response(
                model_id=model_to_use,
                messages=[m.dict() for m in prompt_messages],
                response=answer,
                context_hash=context_hash,
            )

        # Save messages
        await self._save_message(conversation.id, MessageRole.USER, message)
        await self._save_message(
            conversation.id,
            MessageRole.ASSISTANT,
            answer,
            metadata=json.dumps({"sources": sources}) if sources else None,
        )

        logger.info(f"Chat response generated for session {session_id}")

        return {
            "answer": answer,
            "sources": sources,
            "session_id": session_id,
            "model_used": model_to_use,
        }

    def _build_system_prompt(
        self,
        rag_context: str,
        dispute_id: Optional[int],
    ) -> str:
        """Build the system prompt."""
        prompt = """You are an AI assistant specialized in dispute resolution and fair division of assets.
You help users understand legal concepts, analyze cases, and provide guidance on fair allocation algorithms.

Your expertise includes:
- Max-min fairness allocation
- Nash social welfare allocation
- Legal precedents and laws
- Fair division principles

Always provide clear, helpful, and accurate responses."""

        if rag_context:
            prompt += f"\n\nRelevant context from documents:\n{rag_context}"

        if dispute_id:
            prompt += f"\n\nThe user is currently working on dispute ID: {dispute_id}"

        return prompt

    async def _get_or_create_conversation(
        self,
        user_id: int,
        session_id: str,
        model_id: Optional[str],
    ) -> Conversation:
        """Get or create a conversation."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                model_id=model_id,
            )
            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)

        return conversation

    async def _load_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """Load conversation history."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(settings.chat_history_max_messages)
        )
        messages = result.scalars().all()

        return [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]

    async def _save_message(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
        metadata: Optional[str] = None,
    ):
        """Save a message to the database."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata=metadata,
        )
        self.db.add(message)
        await self.db.commit()
