"""Shared utilities for driver's test tools."""

import os
import tempfile
import time
from collections.abc import Callable
from typing import TypedDict, TypeVar

T = TypeVar("T")

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
STATES_DIR = os.path.join(ROOT_DIR, "data", "states")


def cache_path(filename: str) -> str:
    """Return a path inside a per-user scratch dir for downloaded/extracted artifacts.

    Namespaced by uid so parallel runs by different users don't clobber each
    other's cached manuals (plain /tmp paths collided).
    """
    cache_dir = os.path.join(tempfile.gettempdir(), f"drivers_cache_{os.getuid()}")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, filename)


class StatePaths(TypedDict):
    state_dir: str
    config_path: str
    questions_en_path: str


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences from LLM response text."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[: text.rfind("```")]
        text = text.strip()
    return text


def chunk_text(text: str, chunk_size: int = 10000, overlap: int = 500) -> list[str]:
    """Split text into overlapping chunks, breaking at paragraph boundaries."""
    if overlap >= chunk_size:
        raise ValueError(f"overlap ({overlap}) must be smaller than chunk_size ({chunk_size})")
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Try to break at a paragraph boundary
            newline_pos = text.rfind("\n\n", start + chunk_size - 1000, end + 500)
            if newline_pos > start:
                end = newline_pos
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def deduplicate(
    new_questions: list[dict],
    existing_questions: list[dict] | None = None,
    threshold: float = 0.5,
) -> list[dict]:
    """Remove duplicate questions by word-overlap similarity.

    Compares each question in *new_questions* against both previously-accepted
    questions and, optionally, an *existing_questions* baseline.  Questions whose
    word-overlap ratio exceeds *threshold* are dropped.
    """
    seen: set[frozenset[str]] = set()
    if existing_questions:
        for q in existing_questions:
            key = q["question"].lower().strip()
            seen.add(frozenset(key.split()))

    unique: list[dict] = []
    for q in new_questions:
        key = q["question"].lower().strip()
        words = set(key.split())
        is_dup = False
        for existing_words in seen:
            overlap = len(words & existing_words) / max(len(words | existing_words), 1)
            if overlap > threshold:
                is_dup = True
                break
        if not is_dup:
            seen.add(frozenset(words))
            unique.append(q)
    return unique


def retry_with_backoff(fn: Callable[[], T], max_attempts: int = 3, base_delay: int = 2) -> T:
    """Call *fn* up to *max_attempts* times with exponential back-off.

    Returns the result of *fn* on success.  Re-raises the last exception if all
    attempts fail.
    """
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            if attempt < max_attempts - 1:
                wait = base_delay ** (attempt + 1)
                print(f"retry in {wait}s ({exc})...", end=" ", flush=True)
                time.sleep(wait)
            else:
                print(f"FAILED: {exc}")
    if last_exc is None:
        raise RuntimeError("retry_with_backoff exhausted attempts without capturing an exception")
    raise last_exc


def resolve_state_paths(state_code: str) -> StatePaths:
    """Return common filesystem paths for a given state code."""
    state_dir = os.path.join(STATES_DIR, state_code)
    return StatePaths(
        state_dir=state_dir,
        config_path=os.path.join(state_dir, "config.json"),
        questions_en_path=os.path.join(state_dir, "questions_en.yaml"),
    )


def questions_path(state_code: str, lang: str) -> str:
    """Return the path to a state's questions file for a given language."""
    return os.path.join(STATES_DIR, state_code, f"questions_{lang}.yaml")
