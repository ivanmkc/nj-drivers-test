"""Unit tests for ``tools/bundle.py``.

Run with ``pytest tools/test_bundle.py``. Uses tmp_path to stand up a fake
states directory — no real data files needed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import bundle
import pytest
import yaml


@pytest.fixture
def states_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Set up a fake STATES_DIR with helper to write state data."""
    sd = tmp_path / "data" / "states"
    sd.mkdir(parents=True)
    monkeypatch.setattr(bundle, "STATES_DIR", str(sd))

    def write_state(
        code: str,
        *,
        questions: list[dict[str, Any]] | None = None,
        raw_yaml: Any = None,
        config: dict[str, Any] | None = None,
    ) -> Path:
        sdir = sd / code
        sdir.mkdir(exist_ok=True)
        if config is None:
            config = {
                "name": code.upper(),
                "agency": "DMV",
                "passing_score_pct": 80,
                "test_question_count": 25,
            }
        (sdir / "config.json").write_text(json.dumps(config))
        if raw_yaml is not None:
            (sdir / "questions_en.yaml").write_text(yaml.safe_dump(raw_yaml, sort_keys=False))
        elif questions is not None:
            data = {
                "metadata": {"source": "test", "total_questions": len(questions)},
                "questions": questions,
            }
            (sdir / "questions_en.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
        return sdir

    yield {"dir": sd, "write": write_state}


def _sample_questions(n: int = 3) -> list[dict[str, Any]]:
    return [
        {
            "id": i,
            "category": "safe_driving_rules",
            "question": f"q{i}",
            "choices": {"A": "a", "B": "b", "C": "c", "D": "d"},
            "answer": "A",
            "explanation": f"e{i}",
        }
        for i in range(1, n + 1)
    ]


def test_build_bundle_raises_on_bare_list(states_dir) -> None:
    """If questions YAML is a bare list instead of a mapping, raise with the state code."""
    states_dir["write"]("xx", raw_yaml=[{"id": 1, "question": "q"}])
    with pytest.raises(ValueError, match="xx"):
        bundle.build_bundle()


def test_build_bundle_happy_path(states_dir) -> None:
    states_dir["write"]("ab", questions=_sample_questions(3))
    states_dir["write"]("cd", questions=_sample_questions(2))
    result = bundle.build_bundle()
    assert "states" in result
    assert len(result["states"]) == 2
    codes = [s["code"] for s in result["states"]]
    assert codes == ["ab", "cd"]
    assert len(result["states"][0]["languages"]["en"]) == 3
    assert len(result["states"][1]["languages"]["en"]) == 2


def test_build_bundle_trust_metadata(states_dir) -> None:
    """States carry categories, source, verification, and per-question evidence."""
    sdir = states_dir["write"](
        "tv",
        questions=_sample_questions(3),
        config={
            "name": "TV",
            "agency": "DMV",
            "passing_score_pct": 80,
            "test_question_count": 25,
            "source": "2026 TV Driver Manual",
        },
    )
    report = {
        "verified_at": "2026-08-01T00:00:00Z",
        "overall_verdict": "PASS",
        "source": {"manual_url": "https://example.gov/manual.pdf", "edition": "2026"},
        "precision": {
            "avg_fidelity": 9.9,
            "grade": "A",
            "judged_count": 3,
            "evidence_by_question_id": {"1": ["Quote one.", "Quote two.", "Quote three."]},
        },
        "recall": {"coverage_pct": 96.0},
        "translation": {"es": {"verdict": "PASS"}},
    }
    (sdir / "verification_report.json").write_text(json.dumps(report))

    result = bundle.build_bundle()
    state = next(s for s in result["states"] if s["code"] == "tv")
    assert state["source"] == "2026 TV Driver Manual"
    assert state["categories"] == {"safe_driving_rules": 3}
    v = state["verification"]
    assert v["overall"] == "PASS"
    assert v["manual_url"] == "https://example.gov/manual.pdf"
    assert v["precision_grade"] == "A"
    assert v["recall_coverage_pct"] == 96.0
    assert v["translations"] == {"es": "PASS"}
    q1 = next(q for q in state["languages"]["en"] if q["id"] == 1)
    assert q1["evidence"] == ["Quote one.", "Quote two."]  # capped at 2 quotes
    q2 = next(q for q in state["languages"]["en"] if q["id"] == 2)
    assert "evidence" not in q2


def test_build_bundle_no_report_yields_null_verification(states_dir) -> None:
    states_dir["write"]("nr", questions=_sample_questions(2))
    result = bundle.build_bundle()
    state = next(s for s in result["states"] if s["code"] == "nr")
    assert state["verification"] is None
    assert state["categories"] == {"safe_driving_rules": 2}
    assert all("evidence" not in q for q in state["languages"]["en"])
