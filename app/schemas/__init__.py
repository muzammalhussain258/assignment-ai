"""Pydantic v2 schemas for request/response validation."""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class EducationLevel(str, Enum):
    high_school = "high_school"
    undergraduate = "undergraduate"
    university = "university"
    postgraduate = "postgraduate"
    phd = "phd"


class TemplateType(str, Enum):
    standard = "standard"
    research_paper = "research_paper"
    essay = "essay"
    case_study = "case_study"
    lab_report = "lab_report"


class LLMProviderType(str, Enum):
    openai = "openai"
    gemini = "gemini"
    anthropic = "anthropic"
    groq = "groq"


class AssignmentRequest(BaseModel):
    """Validated assignment generation request."""

    topic: str = Field(..., min_length=3, max_length=500)
    education_level: EducationLevel
    word_count: int = Field(..., ge=200, le=10000)
    template: TemplateType
    llm_provider: LLMProviderType
    api_key: Optional[str] = Field(default=None)

    @field_validator("topic", mode="before")
    @classmethod
    def sanitize_topic(cls, v: str) -> str:
        v = v.strip()
        v = re.sub(r"\s+", " ", v)
        return v

    @field_validator("word_count", mode="before")
    @classmethod
    def validate_word_count_step(cls, v: int) -> int:
        # Round to nearest 50
        return int(round(int(v) / 50) * 50)


class AssignmentResponse(BaseModel):
    """Successful assignment generation response."""

    assignment_id: str
    topic: str
    education_level: str
    word_count: int
    template: str
    message: str
    download_docx: str
    download_pdf: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    error_code: str
    detail: Optional[object] = None
    status_code: int
