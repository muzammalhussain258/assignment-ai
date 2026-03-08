"""PDF generation using ReportLab Platypus with atomic writes and markdown parsing."""

from __future__ import annotations

import re
from typing import Any

import structlog
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from app.utils.file_manager import cleanup_file, finalize_temp_file, get_temp_filepath

log = structlog.get_logger(__name__)


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles: dict[str, ParagraphStyle] = {
        "title": ParagraphStyle(
            "AssignmentTitle",
            parent=base["Title"],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "heading1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontSize=16,
            leading=20,
            spaceAfter=6,
            spaceBefore=12,
        ),
        "heading2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontSize=14,
            leading=18,
            spaceAfter=4,
            spaceBefore=10,
        ),
        "heading3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontSize=12,
            leading=16,
            spaceAfter=4,
            spaceBefore=8,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=11,
            leading=15,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=11,
            leading=14,
            leftIndent=20,
            spaceAfter=3,
        ),
        "numbered": ParagraphStyle(
            "Numbered",
            parent=base["Normal"],
            fontSize=11,
            leading=14,
            leftIndent=20,
            spaceAfter=3,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.grey,
        ),
    }
    return styles


def _md_to_rl(text: str) -> str:
    """Convert markdown inline markup to ReportLab XML — escape HTML chars first."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    return text


def generate_pdf(
    content: str,
    filepath: str,
    metadata: dict[str, Any],
) -> None:
    """Generate a PDF file from markdown-style content with atomic write."""
    temp_path = get_temp_filepath(filepath)
    styles = _build_styles()

    try:
        doc = SimpleDocTemplate(
            temp_path,
            pagesize=A4,
            leftMargin=inch,
            rightMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
            title=metadata.get("title", ""),
            subject=metadata.get("subject", ""),
            author=metadata.get("author", "AI Assignment Generator"),
        )

        story: list[Any] = []
        bullet_buffer: list[str] = []
        numbered_buffer: list[str] = []

        def flush_bullets() -> None:
            if bullet_buffer:
                items = [ListItem(Paragraph(_md_to_rl(b), styles["bullet"])) for b in bullet_buffer]
                story.append(ListFlowable(items, bulletType="bullet", start="•"))
                story.append(Spacer(1, 4))
                bullet_buffer.clear()

        def flush_numbered() -> None:
            if numbered_buffer:
                items = [ListItem(Paragraph(_md_to_rl(n), styles["numbered"])) for n in numbered_buffer]
                story.append(ListFlowable(items, bulletType="1"))
                story.append(Spacer(1, 4))
                numbered_buffer.clear()

        first_heading = True

        for line in content.splitlines():
            try:
                stripped = line.rstrip()

                if not stripped:
                    flush_bullets()
                    flush_numbered()
                    story.append(Spacer(1, 6))
                    continue

                if stripped.startswith("#### "):
                    flush_bullets(); flush_numbered()
                    story.append(Paragraph(_md_to_rl(stripped[5:]), styles["heading3"]))
                elif stripped.startswith("### "):
                    flush_bullets(); flush_numbered()
                    story.append(Paragraph(_md_to_rl(stripped[4:]), styles["heading3"]))
                elif stripped.startswith("## "):
                    flush_bullets(); flush_numbered()
                    if not first_heading:
                        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
                    story.append(Paragraph(_md_to_rl(stripped[3:]), styles["heading2"]))
                    first_heading = False
                elif stripped.startswith("# "):
                    flush_bullets(); flush_numbered()
                    story.append(Paragraph(_md_to_rl(stripped[2:]), styles["heading1"]))
                    first_heading = False
                elif stripped.startswith("- ") or stripped.startswith("* "):
                    flush_numbered()
                    bullet_buffer.append(stripped[2:])
                elif re.match(r"^\d+\.\s", stripped):
                    flush_bullets()
                    text = re.sub(r"^\d+\.\s", "", stripped)
                    numbered_buffer.append(text)
                else:
                    flush_bullets(); flush_numbered()
                    story.append(Paragraph(_md_to_rl(stripped), styles["body"]))
            except Exception as exc:
                log.warning("pdf_line_error", error=str(exc))

        flush_bullets()
        flush_numbered()

        # Metadata footer
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        meta_parts = []
        if metadata.get("education_level"):
            meta_parts.append(f"Level: {metadata['education_level']}")
        if metadata.get("template"):
            meta_parts.append(f"Template: {metadata['template']}")
        if metadata.get("word_count"):
            meta_parts.append(f"Words: {metadata['word_count']}")
        story.append(Paragraph(" | ".join(meta_parts), styles["meta"]))

        doc.build(story)
        finalize_temp_file(temp_path, filepath)
        log.info("pdf_generated", filepath=filepath)
    except Exception as exc:
        cleanup_file(temp_path)
        raise exc
