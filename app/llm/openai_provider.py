"""OpenAI GPT provider."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.llm.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4o-mini provider."""

    MODEL = "gpt-4o-mini"

    def get_chat_model(
        self,
        api_key: str,
        temperature: float = 0.7,
        timeout: int = 120,
        max_retries: int = 2,
    ) -> BaseChatModel:
        return ChatOpenAI(
            model=self.MODEL,
            api_key=api_key,  # type: ignore[arg-type]
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
        )
