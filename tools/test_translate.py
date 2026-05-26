"""Unit tests for ``tools/translate.py`` invariants.

Tests the EN-as-source-of-truth invariant introduced after #59 follow-up.
Doesn't exercise Gemini — only the alignment check.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import translate as tr
import yaml


def _write_en(path: Path, ids: list[int]) -> None:
    data: dict[str, Any] = {
        "metadata": {"source": "test", "total_questions": len(ids), "categories": []},
        "questions": [
            {
                "id": i,
                "category": "safe_driving_rules",
                "question": f"en {i}",
                "choices": {"A": "a", "B": "b", "C": "c", "D": "d"},
                "answer": "A",
                "explanation": f"e{i}",
            }
            for i in ids
        ],
    }
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def _translate_mock(out_ids: list[int]):
    """Return a translate_batch stand-in that emits questions for the given IDs in order."""

    def _fn(batch: list[dict], _lang: str) -> list[dict]:
        return [
            {
                "id": q["id"],
                "category": q["category"],
                "question": f"es {q['id']}",
                "choices": {"A": "a", "B": "b", "C": "c", "D": "d"},
                "answer": "A",
                "explanation": f"e{q['id']}",
            }
            for q in batch
            if q["id"] in out_ids
        ]

    return _fn


@pytest.fixture
def state_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Stand up a fake repo with an EN bank for state ``xx``."""
    states_dir = tmp_path / "data" / "states"
    (states_dir / "xx").mkdir(parents=True)
    en_path = states_dir / "xx" / "questions_en.yaml"

    def _resolve(code: str) -> dict[str, str]:
        return {"questions_en_path": str(states_dir / code / "questions_en.yaml")}

    def _qpath(code: str, lang: str) -> str:
        return str(states_dir / code / f"questions_{lang}.yaml")

    monkeypatch.setattr(tr, "resolve_state_paths", _resolve)
    monkeypatch.setattr(tr, "questions_path", _qpath)
    yield {"en_path": en_path, "dir": states_dir / "xx"}


def _run_translate(code: str, lang: str) -> None:
    with patch.object(sys, "argv", ["translate.py", code, lang]):
        tr.main()


def test_alignment_holds_for_clean_translation(
    state_tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_en(state_tree["en_path"], [1, 2, 3])
    monkeypatch.setattr(tr, "translate_batch", _translate_mock([1, 2, 3]))
    monkeypatch.setattr(tr, "time", type("T", (), {"sleep": lambda *_: None}))
    _run_translate("xx", "es")
    es_path = state_tree["dir"] / "questions_es.yaml"
    assert es_path.exists()
    es = yaml.safe_load(es_path.read_text())
    assert sorted(q["id"] for q in es["questions"]) == [1, 2, 3]
    # Translation provenance recorded (item 6 of #59)
    assert "translation" in es["metadata"]
    assert "en_source_sha256" in es["metadata"]["translation"]


def test_alignment_fails_if_translation_introduces_orphan_ids(
    state_tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If the model returns an ID that wasn't in EN, refuse to write."""
    _write_en(state_tree["en_path"], [1, 2, 3])

    # Mock translate_batch to inject an orphan (id=99) regardless of input
    def bad_translate(batch: list[dict], _lang: str) -> list[dict]:
        return [
            {
                "id": 99,
                "category": "safe_driving_rules",
                "question": "orphan",
                "choices": {"A": "a", "B": "b", "C": "c", "D": "d"},
                "answer": "A",
                "explanation": "x",
            }
        ]

    monkeypatch.setattr(tr, "translate_batch", bad_translate)
    monkeypatch.setattr(tr, "time", type("T", (), {"sleep": lambda *_: None}))
    with pytest.raises(ValueError, match="orphan"):
        _run_translate("xx", "es")
    # No file should have been written
    assert not (state_tree["dir"] / "questions_es.yaml").exists()


def test_dropped_batches_produce_subset_not_orphan(
    state_tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If a batch fails and is skipped, the resulting bank has FEWER IDs (a subset of EN) but no orphans. The invariant allows subsets to land — they get flagged later by translation_alignment_audit as 'missing IDs'."""
    _write_en(state_tree["en_path"], [1, 2, 3])
    # Mock translate_batch to drop ID=2 (simulate partial batch failure)
    monkeypatch.setattr(tr, "translate_batch", _translate_mock([1, 3]))
    monkeypatch.setattr(tr, "time", type("T", (), {"sleep": lambda *_: None}))
    _run_translate("xx", "es")
    es = yaml.safe_load((state_tree["dir"] / "questions_es.yaml").read_text())
    tgt_ids = sorted(q["id"] for q in es["questions"])
    # Subset of EN ids — no orphans
    assert set(tgt_ids).issubset({1, 2, 3})
    assert 2 not in tgt_ids  # confirms the partial-fail scenario
