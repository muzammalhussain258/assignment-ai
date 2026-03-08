"""Flask application factory."""

from __future__ import annotations

import time
import uuid

import structlog
from flask import Flask, g, request
from flask_cors import CORS

from app.config import Config, get_config
from app.errors.handlers import register_error_handlers
from app.utils.file_storage import ensure_directories
from app.utils.logger import initialize_logging


def create_app(config: Config | None = None) -> Flask:
    """Create and configure the Flask application (7-step initialisation)."""
    app = Flask(__name__)

    # Step 1: Load config
    cfg = config or get_config()
    app.config.from_object(cfg)
    app.config["_app_config"] = cfg

    # Step 2: Initialize logging
    debug = getattr(cfg, "DEBUG", True)
    log_dir = getattr(cfg, "LOG_DIR", "logs")
    initialize_logging(log_dir=log_dir, debug=debug)
    log = structlog.get_logger(__name__)

    # Step 3: Initialize CORS
    CORS(app)

    # Step 4: Ensure output/log directories
    output_dir = getattr(cfg, "OUTPUT_DIR", "output")
    ensure_directories(output_dir, log_dir)

    # Step 5: Register blueprints
    from app.api.v1 import routes_assignment  # noqa: F401 — registers routes on import
    from app.api.v1.routes import api_v1

    app.register_blueprint(api_v1)

    # Step 6: Register error handlers
    register_error_handlers(app)

    # Step 7: Request lifecycle hooks
    @app.before_request
    def _before() -> None:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        g.request_id = request_id
        g.start_time = time.monotonic()
        structlog.contextvars.bind_contextvars(request_id=request_id)

    @app.after_request
    def _after(response):
        elapsed = time.monotonic() - getattr(g, "start_time", time.monotonic())
        log.info(
            "request_complete",
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=round(elapsed * 1000, 2),
        )
        response.headers["X-Request-ID"] = getattr(g, "request_id", "")
        return response

    @app.teardown_request
    def _teardown(exc=None) -> None:
        structlog.contextvars.clear_contextvars()

    log.info("app_created", env=getattr(cfg, "FLASK_ENV", "development"))
    return app
