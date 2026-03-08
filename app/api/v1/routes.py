"""API v1 blueprint definition and health check."""

from __future__ import annotations

from flask import Blueprint, jsonify

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@api_v1.get("/health")
def health_check():
    return jsonify({"status": "healthy", "version": "1.0.0"})
