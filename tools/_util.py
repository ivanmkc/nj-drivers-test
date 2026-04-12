"""Shared utilities for driver's test tools."""


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences from LLM response text."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[: text.rfind("```")]
        text = text.strip()
    return text
