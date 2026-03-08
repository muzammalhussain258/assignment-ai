"""File lifecycle management: unique filenames, atomic writes, downloads, cleanup."""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path

import structlog

log = structlog.get_logger(__name__)


def generate_unique_filepath(directory: str, assignment_id: str, extension: str) -> str:
    """Return a unique filepath: <dir>/<assignment_id>_<timestamp>.<ext>."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{assignment_id}_{timestamp}.{extension}"
    path = os.path.join(directory, filename)
    # Collision detection — highly unlikely but handled
    counter = 0
    while os.path.exists(path):
        counter += 1
        filename = f"{assignment_id}_{timestamp}_{counter}.{extension}"
        path = os.path.join(directory, filename)
    return path


def get_temp_filepath(final_path: str) -> str:
    """Return a .tmp path alongside the final path for atomic writes."""
    return final_path + ".tmp"


def finalize_temp_file(temp_path: str, final_path: str) -> None:
    """Atomically rename temp file to final path."""
    os.replace(temp_path, final_path)


def cleanup_file(path: str) -> None:
    """Safely delete a file, logging but not raising on failure."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError as exc:
        log.warning("cleanup_file_failed", path=path, error=str(exc))


def cleanup_assignment_files(directory: str, assignment_id: str) -> None:
    """Remove all files whose name starts with assignment_id from directory."""
    try:
        for entry in os.scandir(directory):
            if entry.name.startswith(assignment_id):
                cleanup_file(entry.path)
    except OSError as exc:
        log.warning("cleanup_assignment_files_failed", directory=directory, error=str(exc))


def get_file_for_download(directory: str, assignment_id: str, extension: str) -> str | None:
    """Find the first file matching <assignment_id>_*.<ext> in directory."""
    try:
        for entry in os.scandir(directory):
            name = entry.name
            if name.startswith(assignment_id) and name.endswith(f".{extension}") and not name.endswith(".tmp"):
                return entry.path
    except OSError as exc:
        log.warning("get_file_for_download_error", assignment_id=assignment_id, error=str(exc))
    return None
