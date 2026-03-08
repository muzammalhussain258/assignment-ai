"""Directory management utilities."""

from __future__ import annotations

import os


def ensure_directories(*dirs: str) -> None:
    """Create directories if they do not exist, validate write permissions."""
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        if not os.access(directory, os.W_OK):
            raise PermissionError(f"Directory not writable: {directory}")
