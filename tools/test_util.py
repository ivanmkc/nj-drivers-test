"""Unit tests for ``tools/_util.py``.

Run with ``pytest tools/test_util.py``. All I/O and timers are mocked.
"""

from __future__ import annotations

import os

import _util
import pytest

# ---- chunk_text --------------------------------------------------------------


def test_chunk_text_raises_when_overlap_gte_chunk_size() -> None:
    with pytest.raises(ValueError, match="overlap"):
        _util.chunk_text("abc", chunk_size=100, overlap=100)
    with pytest.raises(ValueError, match="overlap"):
        _util.chunk_text("abc", chunk_size=100, overlap=200)


def test_chunk_text_happy_path() -> None:
    text = "a" * 500
    chunks = _util.chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) >= 2
    joined = chunks[0]
    for c in chunks[1:]:
        joined += c[50:]
    assert len(joined) >= len(text)


# ---- retry_with_backoff -----------------------------------------------------


def test_retry_first_try_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    assert _util.retry_with_backoff(lambda: 42) == 42


def test_retry_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("not yet")
        return "ok"

    assert _util.retry_with_backoff(flaky, max_attempts=3) == "ok"
    assert attempts["n"] == 3


def test_retry_exhausts_and_reraises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)

    def always_fail():
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        _util.retry_with_backoff(always_fail, max_attempts=2)


# ---- cache_path --------------------------------------------------------------


def test_cache_path_creates_uid_dir(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr("tempfile.gettempdir", lambda: str(tmp_path))
    result = _util.cache_path("test_file.pdf")
    assert os.path.isdir(os.path.dirname(result))
    assert result.endswith("test_file.pdf")
    assert f"drivers_cache_{os.getuid()}" in result


# ---- deduplicate -------------------------------------------------------------


def test_deduplicate_keeps_distinct_insurance_questions() -> None:
    """Two questions sharing boilerplate but with different distinctive terms
    should survive dedup thanks to the stopword filter."""
    q1 = {
        "id": 1,
        "question": (
            "What is the minimum amount of liability insurance coverage "
            "required for property damage per accident in Alaska?"
        ),
    }
    q2 = {
        "id": 2,
        "question": (
            "What is the minimum amount of bodily injury protection "
            "required per person under California state regulations?"
        ),
    }
    result = _util.deduplicate([q1, q2])
    assert len(result) == 2


def test_deduplicate_drops_true_near_duplicate() -> None:
    q1 = {"id": 1, "question": "When should you yield at an intersection?"}
    q2 = {"id": 2, "question": "When should you yield at an intersection?"}
    result = _util.deduplicate([q1, q2])
    assert len(result) == 1


# ---- _distinctive_words ------------------------------------------------------


def test_distinctive_words_filters_stopwords() -> None:
    words = _util._distinctive_words("What is the minimum amount of coverage required?")
    assert "what" not in words
    assert "the" not in words
    assert "minimum" in words


def test_distinctive_words_falls_back_when_all_stopwords() -> None:
    text = "the a an you your"
    words = _util._distinctive_words(text)
    assert len(words) > 0
    assert words == set(text.lower().split())
