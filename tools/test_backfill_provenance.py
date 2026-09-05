"""Unit tests for ``tools/backfill_translation_provenance.py``.

Run with ``pytest tools/test_backfill_provenance.py``. Git and filesystem calls
are monkeypatched — tests never touch real state data.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import backfill_translation_provenance as bp
import pytest
import yaml


@pytest.fixture
def prov_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Build a fake STATES_DIR with helpers for provenance testing."""
    states_dir = tmp_path / "data" / "states"
    states_dir.mkdir(parents=True)
    monkeypatch.setattr(bp, "STATES_DIR", str(states_dir))

    def _resolve(code: str) -> dict[str, str]:
        sdir = states_dir / code
        return {
            "state_dir": str(sdir),
            "config_path": str(sdir / "config.json"),
            "questions_en_path": str(sdir / "questions_en.yaml"),
        }

    def _qpath(code: str, lang: str) -> str:
        return str(states_dir / code / f"questions_{lang}.yaml")

    monkeypatch.setattr(bp, "resolve_state_paths", _resolve)
    monkeypatch.setattr(bp, "questions_path", _qpath)

    def write_state(
        code: str,
        *,
        en_ids: list[int] | None = None,
        es_ids: list[int] | None = None,
        es_meta: dict[str, Any] | None = None,
        report: dict[str, Any] | None = None,
    ) -> Path:
        sdir = states_dir / code
        sdir.mkdir(exist_ok=True)

        if en_ids is not None:
            en_data: dict[str, Any] = {
                "metadata": {"source": "test"},
                "questions": [{"id": i, "question": f"q{i}"} for i in en_ids],
            }
            (sdir / "questions_en.yaml").write_text(yaml.safe_dump(en_data, sort_keys=False))

        if es_ids is not None:
            es_data: dict[str, Any] = {
                "metadata": {"source": "test", **(es_meta or {})},
                "questions": [{"id": i, "question": f"q{i}"} for i in es_ids],
            }
            (sdir / "questions_es.yaml").write_text(yaml.safe_dump(es_data, sort_keys=False))

        if report is not None:
            (sdir / "verification_report.json").write_text(json.dumps(report))

        return sdir

    yield {"dir": states_dir, "write": write_state}


def _passing_report(verified_at: str = "2026-07-01T00:00:00Z") -> dict[str, Any]:
    return {
        "verified_at": verified_at,
        "translation": {"es": {"verdict": "PASS"}},
    }


def _old_commit_time(*_args, **_kwargs) -> datetime:
    return datetime(2026, 6, 1, tzinfo=timezone.utc)


def test_stamps_when_all_guards_pass(prov_tree, monkeypatch: pytest.MonkeyPatch) -> None:
    prov_tree["write"](
        "xx",
        en_ids=[1, 2],
        es_ids=[1, 2],
        report=_passing_report(),
    )
    monkeypatch.setattr(bp, "_en_last_commit_time", _old_commit_time)

    actions = bp.backfill_state("xx", dry_run=False)
    assert any("stamped" in a for a in actions)

    es_path = prov_tree["dir"] / "xx" / "questions_es.yaml"
    es_data = yaml.safe_load(es_path.read_text())
    en_path = prov_tree["dir"] / "xx" / "questions_en.yaml"
    expected_sha = hashlib.sha256(en_path.read_bytes()).hexdigest()
    assert es_data["metadata"]["translation"]["en_source_sha256"] == expected_sha


def test_skips_when_stamp_exists(prov_tree, monkeypatch: pytest.MonkeyPatch) -> None:
    prov_tree["write"](
        "xx",
        en_ids=[1],
        es_ids=[1],
        es_meta={"translation": {"en_source_sha256": "abc123"}},
        report=_passing_report(),
    )
    monkeypatch.setattr(bp, "_en_last_commit_time", _old_commit_time)

    actions = bp.backfill_state("xx", dry_run=False)
    assert not any("stamped" in a for a in actions)


def test_skips_when_gate_not_pass(prov_tree, monkeypatch: pytest.MonkeyPatch) -> None:
    report = {
        "verified_at": "2026-07-01T00:00:00Z",
        "translation": {"es": {"verdict": "FAIL"}},
    }
    prov_tree["write"]("xx", en_ids=[1], es_ids=[1], report=report)
    monkeypatch.setattr(bp, "_en_last_commit_time", _old_commit_time)

    actions = bp.backfill_state("xx", dry_run=False)
    assert any("SKIP" in a for a in actions)
    assert not any("stamped" in a for a in actions)


def test_skips_when_en_newer_than_report(prov_tree, monkeypatch: pytest.MonkeyPatch) -> None:
    prov_tree["write"](
        "xx",
        en_ids=[1],
        es_ids=[1],
        report=_passing_report("2026-06-01T00:00:00Z"),
    )

    def _recent_commit(*_args, **_kwargs):
        return datetime(2026, 7, 15, tzinfo=timezone.utc)

    monkeypatch.setattr(bp, "_en_last_commit_time", _recent_commit)

    actions = bp.backfill_state("xx", dry_run=False)
    assert any("SKIP" in a for a in actions)
    assert not any("stamped" in a for a in actions)


def test_preserves_existing_translation_keys(prov_tree, monkeypatch: pytest.MonkeyPatch) -> None:
    """If translation metadata already has partial keys (but no en_source_sha256),
    the backfill should add to them, not overwrite."""
    prov_tree["write"](
        "xx",
        en_ids=[1],
        es_ids=[1],
        es_meta={"translation": {"translated_by": "gemini-test"}},
        report=_passing_report(),
    )
    monkeypatch.setattr(bp, "_en_last_commit_time", _old_commit_time)

    bp.backfill_state("xx", dry_run=False)

    es_data = yaml.safe_load((prov_tree["dir"] / "xx" / "questions_es.yaml").read_text())
    t = es_data["metadata"]["translation"]
    assert "en_source_sha256" in t
    assert t["translated_by"] == "gemini-test"
