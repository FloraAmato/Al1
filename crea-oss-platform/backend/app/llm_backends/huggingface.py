"""
HuggingFace local backend for running models directly.

Supports loading models from HuggingFace Hub or local paths.
"""
import asyncio
from typing import AsyncIterator, List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.llm_backends.base import BaseLLMBackend, GenerationConfig, Message

logger = get_logger(__name__)


class HuggingFaceLocalBackend(BaseLLMBackend):
    """
    Backend for running HuggingFace models locally.

    Uses transformers library with optional quantization.
    """

    def __init__(self, model_id: str, **kwargs):
        super().__init__(model_id, **kwargs)
        self.device = kwargs.get("device", settings.hf_device)
        self.load_in_8bit = kwargs.get("load_in_8bit", settings.hf_load_in_8bit)
        self.load_in_4bit = kwargs.get("load_in_4bit", settings.hf_load_in_4bit)

        self.model = None
        self.tokenizer = None
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of model and tokenizer."""
        if self._initialized:
            return

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            logger.info(f"Loading model {self.model_id} on device {self.device}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                trust_remote_code=True,
            )

            # Configure quantization
            model_kwargs = {"trust_remote_code": True}
            if self.load_in_8bit:
                model_kwargs["load_in_8bit"] = True
            elif self.load_in_4bit:
                model_kwargs["load_in_4bit"] = True
            else:
                model_kwargs["device_map"] = self.device

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id, **model_kwargs
            )

            self._initialized = True
            logger.info(f"Model {self.model_id} loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model {self.model_id}: {e}")
            raise

    async def generate(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """Generate a response using the local HuggingFace model."""
        self._initialize()

        if config is None:
            config = GenerationConfig()

        # Format messages into prompt
        prompt = self.format_messages(messages)

        # Run generation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._generate_sync, prompt, config
        )
        return result

    def _generate_sync(self, prompt: str, config: GenerationConfig) -> str:
        """Synchronous generation (runs in thread pool)."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=config.max_new_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            repetition_penalty=config.repetition_penalty,
            do_sample=True,
        )

        # Decode only the generated part
        generated_text = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True,
        )
        return generated_text.strip()

    async def stream_generate(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None,
    ) -> AsyncIterator[str]:
        """Stream generation (simplified implementation)."""
        # For simplicity, we just yield the full response
        # A full implementation would use TextIteratorStreamer
        result = await self.generate(messages, config)
        yield result
