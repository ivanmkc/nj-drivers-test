"""Unit tests for ``tools/_manual_fetch.py``.

Run with ``pytest tools/test_manual_fetch.py``. All HTTP and PDF I/O is mocked.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import _manual_fetch as mf
import pytest

# Minimum-length placeholder text for mocks that feed assemble_manual_text
# (which rejects < 5 000 chars).
_LONG = "x" * 6000

# ---- assemble_manual_text — single PDF (legacy happy path) -----------------


def test_assemble_single_pdf_writes_file(tmp_path: Any) -> None:
    entry = {"code": "vt", "manual_url": "https://dmv.vermont.gov/manual.pdf"}
    out = tmp_path / "vt.txt"
    with patch.object(mf, "fetch_pdf_text", return_value=_LONG):
        mf.assemble_manual_text(entry, str(out))
    assert out.read_text() == _LONG


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
        return _LONG

    with patch.object(mf, "fetch_pdf_text", side_effect=capture):
        mf.assemble_manual_text(entry, str(out))

    assert called_with == [entry["recovery_url"]]
    assert out.read_text() == _LONG


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
    fake_texts = iter(["CH1 " + "x" * 2000, "CH2 " + "x" * 2000, "CH3 " + "x" * 2000])

    def fake_fetch(url: str, *, cache_path: str | None = None) -> str:
        del url, cache_path
        return next(fake_texts)

    with patch.object(mf, "fetch_pdf_text", side_effect=fake_fetch):
        mf.assemble_manual_text(entry, str(out))

    text = out.read_text()
    assert "=== chapter 1 ===" in text
    assert "=== chapter 2 ===" in text
    assert "=== chapter 3 ===" in text
    assert text.index("CH1 ") < text.index("CH2 ") < text.index("CH3 ")


# ---- assemble_manual_text — HTML index ------------------------------------


def test_assemble_html_index(tmp_path: Any) -> None:
    entry = {"code": "xx", "manual_url": "https://dmv.example.gov/handbook"}
    out = tmp_path / "xx.txt"
    html_body = b"<html><body>" + b"handbook content " * 500 + b"</body></html>"
    with (
        patch.object(mf, "_http_get", return_value=html_body) as mock_get,
        patch.object(mf, "fetch_html_text", return_value="h" * 6000) as mock_html,
    ):
        mf.assemble_manual_text(entry, str(out))
    mock_get.assert_called_once()
    mock_html.assert_called_once_with("https://dmv.example.gov/handbook", body=html_body)
    assert out.read_text() == "h" * 6000


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
    with patch.object(mf, "fetch_pdf_text", return_value=_LONG):
        mf.assemble_manual_text(entry, str(out), force=True)
    assert out.read_text() == _LONG


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


# ---- extension-less URL: PDF bytes -> extract_pdf_text --------------------


def test_extensionless_url_pdf_bytes_routed_to_extract(tmp_path: Any) -> None:
    """Extension-less URL returning %PDF bytes should save to cache and call extract_pdf_text."""
    entry = {"code": "ma", "manual_url": "https://www.mass.gov/doc/handbook/download"}
    out = tmp_path / "ma.txt"
    pdf_bytes = b"%PDF-1.4 fake pdf content"
    cache_file = str(tmp_path / "ma_manual.pdf")

    with (
        patch.object(mf, "_util_cache_path", return_value=cache_file),
        patch.object(mf, "_http_get", return_value=pdf_bytes) as mock_get,
        patch.object(mf, "extract_pdf_text", return_value=_LONG) as mock_extract,
    ):
        mf.assemble_manual_text(entry, str(out))

    mock_get.assert_called_once()
    mock_extract.assert_called_once()
    assert out.read_text() == _LONG


# ---- extension-less URL: HTML bytes -> fetch_html_text --------------------


def test_extensionless_url_html_bytes_routed_to_html(tmp_path: Any) -> None:
    """Extension-less URL returning HTML bytes should call fetch_html_text with body=."""
    entry = {"code": "xx", "manual_url": "https://dmv.example.gov/handbook/index"}
    out = tmp_path / "xx.txt"
    html_bytes = b"<html><body>stuff</body></html>"
    cache_file = str(tmp_path / "xx_manual.pdf")

    with (
        patch.object(mf, "_util_cache_path", return_value=cache_file),
        patch.object(mf, "_http_get", return_value=html_bytes) as mock_get,
        patch.object(mf, "fetch_html_text", return_value=_LONG) as mock_html,
    ):
        mf.assemble_manual_text(entry, str(out))

    mock_get.assert_called_once()
    mock_html.assert_called_once_with("https://dmv.example.gov/handbook/index", body=html_bytes)


# ---- fetch_html_text with body= never calls _http_get --------------------


def test_fetch_html_text_with_body_skips_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """When body= is pre-supplied, fetch_html_text must not make an HTTP request."""
    body = b"<html><body>pre-fetched</body></html>"
    monkeypatch.setattr(mf, "_http_get", MagicMock(side_effect=AssertionError("must not call")))
    text = mf.fetch_html_text("https://example.gov/foo", body=body)
    assert "pre-fetched" in text


# ---- assemble_manual_text raises on < 5 000 chars ------------------------


def test_assemble_raises_on_short_text(tmp_path: Any) -> None:
    entry = {"code": "tiny", "manual_url": "https://dmv.example.gov/short.pdf"}
    out = tmp_path / "tiny.txt"
    with patch.object(mf, "fetch_pdf_text", return_value="short"):
        with pytest.raises(ValueError, match="5,000"):
            mf.assemble_manual_text(entry, str(out))


# ---- extract_pdf_text raises on all-whitespace pages ----------------------


def test_extract_pdf_text_raises_on_whitespace_only() -> None:
    """Scanned/image-only PDFs produce whitespace-only text — should raise."""
    fake_page = MagicMock()
    fake_page.get_text.return_value = "   \n\n  \t  "
    fake_doc = MagicMock()
    fake_doc.__iter__ = MagicMock(return_value=iter([fake_page]))
    fake_doc.close = MagicMock()

    fake_fitz = MagicMock()
    fake_fitz.open.return_value = fake_doc

    import sys

    with patch.dict(sys.modules, {"fitz": fake_fitz}):
        import importlib

        import _manual_fetch

        importlib.reload(_manual_fetch)
        with pytest.raises(ValueError, match="No extractable text"):
            _manual_fetch.extract_pdf_text("/fake/path.pdf")
        importlib.reload(_manual_fetch)
