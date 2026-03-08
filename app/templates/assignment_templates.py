"""Assignment document template configurations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TemplateConfig:
    name: str
    sections: list[str]
    formatting_instructions: str
    word_distribution: dict[str, float]


_TEMPLATES: dict[str, TemplateConfig] = {
    "standard": TemplateConfig(
        name="Standard Assignment",
        sections=["Title", "Introduction", "Body", "Conclusion", "References"],
        formatting_instructions=(
            "Write a clear, well-structured assignment with an introduction that "
            "states the purpose, body paragraphs each covering a key point, "
            "a conclusion that summarises the main ideas, and a references section."
        ),
        word_distribution={
            "Introduction": 0.15,
            "Body": 0.65,
            "Conclusion": 0.15,
            "References": 0.05,
        },
    ),
    "research_paper": TemplateConfig(
        name="Research Paper",
        sections=[
            "Title",
            "Abstract",
            "Introduction",
            "Literature Review",
            "Methodology",
            "Findings",
            "Discussion",
            "Conclusion",
            "References",
        ],
        formatting_instructions=(
            "Write a formal academic research paper. Include an abstract (150-250 words), "
            "a comprehensive literature review, a clearly defined methodology section, "
            "findings presented objectively, and a critical discussion of implications."
        ),
        word_distribution={
            "Abstract": 0.05,
            "Introduction": 0.10,
            "Literature Review": 0.20,
            "Methodology": 0.15,
            "Findings": 0.20,
            "Discussion": 0.20,
            "Conclusion": 0.08,
            "References": 0.02,
        },
    ),
    "essay": TemplateConfig(
        name="Essay",
        sections=["Title", "Introduction", "Body Paragraphs", "Conclusion"],
        formatting_instructions=(
            "Write a persuasive/analytical essay. Open with a hook to engage the reader, "
            "state a clear thesis, develop each body paragraph around a single idea with "
            "supporting evidence, and close with a conclusion that reinforces the thesis."
        ),
        word_distribution={
            "Introduction": 0.15,
            "Body Paragraphs": 0.70,
            "Conclusion": 0.15,
        },
    ),
    "case_study": TemplateConfig(
        name="Case Study",
        sections=[
            "Title",
            "Executive Summary",
            "Background",
            "Analysis",
            "Recommendations",
            "Conclusion",
            "References",
        ],
        formatting_instructions=(
            "Write a detailed case study. Provide an executive summary (100-200 words), "
            "background context, in-depth analysis using relevant frameworks, "
            "actionable recommendations with justification, and a brief conclusion."
        ),
        word_distribution={
            "Executive Summary": 0.08,
            "Background": 0.15,
            "Analysis": 0.40,
            "Recommendations": 0.25,
            "Conclusion": 0.08,
            "References": 0.04,
        },
    ),
    "lab_report": TemplateConfig(
        name="Lab Report",
        sections=[
            "Title",
            "Abstract",
            "Introduction",
            "Materials and Methods",
            "Results",
            "Discussion",
            "Conclusion",
            "References",
        ],
        formatting_instructions=(
            "Write a structured lab report. Include a concise abstract, clear introduction "
            "with objectives, detailed materials and methods for reproducibility, "
            "objective results presentation (tables/figures described), critical discussion "
            "of findings and limitations, and a conclusion."
        ),
        word_distribution={
            "Abstract": 0.05,
            "Introduction": 0.12,
            "Materials and Methods": 0.20,
            "Results": 0.25,
            "Discussion": 0.28,
            "Conclusion": 0.07,
            "References": 0.03,
        },
    ),
}


def get_template(name: str) -> TemplateConfig:
    """Return template config by name, falling back to 'standard'."""
    return _TEMPLATES.get(name, _TEMPLATES["standard"])


def list_templates() -> list[str]:
    return list(_TEMPLATES.keys())
