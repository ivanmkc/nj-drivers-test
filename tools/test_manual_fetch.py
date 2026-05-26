"""Unit tests for ``tools/_manual_fetch.py``.

Run with ``pytest tools/test_manual_fetch.py``. All HTTP and PDF I/O is mocked.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import _manual_fetch as mf
import pytest

# ---- assemble_manual_text — single PDF (legacy happy path) -----------------


def test_assemble_single_pdf_writes_file(tmp_path: Any) -> None:
    entry = {"code": "vt", "manual_url": "https://dmv.vermont.gov/manual.pdf"}
    out = tmp_path / "vt.txt"
    with patch.object(mf, "fetch_pdf_text", return_value="vermont chapter text"):
        mf.assemble_manual_text(entry, str(out))
    assert out.read_text() == "vermont chapter text"


def test_extract_edition_revised_month_year() -> None:
    text = "South Dakota Driver Manual\nRevised: December 2023\nDepartment of Public Safety"
    assert mf._extract_edition_from_text(text) == "Rev December 2023"


def test_extract_edition_revised_numeric() -> None:
    assert mf._extract_edition_from_text("rev. 8/2023 issued by ...") == "Rev 08/2023"
    assert mf._extract_edition_from_text("Revised 11/23 — internal copy") == "Rev 11/2023"


def test_extract_edition_year_with_edition_word() -> None:
    assert mf._extract_edition_from_text("2025 Driver's Handbook · published Jan 2025") == "2025"
    assert mf._extract_edition_from_text("June 2016 Edition · DMV") == "June 2016"


def test_extract_edition_year_range() -> None:
    # Oregon style cover spread
    assert mf._extract_edition_from_text("Oregon Driver Manual\n2026-2027") == "2026-2027"


def test_extract_edition_standalone_month_year() -> None:
    assert mf._extract_edition_from_text("NV DMV\nApril 2024") == "April 2024"


def test_extract_edition_copyright_fallback() -> None:
    assert mf._extract_edition_from_text("Some text\n© 2025 State of Foo, DMV") == "2025"


def test_extract_edition_returns_empty_when_no_match() -> None:
    # Just driving content with no date marker
    assert (
        mf._extract_edition_from_text("Drivers must yield at every uncontrolled intersection.")
        == ""
    )


def test_extract_edition_picks_most_specific_first() -> None:
    # Both "Revised April 2024" AND "© 2020" present — the rev pattern wins (higher specificity).
    text = "Driver Manual · Revised April 2024 · © 2020"
    assert mf._extract_edition_from_text(text) == "Rev April 2024"


def test_assemble_prefers_recovery_url(tmp_path: Any) -> None:
    entry = {
        "code": "sd",
        "manual_url": "https://dps.sd.gov/files/sd-driver-manual.pdf",
        "recovery_url": "https://web.archive.org/web/2024/https://dps.sd.gov/files/sd-driver-manual.pdf",
    }
    out = tmp_path / "sd.txt"
    called_with: list[str] = []

    def capture(url: str, *, cache_path: str | None = None) -> str:
        del cache_path
        called_with.append(url)
        return "sd manual via archive"

    with patch.object(mf, "fetch_pdf_text", side_effect=capture):
        mf.assemble_manual_text(entry, str(out))

    assert called_with == [entry["recovery_url"]]
    assert out.read_text() == "sd manual via archive"


# ---- assemble_manual_text — multi-PDF concatenation -----------------------


def test_assemble_multi_pdf_concatenates_with_separators(tmp_path: Any) -> None:
    entry = {
        "code": "mi",
        "manual_url": "https://www.michigan.gov/sos/landing",
        "urls": [
            "https://www.michigan.gov/-/media/ch1.pdf",
            "https://www.michigan.gov/-/media/ch2.pdf",
            "https://www.michigan.gov/-/media/ch3.pdf",
        ],
    }
    out = tmp_path / "mi.txt"
    fake_texts = iter(["CH1 BODY", "CH2 BODY", "CH3 BODY"])

    def fake_fetch(url: str, *, cache_path: str | None = None) -> str:
        del url, cache_path
        return next(fake_texts)

    with patch.object(mf, "fetch_pdf_text", side_effect=fake_fetch):
        mf.assemble_manual_text(entry, str(out))

    text = out.read_text()
    # Each chapter wrapped with marker.
    assert "=== chapter 1 ===" in text
    assert "=== chapter 2 ===" in text
    assert "=== chapter 3 ===" in text
    # Order preserved.
    assert text.index("CH1 BODY") < text.index("CH2 BODY") < text.index("CH3 BODY")


# ---- assemble_manual_text — HTML index ------------------------------------


def test_assemble_html_index(tmp_path: Any) -> None:
    entry = {"code": "xx", "manual_url": "https://dmv.example.gov/handbook"}
    out = tmp_path / "xx.txt"
    with patch.object(mf, "fetch_html_text", return_value="HTML body text"):
        mf.assemble_manual_text(entry, str(out))
    assert out.read_text() == "HTML body text"


# ---- assemble_manual_text — caching --------------------------------------


def test_assemble_skips_when_output_exists(tmp_path: Any) -> None:
    entry = {"code": "vt", "manual_url": "https://dmv.vermont.gov/manual.pdf"}
    out = tmp_path / "vt.txt"
    out.write_text("PRE-EXISTING TEXT")
    with patch.object(mf, "fetch_pdf_text") as fetch:
        mf.assemble_manual_text(entry, str(out))
    fetch.assert_not_called()


def test_assemble_force_overwrites(tmp_path: Any) -> None:
    entry = {"code": "vt", "manual_url": "https://dmv.vermont.gov/manual.pdf"}
    out = tmp_path / "vt.txt"
    out.write_text("PRE-EXISTING TEXT")
    with patch.object(mf, "fetch_pdf_text", return_value="NEW TEXT"):
        mf.assemble_manual_text(entry, str(out), force=True)
    assert out.read_text() == "NEW TEXT"


# ---- assemble_manual_text — bad input ------------------------------------


def test_assemble_raises_when_no_url(tmp_path: Any) -> None:
    entry = {"code": "xx"}
    out = tmp_path / "xx.txt"
    with pytest.raises(ValueError, match="neither manual_url nor urls"):
        mf.assemble_manual_text(entry, str(out))


# ---- _is_pdf_url ----------------------------------------------------------


def test_is_pdf_url() -> None:
    assert mf._is_pdf_url("https://x.gov/m.pdf") is True
    assert mf._is_pdf_url("https://x.gov/M.PDF") is True
    assert mf._is_pdf_url("https://x.gov/handbook") is False


# ---- _http_get user-agent header -----------------------------------------


def test_http_get_uses_desktop_ua() -> None:
    fake_resp = MagicMock()
    fake_resp.content = b"abc"
    fake_resp.raise_for_status = MagicMock()
    with patch.object(mf.requests, "get", return_value=fake_resp) as g:
        mf._http_get("https://example.gov/x")
    kwargs = g.call_args.kwargs
    assert kwargs["headers"]["User-Agent"].startswith("Mozilla/5.0")
