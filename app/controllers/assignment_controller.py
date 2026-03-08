"""Assignment controller — HTTP boundary layer."""

from __future__ import annotations

import re
import uuid

import structlog
from flask import Request, jsonify, send_file
from pydantic import ValidationError as PydanticValidationError

from app.config import get_config
from app.errors import NotFoundError, ValidationError
from app.schemas import AssignmentRequest
from app.services.assignment_service import generate_assignment
from app.utils.file_manager import get_file_for_download

log = structlog.get_logger(__name__)

_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _validate_uuid(assignment_id: str) -> None:
    """Raise ValidationError if assignment_id is not a valid v4 UUID."""
    if not _UUID_PATTERN.match(assignment_id):
        raise ValidationError(
            "Invalid assignment ID format.",
            detail="assignment_id must be a valid UUID v4.",
        )


def handle_generate_assignment(request: Request):
    """Parse, validate, and dispatch to the assignment service."""
    # Enforce Content-Type
    if not request.is_json:
        raise ValidationError(
            "Content-Type must be application/json.",
            error_code="UNSUPPORTED_MEDIA_TYPE",
        )

    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    log.info("generate_assignment_request", request_id=request_id)

    data = request.get_json(silent=True) or {}

    try:
        assignment_request = AssignmentRequest(**data)
    except PydanticValidationError as exc:
        errors = []
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            errors.append({"field": field, "message": err["msg"]})
        raise ValidationError(
            "Request validation failed.",
            detail=errors,
        )

    response = generate_assignment(assignment_request)
    result = jsonify(response.model_dump())
    result.status_code = 201
    log.info("generate_assignment_response", assignment_id=response.assignment_id, request_id=request_id)
    return result


def handle_download_docx(assignment_id: str):
    """Stream the DOCX file for the given assignment_id."""
    _validate_uuid(assignment_id)
    cfg = get_config()
    path = get_file_for_download(cfg.OUTPUT_DIR, assignment_id, "docx")
    if not path:
        raise NotFoundError(f"DOCX file not found for assignment '{assignment_id}'.")
    return send_file(path, as_attachment=True, download_name=f"{assignment_id}.docx")


def handle_download_pdf(assignment_id: str):
    """Stream the PDF file for the given assignment_id."""
    _validate_uuid(assignment_id)
    cfg = get_config()
    path = get_file_for_download(cfg.OUTPUT_DIR, assignment_id, "pdf")
    if not path:
        raise NotFoundError(f"PDF file not found for assignment '{assignment_id}'.")
    return send_file(path, as_attachment=True, download_name=f"{assignment_id}.pdf")
