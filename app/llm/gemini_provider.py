"""Google Gemini provider."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.llm.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini 2.0 Flash provider."""

    MODEL = "gemini-2.0-flash"

    def get_chat_model(
        self,
        api_key: str,
        temperature: float = 0.7,
        timeout: int = 120,
        max_retries: int = 2,
    ) -> BaseChatModel:
        return ChatGoogleGenerativeAI(
            model=self.MODEL,
            google_api_key=api_key,  # type: ignore[arg-type]
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
        )
