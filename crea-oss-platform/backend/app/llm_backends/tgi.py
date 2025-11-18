"""
Text Generation Inference (TGI) backend.

Connects to a remote TGI server for inference.
"""
import asyncio
from typing import AsyncIterator, List, Optional
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.llm_backends.base import BaseLLMBackend, GenerationConfig, Message

logger = get_logger(__name__)


class TGIBackend(BaseLLMBackend):
    """
    Backend for Text Generation Inference (TGI) server.

    Connects to a remote TGI instance via HTTP.
    """

    def __init__(self, model_id: str, **kwargs):
        super().__init__(model_id, **kwargs)
        self.endpoint_url = kwargs.get("endpoint_url", settings.tgi_url)
        if not self.endpoint_url:
            raise ValueError("TGI endpoint URL must be provided")

        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """Generate a response using TGI."""
        if config is None:
            config = GenerationConfig()

        prompt = self.format_messages(messages)

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": config.max_new_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "top_k": config.top_k,
                "repetition_penalty": config.repetition_penalty,
                "do_sample": True,
            },
        }

        if config.stop_sequences:
            payload["parameters"]["stop"] = config.stop_sequences

        try:
            response = await self.client.post(
                f"{self.endpoint_url}/generate",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            return result["generated_text"].strip()
        except Exception as e:
            logger.error(f"TGI generation failed: {e}")
            raise

    async def stream_generate(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None,
    ) -> AsyncIterator[str]:
        """Stream generation using TGI."""
        if config is None:
            config = GenerationConfig()

        prompt = self.format_messages(messages)

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": config.max_new_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "top_k": config.top_k,
                "repetition_penalty": config.repetition_penalty,
                "do_sample": True,
            },
            "stream": True,
        }

        if config.stop_sequences:
            payload["parameters"]["stop"] = config.stop_sequences

        try:
            async with self.client.stream(
                "POST",
                f"{self.endpoint_url}/generate_stream",
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        import json
                        data = json.loads(line[5:])
                        if "token" in data:
                            yield data["token"]["text"]
        except Exception as e:
            logger.error(f"TGI streaming failed: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
