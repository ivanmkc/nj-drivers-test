"""Unit tests for ``tools/cross_state_dedupe.py``.

Run with ``pytest tools/test_cross_state_dedupe.py``. No network, no Gemini.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import cross_state_dedupe as csd
import yaml


def _write_state(
    states_dir: Path,
    code: str,
    questions: list[dict[str, Any]],
) -> None:
    sd = states_dir / code
    sd.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {"source": f"{code} manual", "total_questions": len(questions)},
        "questions": questions,
    }
    (sd / "questions_en.yaml").write_text(yaml.safe_dump(payload, sort_keys=False))


def _build_fixture(tmp_path: Path) -> Path:
    """Build 3 fake states sharing an identical and a near-identical question."""
    states_dir = tmp_path / "states"
    # Shared / contaminated stem appears in all three states with tiny edits.
    contaminated = "What is the legal blood alcohol concentration limit for drivers?"
    near = "What is the legal blood-alcohol concentration limit for drivers?"
    near2 = "What is the legal blood alcohol concentration limit for adult drivers?"

    _write_state(
        states_dir,
        "aa",
        [
            {
                "id": 1,
                "category": "alcohol_drugs_health",
                "question": contaminated,
                "choices": {"A": "0.05", "B": "0.08", "C": "0.10", "D": "0.12"},
                "answer": "B",
                "explanation": "0.08 statewide.",
            },
            # Unique to aa.
            {
                "id": 2,
                "category": "license_system",
                "question": "Which Alaska department issues driver licenses?",
                "choices": {"A": "DPS", "B": "DOA", "C": "DOT", "D": "DOE"},
                "answer": "B",
                "explanation": "DOA per Alaska statute.",
            },
            # Sign question — must be filtered out even if it shares text.
            {
                "id": 3,
                "image": "stop.png",
                "category": "signs_and_signals",
                "question": "What does this sign mean?",
                "choices": {"A": "Stop", "B": "Yield", "C": "Go", "D": "Slow"},
                "answer": "A",
                "explanation": "Octagonal red stop sign.",
            },
        ],
    )
    _write_state(
        states_dir,
        "bb",
        [
            {
                "id": 10,
                "category": "alcohol_drugs_health",
                "question": near,
                "choices": {"A": "0.05", "B": "0.08", "C": "0.10", "D": "0.12"},
                "answer": "B",
                "explanation": "0.08 statewide.",
            },
            {
                "id": 11,
                "image": "yield.png",
                "category": "signs_and_signals",
                "question": "What does this sign mean?",
                "choices": {"A": "Stop", "B": "Yield", "C": "Go", "D": "Slow"},
                "answer": "B",
                "explanation": "Triangular yield.",
            },
        ],
    )
    _write_state(
        states_dir,
        "cc",
        [
            {
                "id": 99,
                "category": "alcohol_drugs_health",
                "question": near2,
                "choices": {"A": "0.05", "B": "0.08", "C": "0.10", "D": "0.12"},
                "answer": "B",
                "explanation": "0.08 statewide.",
            },
            {
                "id": 100,
                "category": "safe_driving_rules",
                "question": "How many feet ahead should you scan while driving downtown?",
                "choices": {"A": "5", "B": "50", "C": "500", "D": "5000"},
                "answer": "C",
                "explanation": "Scan well ahead.",
            },
        ],
    )
    return states_dir


def test_iter_all_questions_skips_sign_questions(tmp_path: Path) -> None:
    states_dir = _build_fixture(tmp_path)
    pairs = list(csd.iter_all_questions(str(states_dir)))
    # 3 contaminated + 1 alaska-only + 1 cc-only scan question = 5 non-sign across states.
    assert len(pairs) == 5
    # No image fields survived.
    assert all("image" not in q for _, q in pairs)
    # All three states represented.
    assert {code for code, _ in pairs} == {"aa", "bb", "cc"}


def test_clustering_catches_near_duplicates(tmp_path: Path) -> None:
    states_dir = _build_fixture(tmp_path)
    records = list(csd.iter_all_questions(str(states_dir)))
    raw = csd.build_clusters(records, threshold=0.6)
    clusters = csd.filter_clusters(raw, records, min_states=3)
    assert len(clusters) == 1
    cluster = clusters[0]
    assert set(cluster["states"].keys()) == {"aa", "bb", "cc"}
    assert cluster["size"] == 3
    assert "blood" in cluster["sample"].lower()


def test_min_states_filter_drops_two_state_clusters(tmp_path: Path) -> None:
    states_dir = _build_fixture(tmp_path)
    records = list(csd.iter_all_questions(str(states_dir)))
    raw = csd.build_clusters(records, threshold=0.6)
    # With min_states=4 and only 3 states in fixture, nothing should pass.
    clusters = csd.filter_clusters(raw, records, min_states=4)
    assert clusters == []


def test_normalize_strips_punctuation_and_case() -> None:
    assert csd.normalize("Hello, World!!  Foo-bar.") == "hello world foo bar"


def test_load_state_questions_filters_signs(tmp_path: Path) -> None:
    states_dir = _build_fixture(tmp_path)
    # Point STATES_DIR at the fixture by monkeypatching the module constant.
    original = csd.STATES_DIR
    try:
        csd.STATES_DIR = str(states_dir)  # type: ignore[misc]
        qs = csd.load_state_questions("aa")
        assert len(qs) == 2
        assert all("image" not in q for q in qs)
    finally:
        csd.STATES_DIR = original  # type: ignore[misc]


def test_render_report_well_formed_with_clusters(tmp_path: Path) -> None:
    states_dir = _build_fixture(tmp_path)
    records = list(csd.iter_all_questions(str(states_dir)))
    raw = csd.build_clusters(records, threshold=0.6)
    clusters = csd.filter_clusters(raw, records, min_states=3)
    report = csd.render_report(
        clusters,
        threshold=0.6,
        min_states=3,
        total_questions=len(records),
        total_states=3,
    )
    # Required sections present.
    assert report.startswith("# Cross-State Question Contamination Report")
    assert "## What this report is" in report
    assert "## How to triage clusters" in report
    assert "## Clusters" in report
    # Cluster table rendered.
    assert "| State | Question IDs |" in report
    assert "| aa |" in report
    assert "| bb |" in report
    assert "| cc |" in report
    # No raw Python repr leaked.
    assert "defaultdict" not in report
    assert "{'" not in report


def test_render_report_handles_empty(tmp_path: Path) -> None:
    report = csd.render_report(
        [],
        threshold=0.85,
        min_states=5,
        total_questions=0,
        total_states=0,
    )
    assert "No clusters found" in report
    assert report.startswith("# Cross-State Question Contamination Report")


def test_main_writes_output_file(tmp_path: Path) -> None:
    states_dir = _build_fixture(tmp_path)
    out = tmp_path / "report.md"
    rc = csd.main(
        [
            "--threshold",
            "0.6",
            "--min-states",
            "3",
            "--out",
            str(out),
            "--states-dir",
            str(states_dir),
        ]
    )
    assert rc == 0
    assert out.exists()
    body = out.read_text()
    assert "# Cross-State Question Contamination Report" in body
    assert body.endswith("\n")
    # Cluster surfaced.
    assert "Cluster 1" in body


def test_missing_state_yaml_is_skipped(tmp_path: Path) -> None:
    states_dir = tmp_path / "states"
    states_dir.mkdir()
    # A directory without a YAML file should be skipped silently.
    (states_dir / "zz").mkdir()
    pairs = list(csd.iter_all_questions(str(states_dir)))
    assert pairs == []


def test_load_state_questions_missing_path(tmp_path: Path) -> None:
    original = csd.STATES_DIR
    try:
        csd.STATES_DIR = str(tmp_path)  # type: ignore[misc]
        assert csd.load_state_questions("nope") == []
    finally:
        csd.STATES_DIR = original  # type: ignore[misc]


def test_states_dir_default_exists() -> None:
    """Sanity check the real STATES_DIR resolves; safety net for path drift."""
    assert os.path.isdir(csd.STATES_DIR)
