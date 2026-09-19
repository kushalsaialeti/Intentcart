"""
IntentCart - LLM Intelligence Layer
Module: llm/base.py

Objective (Phase L2):
Abstract Base Class for LLM providers. Decouples prompt execution
from specific API vendors (Gemini, Groq, etc.).
"""

from abc import ABC, abstractmethod
from typing import Optional

class LLMProvider(ABC):
    """
    Abstract interface for all LLM providers in IntentCart.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns provider identifier (e.g. 'gemini', 'groq')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the specific model version."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if required API keys are present."""
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> str:
        """Synchronous text generation."""
        pass

    @abstractmethod
    async def generate_text_async(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> str:
        """Asynchronous text generation (for racing and concurrent endpoints)."""
        pass
