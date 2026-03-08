"""LLM provider factory with registry pattern."""

from __future__ import annotations

import os

import structlog

from app.errors import ConfigurationError, LLMProviderError
from app.llm.base import BaseLLMProvider

log = structlog.get_logger(__name__)

# Provider registry: provider name → class (lazy import to avoid heavy deps at import time)
_PROVIDER_MAP: dict[str, str] = {
    "openai": "app.llm.openai_provider.OpenAIProvider",
    "gemini": "app.llm.gemini_provider.GeminiProvider",
    "anthropic": "app.llm.anthropic_provider.AnthropicProvider",
    "groq": "app.llm.groq_provider.GroqProvider",
}

# Env variable names for server-side keys
_ENV_KEY_MAP: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
}


def _import_provider(dotted_path: str) -> type[BaseLLMProvider]:
    module_path, class_name = dotted_path.rsplit(".", 1)
    import importlib

    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class LLMFactory:
    """Factory that resolves API keys and returns configured LangChain chat models."""

    @staticmethod
    def get_chat_model(
        provider: str,
        user_api_key: str | None,
        temperature: float = 0.7,
        timeout: int = 120,
        max_retries: int = 2,
    ):
        """Resolve provider + key and return a LangChain chat model."""
        if provider not in _PROVIDER_MAP:
            raise ConfigurationError(
                f"Unknown LLM provider: '{provider}'",
                detail=f"Supported providers: {list(_PROVIDER_MAP.keys())}",
            )

        # Key priority: user-supplied → env var → error
        api_key: str | None = user_api_key or os.getenv(_ENV_KEY_MAP.get(provider, ""), "")
        if not api_key:
            raise LLMProviderError(
                f"No API key available for provider '{provider}'.",
                detail=(
                    f"Supply 'api_key' in the request body or set "
                    f"{_ENV_KEY_MAP.get(provider)} in the server environment."
                ),
            )

        try:
            provider_class = _import_provider(_PROVIDER_MAP[provider])
            instance = provider_class()
            return instance.get_chat_model(
                api_key=api_key,
                temperature=temperature,
                timeout=timeout,
                max_retries=max_retries,
            )
        except (ConfigurationError, LLMProviderError):
            raise
        except Exception as exc:
            log.error("llm_factory_error", provider=provider, error=str(exc))
            raise LLMProviderError(
                f"Failed to initialise LLM provider '{provider}'.",
                detail=str(exc),
            ) from exc
