"""Unit tests for ``tools/find_manuals.py``.

Run with ``pytest tools/test_find_manuals.py``. All Gemini/network I/O is mocked.
"""

from __future__ import annotations

import json
import os
from typing import Any

import find_manuals as fm
import pytest


@pytest.fixture
def catalog_env(tmp_path, monkeypatch: pytest.MonkeyPatch):
    """Redirect the catalog file to a tmp_path location and mock network calls."""
    catalog_path = tmp_path / "manual_urls.json"

    original_abspath = os.path.abspath

    def patched_abspath(p):
        if p is fm.__file__ or p == fm.__file__:
            return str(tmp_path / "find_manuals.py")
        return original_abspath(p)

    monkeypatch.setattr(os.path, "abspath", patched_abspath)

    def _write_catalog(entries: list[dict[str, Any]]) -> None:
        catalog_path.write_text(json.dumps(entries, indent=2))

    def _read_catalog() -> list[dict[str, Any]]:
        return json.loads(catalog_path.read_text())

    yield {
        "path": catalog_path,
        "write": _write_catalog,
        "read": _read_catalog,
    }


def test_catalog_merge_preserves_existing_and_hand_curated(
    catalog_env, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Existing entries (including hand-curated fields like recovery_url)
    are preserved when the same code is updated by a new run."""
    existing = [
        {
            "code": "sd",
            "name": "South Dakota",
            "manual_url": "https://dps.sd.gov/old.pdf",
            "recovery_url": "https://web.archive.org/web/2024/old.pdf",
        },
        {
            "code": "vt",
            "name": "Vermont",
            "manual_url": "https://dmv.vermont.gov/m.pdf",
        },
    ]
    catalog_env["write"](existing)

    def fake_find(states):
        return {
            "results": [
                {
                    "code": "sd",
                    "name": "South Dakota",
                    "agency": "DPS",
                    "manual_url": "https://dps.sd.gov/new.pdf",
                }
            ]
        }

    monkeypatch.setattr(fm, "find_manual_urls", fake_find)
    monkeypatch.setattr(fm, "find_existing", lambda: set())
    monkeypatch.setattr("sys.argv", ["find_manuals.py", "sd"])

    fm.main()

    catalog = catalog_env["read"]()
    sd = next(e for e in catalog if e["code"] == "sd")
    assert sd["manual_url"] == "https://dps.sd.gov/new.pdf"
    assert sd["recovery_url"] == "https://web.archive.org/web/2024/old.pdf"
    assert any(e["code"] == "vt" for e in catalog)


def test_new_codes_appended(catalog_env, monkeypatch: pytest.MonkeyPatch) -> None:
    """New state codes are appended to the catalog."""
    catalog_env["write"]([{"code": "vt", "name": "Vermont", "manual_url": "https://x.gov/m.pdf"}])

    def fake_find(states):
        return {
            "results": [
                {
                    "code": "oh",
                    "name": "Ohio",
                    "agency": "BMV",
                    "manual_url": "https://ohio.gov/m.pdf",
                }
            ]
        }

    monkeypatch.setattr(fm, "find_manual_urls", fake_find)
    monkeypatch.setattr(fm, "find_existing", lambda: set())
    monkeypatch.setattr("sys.argv", ["find_manuals.py", "oh"])

    fm.main()

    catalog = catalog_env["read"]()
    codes = [e["code"] for e in catalog]
    assert "oh" in codes
    assert "vt" in codes


def test_output_sorted_by_code(catalog_env, monkeypatch: pytest.MonkeyPatch) -> None:
    """Merged catalog entries are sorted alphabetically by code."""
    catalog_env["write"](
        [
            {"code": "wy", "name": "Wyoming", "manual_url": "https://wy.gov/m.pdf"},
            {"code": "al", "name": "Alabama", "manual_url": "https://al.gov/m.pdf"},
        ]
    )

    def fake_find(states):
        return {
            "results": [
                {
                    "code": "mi",
                    "name": "Michigan",
                    "agency": "SOS",
                    "manual_url": "https://mi.gov/m.pdf",
                }
            ]
        }

    monkeypatch.setattr(fm, "find_manual_urls", fake_find)
    monkeypatch.setattr(fm, "find_existing", lambda: set())
    monkeypatch.setattr("sys.argv", ["find_manuals.py", "mi"])

    fm.main()

    catalog = catalog_env["read"]()
    codes = [e["code"] for e in catalog]
    assert codes == sorted(codes)
