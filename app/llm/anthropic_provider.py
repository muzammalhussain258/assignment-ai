"""Anthropic Claude provider."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel

from app.llm.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Opus 4.6 provider."""

    MODEL = "claude-opus-4-6"

    def get_chat_model(
        self,
        api_key: str,
        temperature: float = 0.7,
        timeout: int = 120,
        max_retries: int = 2,
    ) -> BaseChatModel:
        return ChatAnthropic(
            model=self.MODEL,
            api_key=api_key,  # type: ignore[arg-type]
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
        )
