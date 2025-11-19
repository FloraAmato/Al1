"""
vLLM backend for high-throughput inference.

Connects to a remote vLLM server.
"""
from typing import AsyncIterator, List, Optional
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.llm_backends.base import BaseLLMBackend, GenerationConfig, Message

logger = get_logger(__name__)


class VLLMBackend(BaseLLMBackend):
    """
    Backend for vLLM server.

    Connects to a remote vLLM instance via OpenAI-compatible API.
    """

    def __init__(self, model_id: str, **kwargs):
        super().__init__(model_id, **kwargs)
        self.endpoint_url = kwargs.get("endpoint_url", settings.vllm_url)
        if not self.endpoint_url:
            raise ValueError("vLLM endpoint URL must be provided")

        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """Generate a response using vLLM."""
        if config is None:
            config = GenerationConfig()

        # vLLM supports OpenAI-compatible chat completions
        payload = {
            "model": self.model_id,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": config.max_new_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }

        if config.stop_sequences:
            payload["stop"] = config.stop_sequences

        try:
            response = await self.client.post(
                f"{self.endpoint_url}/v1/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"vLLM generation failed: {e}")
            raise

    async def stream_generate(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None,
    ) -> AsyncIterator[str]:
        """Stream generation using vLLM."""
        if config is None:
            config = GenerationConfig()

        payload = {
            "model": self.model_id,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": config.max_new_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "stream": True,
        }

        if config.stop_sequences:
            payload["stop"] = config.stop_sequences

        try:
            async with self.client.stream(
                "POST",
                f"{self.endpoint_url}/v1/chat/completions",
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        if line.strip() == "data: [DONE]":
                            break
                        import json
                        data = json.loads(line[5:])
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
        except Exception as e:
            logger.error(f"vLLM streaming failed: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
