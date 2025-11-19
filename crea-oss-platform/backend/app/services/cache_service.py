"""
Semantic caching service for LLM responses.

Caches responses based on prompt hash to reduce compute costs.
"""
import hashlib
import json
from typing import Any, Dict, Optional
import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """
    Service for caching LLM responses.

    Uses Redis for distributed caching with TTL.
    """

    def __init__(self):
        """Initialize the cache service."""
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.cache_enabled
        self.ttl = settings.cache_ttl
        self._initialized = False

    async def _initialize(self):
        """Lazy initialization of Redis client."""
        if self._initialized or not self.enabled:
            return

        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
            # Test connection
            await self.redis_client.ping()
            self._initialized = True
            logger.info("Cache service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize cache service: {e}")
            self.enabled = False

    def _generate_cache_key(
        self,
        model_id: str,
        messages: list,
        context_hash: Optional[str] = None,
    ) -> str:
        """
        Generate a cache key from inputs.

        Args:
            model_id: Model identifier
            messages: List of messages
            context_hash: Optional hash of RAG context

        Returns:
            Cache key string
        """
        # Normalize messages to JSON string
        messages_str = json.dumps(messages, sort_keys=True)

        # Create hash
        content = f"{model_id}:{messages_str}"
        if context_hash:
            content += f":{context_hash}"

        key_hash = hashlib.sha256(content.encode()).hexdigest()
        return f"llm_cache:{key_hash}"

    async def get_cached_response(
        self,
        model_id: str,
        messages: list,
        context_hash: Optional[str] = None,
    ) -> Optional[str]:
        """
        Retrieve a cached response.

        Args:
            model_id: Model identifier
            messages: List of messages
            context_hash: Optional hash of RAG context

        Returns:
            Cached response or None
        """
        if not self.enabled:
            return None

        await self._initialize()

        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(model_id, messages, context_hash)
            cached = await self.redis_client.get(cache_key)

            if cached:
                logger.info(f"Cache hit for key: {cache_key[:16]}...")
                return cached
            else:
                logger.debug(f"Cache miss for key: {cache_key[:16]}...")
                return None

        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    async def set_cached_response(
        self,
        model_id: str,
        messages: list,
        response: str,
        context_hash: Optional[str] = None,
        ttl: Optional[int] = None,
    ):
        """
        Store a response in cache.

        Args:
            model_id: Model identifier
            messages: List of messages
            response: Response to cache
            context_hash: Optional hash of RAG context
            ttl: Time-to-live in seconds (defaults to config setting)
        """
        if not self.enabled:
            return

        await self._initialize()

        if not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key(model_id, messages, context_hash)
            ttl = ttl or self.ttl

            await self.redis_client.setex(cache_key, ttl, response)
            logger.info(f"Cached response for key: {cache_key[:16]}...")

        except Exception as e:
            logger.error(f"Cache storage error: {e}")

    async def invalidate_cache(self, pattern: str = "llm_cache:*"):
        """
        Invalidate cache entries matching a pattern.

        Args:
            pattern: Redis key pattern
        """
        if not self.enabled:
            return

        await self._initialize()

        if not self.redis_client:
            return

        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries")

        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")

    async def close(self):
        """Close the Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
