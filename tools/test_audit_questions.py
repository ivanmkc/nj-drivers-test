"""Unit tests for ``tools/audit_questions.py``.

Run with ``pytest tools/test_audit_questions.py``. Uses tmp_path + monkeypatch to
stand up a fake ``data/states/<code>/`` tree so tests don't depend on real banks.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import audit_questions as aq
import pytest
import yaml


@pytest.fixture
def state_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Build a fake STATES_DIR with one state's directory; yield the path + write helpers."""
    states_dir = tmp_path / "data" / "states"
    states_dir.mkdir(parents=True)
    monkeypatch.setattr(aq, "STATES_DIR", str(states_dir))

    def _resolve(code: str) -> dict[str, str]:
        sdir = states_dir / code
        return {
            "questions_en_path": str(sdir / "questions_en.yaml"),
            "config_path": str(sdir / "config.json"),
        }

    def _qpath(code: str, lang: str) -> str:
        return str(states_dir / code / f"questions_{lang}.yaml")

    monkeypatch.setattr(aq, "resolve_state_paths", _resolve)
    monkeypatch.setattr(aq, "questions_path", _qpath)

    def write_bank(
        code: str, lang: str, ids: list[int], extras: dict[int, dict[str, Any]] | None = None
    ) -> Path:
        sdir = states_dir / code
        sdir.mkdir(exist_ok=True)
        extras = extras or {}
        out: dict[str, Any] = {
            "metadata": {"source": "test", "total_questions": len(ids)},
            "questions": [
                {
                    "id": i,
                    "category": extras.get(i, {}).get("category", "safe_driving_rules"),
                    "question": extras.get(i, {}).get("question", f"q{i}"),
                    "choices": {"A": "a", "B": "b", "C": "c", "D": "d"},
                    "answer": "A",
                    "explanation": f"x{i}",
                }
                for i in ids
            ],
        }
        path = sdir / f"questions_{lang}.yaml"
        with open(path, "w") as f:
            yaml.safe_dump(out, f, sort_keys=False)
        return path

    yield {"dir": states_dir, "write": write_bank}


# ---- translation_alignment_audit -----------------------------------------


def test_alignment_passes_when_ids_match(state_tree) -> None:
    state_tree["write"]("xx", "en", [1, 2, 3])
    state_tree["write"]("xx", "es", [1, 2, 3])
    assert aq.translation_alignment_audit("xx") == []


def test_alignment_flags_orphan_target_ids(state_tree) -> None:
    """ES bank has 4 IDs but EN only has 3 — the extra ID is an orphan."""
    state_tree["write"]("xx", "en", [1, 2, 3])
    state_tree["write"]("xx", "es", [1, 2, 3, 99])
    issues = aq.translation_alignment_audit("xx")
    assert len(issues) == 1
    assert "orphan" in issues[0].lower()
    assert "99" in issues[0]


def test_alignment_flags_missing_target_ids(state_tree) -> None:
    """EN has 3 IDs, ES has only 1 — the 2 missing IDs need retranslation."""
    state_tree["write"]("xx", "en", [1, 2, 3])
    state_tree["write"]("xx", "es", [1])
    issues = aq.translation_alignment_audit("xx")
    assert len(issues) == 1
    assert "missing" in issues[0].lower()
    assert "2" in issues[0] and "3" in issues[0]


def test_alignment_flags_both_orphans_and_missing(state_tree) -> None:
    state_tree["write"]("xx", "en", [1, 2, 3])
    state_tree["write"]("xx", "es", [1, 4, 5])
    issues = aq.translation_alignment_audit("xx")
    assert len(issues) == 2
    kinds = " ".join(issues).lower()
    assert "orphan" in kinds and "missing" in kinds


def test_alignment_checks_each_target_language_independently(state_tree) -> None:
    state_tree["write"]("xx", "en", [1, 2, 3])
    state_tree["write"]("xx", "es", [1, 2, 3])  # clean
    state_tree["write"]("xx", "ja", [1, 2])  # missing 3
    issues = aq.translation_alignment_audit("xx")
    assert len(issues) == 1
    assert "JA" in issues[0] and "missing" in issues[0].lower()


def test_alignment_skips_when_no_target_bank_exists(state_tree) -> None:
    state_tree["write"]("xx", "en", [1, 2, 3])
    # no ES or JA file
    assert aq.translation_alignment_audit("xx") == []


def test_alignment_skips_when_no_en_bank(state_tree) -> None:
    # No EN file means nothing to audit against — return empty (not a crash)
    (state_tree["dir"] / "xx").mkdir(exist_ok=True)
    state_tree["write"]("xx", "es", [1, 2, 3])
    assert aq.translation_alignment_audit("xx") == []


def test_alignment_orphan_message_truncates_long_lists(state_tree) -> None:
    state_tree["write"]("xx", "en", [1])
    extras = list(range(100, 120))  # 20 orphans
    state_tree["write"]("xx", "es", [1, *extras])
    issues = aq.translation_alignment_audit("xx")
    assert len(issues) == 1
    assert "20 orphan" in issues[0]
    assert "+15 more" in issues[0]  # 20 - 5 shown = 15 more


# ---- translation_staleness_audit ------------------------------------------


def test_staleness_flags_when_no_provenance(state_tree) -> None:
    state_tree["write"]("xx", "en", [1, 2])
    state_tree["write"]("xx", "es", [1, 2])  # no metadata.translation block
    issues = aq.translation_staleness_audit("xx")
    assert any("no translation provenance" in i for i in issues)


def test_staleness_passes_when_sha_matches(state_tree) -> None:
    state_tree["write"]("xx", "en", [1, 2])
    es_path = state_tree["write"]("xx", "es", [1, 2])
    en_path = state_tree["dir"] / "xx" / "questions_en.yaml"
    en_sha = hashlib.sha256(en_path.read_bytes()).hexdigest()
    es_data = yaml.safe_load(es_path.read_text())
    es_data["metadata"]["translation"] = {
        "translated_at": "2026-05-26T00:00:00Z",
        "translated_by": "test-model",
        "en_source_sha256": en_sha,
    }
    es_path.write_text(yaml.safe_dump(es_data, sort_keys=False))
    assert aq.translation_staleness_audit("xx") == []


def test_staleness_flags_when_sha_does_not_match(state_tree) -> None:
    state_tree["write"]("xx", "en", [1, 2])
    es_path = state_tree["write"]("xx", "es", [1, 2])
    es_data = yaml.safe_load(es_path.read_text())
    es_data["metadata"]["translation"] = {
        "translated_at": "2026-05-26T00:00:00Z",
        "translated_by": "test-model",
        "en_source_sha256": "0" * 64,
    }
    es_path.write_text(yaml.safe_dump(es_data, sort_keys=False))
    issues = aq.translation_staleness_audit("xx")
    assert any("stale" in i.lower() for i in issues)
