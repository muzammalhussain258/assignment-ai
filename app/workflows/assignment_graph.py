"""LangGraph 5-node assignment generation workflow."""

from __future__ import annotations

import json
from typing import Any, TypedDict

import structlog
from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, StateGraph

from app.agents.prompts import (
    ANALYZE_TOPIC_PROMPT,
    FORMAT_TEMPLATE_PROMPT,
    GENERATE_CONTENT_PROMPT,
    GENERATE_OUTLINE_PROMPT,
)
from app.templates.assignment_templates import get_template
from app.utils.docx_generator import generate_docx
from app.utils.file_manager import generate_unique_filepath
from app.utils.pdf_generator import generate_pdf

log = structlog.get_logger(__name__)


class AssignmentState(TypedDict, total=False):
    # Inputs
    topic: str
    education_level: str
    word_count: int
    template: str
    assignment_id: str
    output_dir: str

    # Runtime
    llm: BaseChatModel

    # Node outputs
    topic_analysis: str
    outline: str
    content: str
    formatted_content: str

    # File paths
    docx_path: str
    pdf_path: str

    # Error flag
    error: str | None


def _invoke_llm(llm: BaseChatModel, prompt_template: Any, variables: dict[str, Any]) -> str:
    """Invoke a prompt template with the LLM and return the string response."""
    chain = prompt_template | llm
    response = chain.invoke(variables)
    return response.content if hasattr(response, "content") else str(response)


# ────────────────────────────────────────────────────────────────────────────────
# Node 1: Analyze topic
# ────────────────────────────────────────────────────────────────────────────────

def analyze_topic(state: AssignmentState) -> AssignmentState:
    if state.get("error"):
        return state
    try:
        log.info("node_analyze_topic", topic=state["topic"])
        result = _invoke_llm(
            state["llm"],
            ANALYZE_TOPIC_PROMPT,
            {
                "topic": state["topic"],
                "education_level": state["education_level"],
                "word_count": state["word_count"],
                "template": state["template"],
            },
        )
        state["topic_analysis"] = result
        log.info("analyze_topic_done")
    except Exception as exc:
        log.error("analyze_topic_error", error=str(exc))
        state["error"] = f"Topic analysis failed: {exc}"
    return state


# ────────────────────────────────────────────────────────────────────────────────
# Node 2: Generate outline
# ────────────────────────────────────────────────────────────────────────────────

def generate_outline(state: AssignmentState) -> AssignmentState:
    if state.get("error"):
        return state
    try:
        log.info("node_generate_outline")
        template_cfg = get_template(state["template"])
        result = _invoke_llm(
            state["llm"],
            GENERATE_OUTLINE_PROMPT,
            {
                "topic": state["topic"],
                "education_level": state["education_level"],
                "word_count": state["word_count"],
                "template": state["template"],
                "formatting_instructions": template_cfg.formatting_instructions,
                "topic_analysis": state.get("topic_analysis", ""),
                "sections": ", ".join(template_cfg.sections),
            },
        )
        state["outline"] = result
        log.info("generate_outline_done")
    except Exception as exc:
        log.error("generate_outline_error", error=str(exc))
        state["error"] = f"Outline generation failed: {exc}"
    return state


# ────────────────────────────────────────────────────────────────────────────────
# Node 3: Generate content
# ────────────────────────────────────────────────────────────────────────────────

def generate_content(state: AssignmentState) -> AssignmentState:
    if state.get("error"):
        return state
    try:
        log.info("node_generate_content")
        template_cfg = get_template(state["template"])
        result = _invoke_llm(
            state["llm"],
            GENERATE_CONTENT_PROMPT,
            {
                "topic": state["topic"],
                "education_level": state["education_level"],
                "word_count": state["word_count"],
                "template": state["template"],
                "formatting_instructions": template_cfg.formatting_instructions,
                "topic_analysis": state.get("topic_analysis", ""),
                "outline": state.get("outline", ""),
            },
        )
        state["content"] = result
        log.info("generate_content_done", approx_words=len(result.split()))
    except Exception as exc:
        log.error("generate_content_error", error=str(exc))
        state["error"] = f"Content generation failed: {exc}"
    return state


# ────────────────────────────────────────────────────────────────────────────────
# Node 4: Format template
# ────────────────────────────────────────────────────────────────────────────────

def format_template(state: AssignmentState) -> AssignmentState:
    if state.get("error"):
        return state
    try:
        log.info("node_format_template")
        template_cfg = get_template(state["template"])
        result = _invoke_llm(
            state["llm"],
            FORMAT_TEMPLATE_PROMPT,
            {
                "template": template_cfg.name,
                "formatting_instructions": template_cfg.formatting_instructions,
                "education_level": state["education_level"],
                "word_count": state["word_count"],
                "content": state.get("content", ""),
            },
        )
        state["formatted_content"] = result
        log.info("format_template_done")
    except Exception as exc:
        log.error("format_template_error", error=str(exc))
        state["error"] = f"Template formatting failed: {exc}"
    return state


# ────────────────────────────────────────────────────────────────────────────────
# Node 5: Generate files
# ────────────────────────────────────────────────────────────────────────────────

def generate_files(state: AssignmentState) -> AssignmentState:
    if state.get("error"):
        return state
    try:
        log.info("node_generate_files", assignment_id=state["assignment_id"])
        content = state.get("formatted_content") or state.get("content", "")
        output_dir = state.get("output_dir", "output")
        assignment_id = state["assignment_id"]

        metadata = {
            "title": state["topic"],
            "subject": state["template"],
            "keywords": state["education_level"],
            "education_level": state["education_level"],
            "template": state["template"],
            "word_count": state["word_count"],
        }

        docx_path = generate_unique_filepath(output_dir, assignment_id, "docx")
        generate_docx(content, docx_path, metadata)
        state["docx_path"] = docx_path

        pdf_path = generate_unique_filepath(output_dir, assignment_id, "pdf")
        generate_pdf(content, pdf_path, metadata)
        state["pdf_path"] = pdf_path

        log.info("generate_files_done", docx=docx_path, pdf=pdf_path)
    except Exception as exc:
        log.error("generate_files_error", error=str(exc))
        state["error"] = f"File generation failed: {exc}"
    return state


# ────────────────────────────────────────────────────────────────────────────────
# Build the compiled graph
# ────────────────────────────────────────────────────────────────────────────────

def build_assignment_graph():
    """Compile and return the LangGraph state machine."""
    builder = StateGraph(AssignmentState)

    builder.add_node("analyze_topic", analyze_topic)
    builder.add_node("generate_outline", generate_outline)
    builder.add_node("generate_content", generate_content)
    builder.add_node("format_template", format_template)
    builder.add_node("generate_files", generate_files)

    builder.set_entry_point("analyze_topic")
    builder.add_edge("analyze_topic", "generate_outline")
    builder.add_edge("generate_outline", "generate_content")
    builder.add_edge("generate_content", "format_template")
    builder.add_edge("format_template", "generate_files")
    builder.add_edge("generate_files", END)

    return builder.compile()
