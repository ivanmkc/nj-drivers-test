"""Unit tests for ``tools/verify_manuals.py``.

Run with ``pytest tools/test_verify_manuals.py``. All HTTP is mocked — these
tests do NOT touch the network.
"""

from __future__ import annotations

import datetime as _dt
import json
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests
import verify_manuals as vm


def _make_response(
    *,
    status: int = 200,
    content_type: str = "application/pdf",
    content_length: int | None = 5_000_000,
    final_url: str | None = None,
    content_range: str | None = None,
) -> MagicMock:
    """Build a mock ``requests.Response``-shaped object."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status
    headers = {"Content-Type": content_type}
    if content_length is not None:
        headers["Content-Length"] = str(content_length)
    if content_range is not None:
        headers["Content-Range"] = content_range
    resp.headers = headers
    resp.url = final_url or "https://dmv.example.gov/manual.pdf"
    resp.content = b""
    resp.close = MagicMock()
    return resp


def _session_returning(head_resp: MagicMock, get_resp: MagicMock | None = None) -> MagicMock:
    sess = MagicMock(spec=requests.Session)
    sess.head.return_value = head_resp
    sess.get.return_value = get_resp or head_resp
    return sess


# ---- _is_official_host -----------------------------------------------------


@pytest.mark.parametrize(
    "host,expected",
    [
        ("dmv.ca.gov", True),
        ("www.dmv.ca.gov", True),
        ("portal.ct.gov", True),
        ("oklahoma.gov", True),
        ("dot.state.wy.us", True),
        ("scdmvonline.com", True),  # exception list
        ("driving-tests.org", False),
        ("dmvquestionbank.com", False),
        ("usdrivertraining.com", False),
        ("example.com", False),
        ("", False),
    ],
)
def test_is_official_host(host: str, expected: bool) -> None:
    assert vm._is_official_host(host) is expected


# ---- _expect_pdf -----------------------------------------------------------


def test_expect_pdf_true() -> None:
    assert vm._expect_pdf("https://x.gov/a/b/manual.pdf") is True
    assert vm._expect_pdf("https://x.gov/MANUAL.PDF") is True


def test_expect_pdf_false() -> None:
    assert vm._expect_pdf("https://x.gov/handbook/index.html") is False
    assert vm._expect_pdf("https://x.gov/handbook") is False


# ---- verify_entry verdicts -------------------------------------------------


def test_verify_entry_ok_pdf() -> None:
    entry = {"code": "vt", "manual_url": "https://dmv.vermont.gov/manual.pdf"}
    sess = _session_returning(
        _make_response(status=200, content_type="application/pdf", content_length=2_000_000)
    )
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "ok"
    assert result.http == 200
    assert result.host_official is True


def test_verify_entry_404() -> None:
    entry = {"code": "ga", "manual_url": "https://dds.georgia.gov/dead.pdf"}
    sess = _session_returning(
        _make_response(status=404, content_type="text/html", content_length=512),
        _make_response(status=404, content_type="text/html", content_length=512),
    )
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "stale"
    assert result.http == 404


def test_verify_entry_403_then_ok_via_get_fallback() -> None:
    """Some CDNs 403 HEAD but 206 a Range GET — verifier should follow."""
    entry = {"code": "co", "manual_url": "https://dmv.colorado.gov/handbook.pdf"}
    head = _make_response(status=403, content_type="text/html", content_length=0)
    get = _make_response(
        status=206,
        content_type="application/pdf",
        content_length=1024,
        content_range="bytes 0-1023/3145728",
    )
    sess = _session_returning(head, get)
    result = vm.verify_entry(entry, session=sess)
    # status=206 != 200, so this is still "stale" by our strict check —
    # which is correct: we want to surface anything that isn't a clean 200.
    assert result.http == 206
    assert result.verdict == "stale"
    # But the Content-Range total was parsed.
    assert result.content_length == 3_145_728


def test_verify_entry_redirect_to_pdf_via_non_pdf_url() -> None:
    """A /download endpoint that streams a PDF body is still ok."""
    entry = {"code": "ma", "manual_url": "https://www.mass.gov/doc/handbook/download"}
    final = _make_response(
        status=200,
        content_type="application/pdf",
        content_length=4_000_000,
        final_url="https://www.mass.gov/doc/english-drivers-manual/v2.pdf",
    )
    sess = _session_returning(final)
    result = vm.verify_entry(entry, session=sess)
    assert result.http == 200
    assert result.verdict == "ok"


def test_verify_entry_html_index_ok() -> None:
    entry = {"code": "xx", "manual_url": "https://dmv.example.gov/handbook"}
    sess = _session_returning(
        _make_response(status=200, content_type="text/html; charset=utf-8", content_length=400_000)
    )
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "ok"


def test_verify_entry_wrong_content_type() -> None:
    """200 + .pdf URL but text/html body == typical "manual moved to HTML page"."""
    entry = {"code": "mn", "manual_url": "https://dps.mn.gov/handbook.pdf"}
    sess = _session_returning(
        _make_response(status=200, content_type="text/html", content_length=300_000)
    )
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "stale"


def test_verify_entry_too_small() -> None:
    """200 with valid content-type but tiny body == probably an error landing page."""
    entry = {"code": "xx", "manual_url": "https://dmv.example.gov/m.pdf"}
    sess = _session_returning(
        _make_response(status=200, content_type="application/pdf", content_length=8_000)
    )
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "stale"


def test_verify_entry_suspicious_host() -> None:
    entry = {"code": "xx", "manual_url": "https://driving-tests.org/handbook.pdf"}
    sess = _session_returning(
        _make_response(status=200, content_type="application/pdf", content_length=5_000_000)
    )
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "suspicious-host"


def test_verify_entry_connection_error() -> None:
    entry = {"code": "xx", "manual_url": "https://dmv.example.gov/m.pdf"}
    sess = MagicMock(spec=requests.Session)
    sess.head.side_effect = requests.ConnectionError("DNS lookup failed")
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "error"
    assert result.error == "ConnectionError"


def test_verify_entry_multi_url_uses_first() -> None:
    """When ``urls`` is populated, only the first URL is HEAD-checked."""
    entry: dict[str, Any] = {
        "code": "mi",
        "manual_url": "https://www.michigan.gov/sos/landing",
        "urls": [
            "https://www.michigan.gov/-/media/ch1.pdf",
            "https://www.michigan.gov/-/media/ch2.pdf",
        ],
    }
    sess = _session_returning(
        _make_response(status=200, content_type="application/pdf", content_length=2_500_000)
    )
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "ok"
    assert result.url == entry["urls"][0]


def test_verify_entry_no_url() -> None:
    entry = {"code": "xx"}
    result = vm.verify_entry(entry, session=MagicMock(spec=requests.Session))
    assert result.verdict == "error"
    assert result.error == "no URL configured"


# ---- recovery_url ----------------------------------------------------------


def _sequential_session(*responses: MagicMock) -> MagicMock:
    """Build a session whose .head returns a different response on each call."""
    sess = MagicMock(spec=requests.Session)
    sess.head.side_effect = list(responses)
    sess.get.side_effect = list(responses)
    return sess


def test_verify_entry_recovery_promotes_to_recovered() -> None:
    canonical_dead = _make_response(status=200, content_type="text/html", content_length=2000)
    recovery_pdf = _make_response(
        status=200, content_type="application/pdf", content_length=2_300_000
    )
    entry = {
        "code": "sd",
        "manual_url": "https://dps.sd.gov/files/sd-driver-manual.pdf",
        "recovery_url": "https://web.archive.org/web/2024/https://dps.sd.gov/files/sd-driver-manual.pdf",
    }
    sess = _sequential_session(canonical_dead, recovery_pdf)
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "recovered"
    assert result.recovery_url == entry["recovery_url"]
    assert result.recovery_http == 200
    assert result.recovery_content_type == "application/pdf"


def test_verify_entry_recovery_not_probed_when_canonical_ok() -> None:
    canonical_pdf = _make_response(
        status=200, content_type="application/pdf", content_length=2_000_000
    )
    entry = {
        "code": "sd",
        "manual_url": "https://dps.sd.gov/files/m.pdf",
        "recovery_url": "https://web.archive.org/web/2024/https://dps.sd.gov/files/m.pdf",
    }
    sess = _session_returning(canonical_pdf)
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "ok"
    # Recovery probe never happened.
    assert result.recovery_url is None
    assert result.recovery_http is None


def test_verify_entry_recovery_also_fails_stays_stale() -> None:
    # Both canonical and recovery return text/html landing pages instead of
    # PDFs. Verdict stays `stale` — recovery does NOT mask the failure.
    canonical_dead = _make_response(status=200, content_type="text/html", content_length=2000)
    recovery_dead = _make_response(status=200, content_type="text/html", content_length=1500)
    entry = {
        "code": "sd",
        "manual_url": "https://dps.sd.gov/files/m.pdf",
        "recovery_url": "https://web.archive.org/web/2024/https://dps.sd.gov/files/m.pdf",
    }
    sess = _sequential_session(canonical_dead, recovery_dead)
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "stale"
    assert result.recovery_url == entry["recovery_url"]
    assert result.recovery_content_type == "text/html"


def test_verify_entry_recovery_not_consulted_for_non_official_canonical() -> None:
    # Invariant: recovery_url MAY NOT be used to bypass the host allowlist.
    # An entry whose canonical host is non-official is `suspicious-host`, NOT
    # `recovered`, regardless of recovery_url.
    canonical_response = _make_response(
        status=200, content_type="application/pdf", content_length=2_000_000
    )
    entry = {
        "code": "xx",
        "manual_url": "https://driving-tests.org/handbook.pdf",
        "recovery_url": "https://web.archive.org/web/2024/https://driving-tests.org/handbook.pdf",
    }
    sess = _session_returning(canonical_response)
    result = vm.verify_entry(entry, session=sess)
    assert result.verdict == "suspicious-host"
    assert result.recovery_url is None  # never probed


# ---- update_timestamps ----------------------------------------------------


def test_update_timestamps_only_writes_ok() -> None:
    catalog = [
        {"code": "vt", "manual_url": "https://dmv.vermont.gov/m.pdf"},
        {"code": "ga", "manual_url": "https://dds.georgia.gov/dead.pdf"},
        {"code": "sd", "manual_url": "https://dps.sd.gov/files/m.pdf"},
    ]
    results = [
        vm.VerifyResult(
            code="vt",
            url="x",
            http=200,
            content_type="application/pdf",
            content_length=2_000_000,
            expected_pdf=True,
            host_official=True,
        ),
        vm.VerifyResult(
            code="ga",
            url="x",
            http=404,
            content_type="text/html",
            content_length=512,
            expected_pdf=True,
            host_official=True,
        ),
        vm.VerifyResult(
            code="sd",
            url="x",
            http=200,
            content_type="text/html",
            content_length=2000,
            expected_pdf=True,
            host_official=True,
            recovery_url="https://web.archive.org/web/2024/x",
            recovery_http=200,
            recovery_content_type="application/pdf",
            recovery_content_length=2_300_000,
        ),
    ]
    today = _dt.date(2026, 4, 29)
    updated = vm.update_timestamps(catalog, results, today=today)
    # vt: ok -> stamped
    assert updated[0]["last_verified"] == "2026-04-29"
    # ga: stale -> not stamped
    assert "last_verified" not in updated[1]
    # sd: recovered -> stamped (bytes were retrieved, just not from canonical)
    assert updated[2]["last_verified"] == "2026-04-29"
    # Original catalog is unmodified (function returns a new list).
    assert "last_verified" not in catalog[0]


# ---- table & summary -------------------------------------------------------


def test_render_table_basic() -> None:
    results = [
        vm.VerifyResult(
            code="vt",
            url="https://dmv.vermont.gov/m.pdf",
            http=200,
            content_type="application/pdf",
            content_length=2_000_000,
            expected_pdf=True,
            host_official=True,
        )
    ]
    table = vm.render_table(results)
    assert "code" in table and "verdict" in table
    assert "vt" in table and "ok" in table
    # Has a header underline row.
    assert "----" in table


def test_summarize_counts() -> None:
    results = [
        vm.VerifyResult(
            code="a",
            url="",
            http=200,
            content_type="application/pdf",
            content_length=2_000_000,
            expected_pdf=True,
            host_official=True,
        ),
        vm.VerifyResult(
            code="b",
            url="",
            http=404,
            content_type="text/html",
            content_length=512,
            expected_pdf=True,
            host_official=True,
        ),
        vm.VerifyResult(
            code="c",
            url="",
            http=200,
            content_type="application/pdf",
            content_length=2_000_000,
            expected_pdf=True,
            host_official=False,
        ),
    ]
    tally = vm.summarize(results)
    assert tally["ok"] == 1
    assert tally["stale"] == 1
    assert tally["suspicious-host"] == 1


# ---- main returns 0 even on failures --------------------------------------


def test_main_exit_code_always_zero(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog_file = tmp_path / "manual_urls.json"
    catalog_file.write_text(
        json.dumps([{"code": "xx", "manual_url": "https://example.com/m.pdf"}])
    )

    def fake_verify_all(entries, **kwargs):
        del entries, kwargs
        return [
            vm.VerifyResult(
                code="xx",
                url="https://example.com/m.pdf",
                http=404,
                content_type="text/html",
                content_length=512,
                expected_pdf=True,
                host_official=False,
            )
        ]

    monkeypatch.setattr(vm, "verify_all", fake_verify_all)
    rc = vm.main(["--catalog", str(catalog_file)])
    assert rc == 0


# ---- catalog load/save with sentinel --------------------------------------


def test_load_catalog_skips_schema_sentinel(tmp_path: Any) -> None:
    catalog_file = tmp_path / "manual_urls.json"
    catalog_file.write_text(
        json.dumps(
            [
                {"_schema_doc": "see docs/maintaining-state-data.md"},
                {"code": "vt", "manual_url": "https://dmv.vermont.gov/m.pdf"},
            ]
        )
    )
    entries = vm.load_catalog(str(catalog_file))
    assert len(entries) == 1
    assert entries[0]["code"] == "vt"


def test_save_catalog_preserves_sentinel(tmp_path: Any) -> None:
    catalog_file = tmp_path / "manual_urls.json"
    sentinel = {"_schema_doc": "see docs/maintaining-state-data.md"}
    catalog_file.write_text(
        json.dumps([sentinel, {"code": "vt", "manual_url": "https://dmv.vermont.gov/m.pdf"}])
    )
    entries = vm.load_catalog(str(catalog_file))
    entries[0]["last_verified"] = "2026-04-29"
    vm.save_catalog(entries, str(catalog_file))
    raw = json.loads(catalog_file.read_text())
    assert raw[0] == sentinel
    assert raw[1]["last_verified"] == "2026-04-29"
