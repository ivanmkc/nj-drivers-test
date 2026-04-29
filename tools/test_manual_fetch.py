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
    args, kwargs = g.call_args
    assert kwargs["headers"]["User-Agent"].startswith("Mozilla/5.0")
