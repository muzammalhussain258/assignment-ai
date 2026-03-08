"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel


class BaseLLMProvider(ABC):
    """All LLM providers must implement this interface."""

    @abstractmethod
    def get_chat_model(self, api_key: str, temperature: float, timeout: int, max_retries: int) -> BaseChatModel:
        """Return a configured LangChain chat model."""
        ...
