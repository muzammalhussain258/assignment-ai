"""Assignment service — orchestrates the LangGraph workflow."""

from __future__ import annotations

import uuid

import structlog

from app.config import get_config
from app.errors import FileGenerationError, LLMProviderError
from app.llm.llm_factory import LLMFactory
from app.schemas import AssignmentRequest, AssignmentResponse
from app.workflows.assignment_graph import build_assignment_graph

log = structlog.get_logger(__name__)


def generate_assignment(request: AssignmentRequest) -> AssignmentResponse:
    """Run the 5-node LangGraph pipeline and return response metadata."""
    cfg = get_config()
    assignment_id = str(uuid.uuid4())

    log.info(
        "assignment_generation_start",
        assignment_id=assignment_id,
        topic=request.topic,
        education_level=request.education_level.value,
        word_count=request.word_count,
        template=request.template.value,
        provider=request.llm_provider.value,
    )

    # Resolve LLM
    llm = LLMFactory.get_chat_model(
        provider=request.llm_provider.value,
        user_api_key=request.api_key,
        temperature=cfg.LLM_TEMPERATURE,
        timeout=cfg.LLM_TIMEOUT,
        max_retries=cfg.LLM_MAX_RETRIES,
    )

    # Build and invoke graph
    graph = build_assignment_graph()

    initial_state = {
        "topic": request.topic,
        "education_level": request.education_level.value,
        "word_count": request.word_count,
        "template": request.template.value,
        "assignment_id": assignment_id,
        "output_dir": cfg.OUTPUT_DIR,
        "llm": llm,
        "error": None,
    }

    final_state = graph.invoke(initial_state)

    if final_state.get("error"):
        error_msg = final_state["error"]
        if "file generation" in error_msg.lower():
            raise FileGenerationError(error_msg)
        raise LLMProviderError(error_msg)

    log.info("assignment_generation_complete", assignment_id=assignment_id)

    return AssignmentResponse(
        assignment_id=assignment_id,
        topic=request.topic,
        education_level=request.education_level.value,
        word_count=request.word_count,
        template=request.template.value,
        message="Assignment generated successfully.",
        download_docx=f"/api/v1/download/docx/{assignment_id}",
        download_pdf=f"/api/v1/download/pdf/{assignment_id}",
    )
