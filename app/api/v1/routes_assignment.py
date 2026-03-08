"""Assignment endpoints — POST generate, GET download."""

from __future__ import annotations

from flask import request

from app.api.v1.routes import api_v1
from app.controllers.assignment_controller import (
    handle_download_docx,
    handle_download_pdf,
    handle_generate_assignment,
)


@api_v1.post("/generate-assignment")
def generate_assignment():
    return handle_generate_assignment(request)


@api_v1.get("/download/docx/<string:assignment_id>")
def download_docx(assignment_id: str):
    return handle_download_docx(assignment_id)


@api_v1.get("/download/pdf/<string:assignment_id>")
def download_pdf(assignment_id: str):
    return handle_download_pdf(assignment_id)
