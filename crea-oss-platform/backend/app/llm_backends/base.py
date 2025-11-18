"""
Base LLM backend interface.

All LLM backends (HuggingFace, TGI, vLLM, llama.cpp) implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional
from pydantic import BaseModel


class Message(BaseModel):
    """Message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str


class GenerationConfig(BaseModel):
    """Configuration for text generation."""
    max_new_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    stop_sequences: Optional[List[str]] = None


class BaseLLMBackend(ABC):
    """
    Abstract base class for LLM backends.

    All open-source LLM backends must implement these methods.
    """

    def __init__(self, model_id: str, **kwargs):
        """
        Initialize the backend.

        Args:
            model_id: Model identifier (HF model ID, local path, etc.)
            **kwargs: Backend-specific configuration
        """
        self.model_id = model_id
        self.kwargs = kwargs

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """
        Generate a response for the given messages.

        Args:
            messages: List of conversation messages
            config: Generation configuration

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    async def stream_generate(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None,
    ) -> AsyncIterator[str]:
        """
        Stream-generate a response for the given messages.

        Args:
            messages: List of conversation messages
            config: Generation configuration

        Yields:
            Chunks of generated text
        """
        pass

    def format_messages(self, messages: List[Message]) -> str:
        """
        Format messages into a prompt string.

        Default implementation for chat format. Override if needed.
        """
        formatted = ""
        for msg in messages:
            if msg.role == "system":
                formatted += f"<|system|>\n{msg.content}\n"
            elif msg.role == "user":
                formatted += f"<|user|>\n{msg.content}\n"
            elif msg.role == "assistant":
                formatted += f"<|assistant|>\n{msg.content}\n"
        formatted += "<|assistant|>\n"
        return formatted
