"""
LLMService for managing LLM backends and generation.
"""
from typing import AsyncIterator, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import get_logger
from app.models import ModelConfig, ModelBackendType
from app.llm_backends import (
    BaseLLMBackend,
    GenerationConfig,
    Message,
    HuggingFaceLocalBackend,
    TGIBackend,
    VLLMBackend,
)

logger = get_logger(__name__)


class LLMService:
    """
    Service for LLM generation.

    Manages model backends and provides a unified interface.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the service."""
        self.db = db
        self._backend_cache: dict[str, BaseLLMBackend] = {}

    async def get_backend(
        self,
        model_id: Optional[str] = None,
    ) -> BaseLLMBackend:
        """
        Get or create an LLM backend.

        Args:
            model_id: Model identifier (uses default if None)

        Returns:
            LLM backend instance
        """
        # If no model_id, use default from config
        if not model_id:
            model_id = settings.default_model_id
            backend_type = settings.default_llm_backend
            endpoint_url = None
        else:
            # Try to load from database
            result = await self.db.execute(
                select(ModelConfig).where(ModelConfig.model_id == model_id)
            )
            model_config = result.scalar_one_or_none()

            if model_config:
                backend_type = model_config.backend_type
                endpoint_url = model_config.endpoint_url
            else:
                # Fallback to default backend
                backend_type = settings.default_llm_backend
                endpoint_url = None

        # Check cache
        cache_key = f"{backend_type}:{model_id}"
        if cache_key in self._backend_cache:
            return self._backend_cache[cache_key]

        # Create backend
        logger.info(f"Creating LLM backend: {backend_type} for model {model_id}")

        if backend_type == ModelBackendType.HF_LOCAL:
            backend = HuggingFaceLocalBackend(model_id)
        elif backend_type == ModelBackendType.TGI:
            backend = TGIBackend(model_id, endpoint_url=endpoint_url)
        elif backend_type == ModelBackendType.VLLM:
            backend = VLLMBackend(model_id, endpoint_url=endpoint_url)
        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")

        # Cache backend
        self._backend_cache[cache_key] = backend

        return backend

    async def generate(
        self,
        messages: List[Message],
        model_id: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """
        Generate a response.

        Args:
            messages: List of conversation messages
            model_id: Optional model identifier
            config: Optional generation configuration

        Returns:
            Generated response text
        """
        backend = await self.get_backend(model_id)

        if config is None:
            config = GenerationConfig(
                max_new_tokens=settings.llm_max_new_tokens,
                temperature=settings.llm_temperature,
                top_p=settings.llm_top_p,
                top_k=settings.llm_top_k,
            )

        response = await backend.generate(messages, config)
        return response

    async def stream_generate(
        self,
        messages: List[Message],
        model_id: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ) -> AsyncIterator[str]:
        """
        Stream-generate a response.

        Args:
            messages: List of conversation messages
            model_id: Optional model identifier
            config: Optional generation configuration

        Yields:
            Chunks of generated text
        """
        backend = await self.get_backend(model_id)

        if config is None:
            config = GenerationConfig(
                max_new_tokens=settings.llm_max_new_tokens,
                temperature=settings.llm_temperature,
                top_p=settings.llm_top_p,
                top_k=settings.llm_top_k,
            )

        async for chunk in backend.stream_generate(messages, config):
            yield chunk
