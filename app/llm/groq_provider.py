"""Groq LPU provider."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq

from app.llm.base import BaseLLMProvider


class GroqProvider(BaseLLMProvider):
    """Groq LPU — llama-3.3-70b-versatile provider."""

    MODEL = "llama-3.3-70b-versatile"

    def get_chat_model(
        self,
        api_key: str,
        temperature: float = 0.7,
        timeout: int = 120,
        max_retries: int = 2,
    ) -> BaseChatModel:
        return ChatGroq(
            model=self.MODEL,
            groq_api_key=api_key,  # type: ignore[arg-type]
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
        )
