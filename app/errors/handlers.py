"""Global Flask error handlers — 5-layer safety net."""

from __future__ import annotations

import traceback

import structlog
from flask import Flask, Response, jsonify
from pydantic import ValidationError as PydanticValidationError
from werkzeug.exceptions import HTTPException

from app.errors import (
    AppError,
    ConfigurationError,
    FileGenerationError,
    LLMProviderError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

log = structlog.get_logger(__name__)

_HTTP_MESSAGES: dict[int, tuple[str, str]] = {
    400: ("Bad request", "BAD_REQUEST"),
    404: ("Resource not found", "NOT_FOUND"),
    405: ("Method not allowed", "METHOD_NOT_ALLOWED"),
    413: ("Payload too large", "PAYLOAD_TOO_LARGE"),
    415: ("Unsupported media type", "UNSUPPORTED_MEDIA_TYPE"),
    429: ("Too many requests", "RATE_LIMIT_EXCEEDED"),
}


def _safe_error_response(
    message: str,
    error_code: str,
    detail: str | None,
    status_code: int,
) -> Response:
    """Layer 5: if any error handler itself fails, return a minimal valid JSON response."""
    import json

    body = json.dumps(
        {
            "error": message,
            "error_code": error_code,
            "detail": detail,
            "status_code": status_code,
        }
    )
    return Response(body, status=status_code, mimetype="application/json")


def register_error_handlers(app: Flask) -> None:
    """Register all global error handlers on the Flask app."""

    # Layer 1: AppError subclasses
    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError) -> tuple[Response, int]:
        try:
            log.warning(
                "app_error",
                error=exc.message,
                error_code=exc.error_code,
                status_code=exc.status_code,
                detail=exc.detail,
            )
            response = jsonify(
                {
                    "error": exc.message,
                    "error_code": exc.error_code,
                    "detail": exc.detail,
                    "status_code": exc.status_code,
                }
            )
            response.status_code = exc.status_code
            return response, exc.status_code
        except Exception:
            return _safe_error_response(exc.message, exc.error_code, exc.detail, exc.status_code), exc.status_code  # type: ignore[return-value]

    # Register individual subclasses so Flask matches them
    for exc_class in (
        ValidationError,
        LLMProviderError,
        FileGenerationError,
        NotFoundError,
        RateLimitError,
        ConfigurationError,
    ):
        app.register_error_handler(exc_class, handle_app_error)

    # Layer 2: Pydantic ValidationError
    @app.errorhandler(PydanticValidationError)
    def handle_pydantic_error(exc: PydanticValidationError) -> tuple[Response, int]:
        try:
            errors = []
            for err in exc.errors():
                field = ".".join(str(loc) for loc in err["loc"])
                errors.append({"field": field, "message": err["msg"]})
            log.warning("pydantic_validation_error", errors=errors)
            response = jsonify(
                {
                    "error": "Request validation failed",
                    "error_code": "VALIDATION_ERROR",
                    "detail": errors,
                    "status_code": 422,
                }
            )
            response.status_code = 422
            return response, 422
        except Exception:
            return _safe_error_response("Validation error", "VALIDATION_ERROR", None, 422), 422  # type: ignore[return-value]

    # Layer 3: Werkzeug HTTP errors
    @app.errorhandler(HTTPException)
    def handle_http_error(exc: HTTPException) -> tuple[Response, int]:
        try:
            status_code = exc.code or 500
            message, error_code = _HTTP_MESSAGES.get(
                status_code, (exc.description or "HTTP error", "HTTP_ERROR")
            )
            log.info("http_error", status_code=status_code, error_code=error_code)
            response = jsonify(
                {
                    "error": message,
                    "error_code": error_code,
                    "detail": exc.description,
                    "status_code": status_code,
                }
            )
            response.status_code = status_code
            return response, status_code
        except Exception:
            code = exc.code or 500
            return _safe_error_response("HTTP error", "HTTP_ERROR", None, code), code  # type: ignore[return-value]

    # Layer 4: Catch-all
    @app.errorhandler(Exception)
    def handle_unexpected_error(exc: Exception) -> tuple[Response, int]:
        try:
            tb = traceback.format_exc()
            log.error(
                "unexpected_error",
                error=str(exc),
                exc_type=type(exc).__name__,
                traceback=tb,
            )
            response = jsonify(
                {
                    "error": "An unexpected error occurred",
                    "error_code": "INTERNAL_ERROR",
                    "detail": None,
                    "status_code": 500,
                }
            )
            response.status_code = 500
            return response, 500
        except Exception:
            return _safe_error_response("Internal server error", "INTERNAL_ERROR", None, 500), 500  # type: ignore[return-value]
