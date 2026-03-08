"""Custom exception hierarchy for the AI Assignment Generator."""

from __future__ import annotations


class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        detail: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if error_code is not None:
            self.error_code = error_code
        if status_code is not None:
            self.status_code = status_code
        self.detail = detail


class ValidationError(AppError):
    """Input validation error (422)."""

    status_code = 422
    error_code = "VALIDATION_ERROR"


class LLMProviderError(AppError):
    """LLM provider / upstream error (502)."""

    status_code = 502
    error_code = "LLM_PROVIDER_ERROR"


class FileGenerationError(AppError):
    """File generation error (500)."""

    status_code = 500
    error_code = "FILE_GENERATION_ERROR"


class NotFoundError(AppError):
    """Resource not found (404)."""

    status_code = 404
    error_code = "NOT_FOUND"


class RateLimitError(AppError):
    """Rate limit exceeded (429)."""

    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"


class ConfigurationError(AppError):
    """Server configuration error (500)."""

    status_code = 500
    error_code = "CONFIGURATION_ERROR"
