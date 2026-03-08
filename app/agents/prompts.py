"""Prompt templates for LangGraph workflow nodes."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

ANALYZE_TOPIC_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are an expert academic assistant. Analyse the provided assignment topic "
                "and return a structured JSON object with the following fields:\n"
                "- scope: brief description of the topic scope\n"
                "- complexity: one of low | medium | high\n"
                "- key_concepts: list of 3-7 key concepts\n"
                "- suggested_angle: recommended approach or angle for the assignment\n"
                "Return ONLY valid JSON, no markdown fences."
            ),
        ),
        (
            "human",
            (
                "Topic: {topic}\n"
                "Education level: {education_level}\n"
                "Word count: {word_count}\n"
                "Template: {template}"
            ),
        ),
    ]
)

GENERATE_OUTLINE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are an expert academic writer. Create a detailed outline for the assignment. "
                "Return a structured JSON object with:\n"
                "- sections: list of section objects, each with 'title' and 'word_target' (integer)\n"
                "- total_words: total estimated word count\n"
                "The word targets must sum to approximately {word_count}.\n"
                "Return ONLY valid JSON, no markdown fences."
            ),
        ),
        (
            "human",
            (
                "Topic: {topic}\n"
                "Education level: {education_level}\n"
                "Template: {template}\n"
                "Formatting instructions: {formatting_instructions}\n"
                "Topic analysis: {topic_analysis}\n"
                "Required sections: {sections}"
            ),
        ),
    ]
)

GENERATE_CONTENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are an expert academic writer producing high-quality assignments. "
                "Write the complete assignment in markdown format:\n"
                "- Use # for main title, ## for major sections, ### for subsections\n"
                "- Use **bold** for emphasis, *italic* for terms\n"
                "- Use bullet points (- item) and numbered lists where appropriate\n"
                "- Match the education level in vocabulary and depth\n"
                "- Target approximately {word_count} words\n"
                "- Follow the outline strictly\n"
                "Write ONLY the assignment content — no meta-commentary."
            ),
        ),
        (
            "human",
            (
                "Topic: {topic}\n"
                "Education level: {education_level}\n"
                "Template: {template}\n"
                "Formatting instructions: {formatting_instructions}\n"
                "Topic analysis: {topic_analysis}\n"
                "Outline: {outline}"
            ),
        ),
    ]
)

FORMAT_TEMPLATE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are an expert academic editor. Review and refine the assignment content "
                "to ensure it perfectly matches the '{template}' template requirements:\n"
                "{formatting_instructions}\n\n"
                "Preserve the markdown formatting. Fix any structural issues. "
                "Do NOT add meta-commentary. Return ONLY the refined assignment."
            ),
        ),
        (
            "human",
            (
                "Education level: {education_level}\n"
                "Target word count: {word_count}\n\n"
                "Assignment content:\n{content}"
            ),
        ),
    ]
)
