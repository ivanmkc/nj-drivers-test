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


# ---- liveness log: result_to_log_entry + append_liveness_log --------------


def _ok_result(code: str = "vt") -> vm.VerifyResult:
    return vm.VerifyResult(
        code=code,
        url=f"https://dmv.{code}.gov/manual.pdf",
        http=200,
        content_type="application/pdf",
        content_length=2_000_000,
        expected_pdf=True,
        host_official=True,
    )


def _stale_result(code: str = "ga") -> vm.VerifyResult:
    return vm.VerifyResult(
        code=code,
        url=f"https://dmv.{code}.gov/dead.pdf",
        http=404,
        content_type="text/html",
        content_length=512,
        expected_pdf=True,
        host_official=True,
    )


def _recovered_result(code: str = "sd") -> vm.VerifyResult:
    return vm.VerifyResult(
        code=code,
        url=f"https://dps.{code}.gov/files/m.pdf",
        http=200,
        content_type="text/html",
        content_length=2000,
        expected_pdf=True,
        host_official=True,
        recovery_url="https://web.archive.org/web/2024/https://dps.sd.gov/files/m.pdf",
        recovery_http=200,
        recovery_content_type="application/pdf",
        recovery_content_length=2_300_000,
    )


def test_result_to_log_entry_ok_uses_canonical_metadata() -> None:
    r = _ok_result()
    ts = _dt.datetime(2026, 5, 4, 12, 0, 0, tzinfo=_dt.timezone.utc)
    entry = vm.result_to_log_entry(r, timestamp=ts)
    assert entry["code"] == "vt"
    assert entry["url"] == r.url
    assert entry["verdict"] == "ok"
    assert entry["http_status"] == 200
    assert entry["content_type"] == "application/pdf"
    assert entry["content_length"] == 2_000_000
    assert entry["timestamp"] == "2026-05-04T12:00:00Z"
    # sha256 is optional and absent unless provided.
    assert "sha256" not in entry


def test_result_to_log_entry_recovered_uses_recovery_metadata() -> None:
    r = _recovered_result()
    ts = _dt.datetime(2026, 5, 4, 12, 0, 0, tzinfo=_dt.timezone.utc)
    entry = vm.result_to_log_entry(r, timestamp=ts)
    assert entry["verdict"] == "recovered"
    assert entry["url"] == r.recovery_url
    assert entry["http_status"] == 200
    assert entry["content_type"] == "application/pdf"
    assert entry["content_length"] == 2_300_000


def test_result_to_log_entry_includes_sha256_when_provided() -> None:
    entry = vm.result_to_log_entry(_ok_result(), sha256="abc123")
    assert entry["sha256"] == "abc123"


def test_append_liveness_log_creates_file_and_appends(tmp_path: Any) -> None:
    log_path = str(tmp_path / "subdir" / "source_liveness.jsonl")
    ts = _dt.datetime(2026, 5, 4, 12, 0, 0, tzinfo=_dt.timezone.utc)
    rows = vm.append_liveness_log(
        [_ok_result("vt"), _stale_result("ga")], log_path=log_path, timestamp=ts
    )
    assert rows == 2
    with open(log_path) as f:
        lines = [line.strip() for line in f if line.strip()]
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["code"] == "vt"
    assert first["verdict"] == "ok"
    assert first["timestamp"] == "2026-05-04T12:00:00Z"
    second = json.loads(lines[1])
    assert second["code"] == "ga"
    assert second["verdict"] == "stale"


def test_append_liveness_log_is_append_only(tmp_path: Any) -> None:
    log_path = str(tmp_path / "source_liveness.jsonl")
    vm.append_liveness_log(
        [_ok_result("vt")],
        log_path=log_path,
        timestamp=_dt.datetime(2026, 5, 4, tzinfo=_dt.timezone.utc),
    )
    vm.append_liveness_log(
        [_ok_result("vt"), _stale_result("ga")],
        log_path=log_path,
        timestamp=_dt.datetime(2026, 5, 11, tzinfo=_dt.timezone.utc),
    )
    with open(log_path) as f:
        lines = [line.strip() for line in f if line.strip()]
    # 1 row from first call + 2 rows from second call.
    assert len(lines) == 3
    timestamps = [json.loads(line)["timestamp"] for line in lines]
    assert timestamps == [
        "2026-05-04T00:00:00Z",
        "2026-05-11T00:00:00Z",
        "2026-05-11T00:00:00Z",
    ]


def test_main_log_flag_appends_jsonl(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog_file = tmp_path / "manual_urls.json"
    catalog_file.write_text(
        json.dumps([{"code": "vt", "manual_url": "https://dmv.vermont.gov/m.pdf"}])
    )
    log_file = tmp_path / "source_liveness.jsonl"

    def fake_verify_all(entries, **kwargs):
        del entries, kwargs
        return [_ok_result("vt")]

    monkeypatch.setattr(vm, "verify_all", fake_verify_all)
    rc = vm.main(["--catalog", str(catalog_file), "--log", "--log-path", str(log_file)])
    assert rc == 0
    assert log_file.exists()
    rows = [json.loads(line) for line in log_file.read_text().splitlines() if line.strip()]
    assert len(rows) == 1
    assert rows[0]["code"] == "vt"
    assert rows[0]["verdict"] == "ok"


def test_main_without_log_flag_does_not_write(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    catalog_file = tmp_path / "manual_urls.json"
    catalog_file.write_text(
        json.dumps([{"code": "vt", "manual_url": "https://dmv.vermont.gov/m.pdf"}])
    )
    log_file = tmp_path / "source_liveness.jsonl"

    def fake_verify_all(entries, **kwargs):
        del entries, kwargs
        return [_ok_result("vt")]

    monkeypatch.setattr(vm, "verify_all", fake_verify_all)
    rc = vm.main(["--catalog", str(catalog_file), "--log-path", str(log_file)])
    assert rc == 0
    assert not log_file.exists()


# ---- load_liveness_log -----------------------------------------------------


def test_load_liveness_log_missing_file_returns_empty(tmp_path: Any) -> None:
    assert vm.load_liveness_log(str(tmp_path / "nope.jsonl")) == []


def test_load_liveness_log_skips_blank_and_invalid_lines(tmp_path: Any) -> None:
    log_path = tmp_path / "source_liveness.jsonl"
    log_path.write_text(
        '{"code":"vt","verdict":"ok","timestamp":"2026-05-04T00:00:00Z"}\n'
        "\n"
        "not-json\n"
        '{"code":"ga","verdict":"stale","timestamp":"2026-05-04T00:00:00Z"}\n'
    )
    entries = vm.load_liveness_log(str(log_path))
    assert [e["code"] for e in entries] == ["vt", "ga"]


# ---- find_stale_states -----------------------------------------------------


def _entry(code: str, verdict: str, days_ago: int, now: _dt.datetime) -> dict[str, Any]:
    ts = now - _dt.timedelta(days=days_ago)
    return {
        "code": code,
        "url": f"https://dmv.{code}.gov/m.pdf",
        "verdict": verdict,
        "http_status": 200 if verdict in ("ok", "recovered") else 404,
        "content_type": "application/pdf",
        "content_length": 2_000_000,
        "timestamp": ts.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def test_find_stale_states_flags_only_old_failures() -> None:
    now = _dt.datetime(2026, 5, 26, 12, 0, 0, tzinfo=_dt.timezone.utc)
    entries = [
        # vt is fresh — last success 5 days ago.
        _entry("vt", "ok", 60, now),
        _entry("vt", "ok", 5, now),
        # ga has only-stale verdicts for the last 40 days but had a success
        # 90 days ago — that's beyond the 30-day window, so flag it.
        _entry("ga", "ok", 90, now),
        _entry("ga", "stale", 40, now),
        _entry("ga", "stale", 10, now),
        # ca is fresh — recovered counts as success.
        _entry("ca", "recovered", 3, now),
    ]
    stale = vm.find_stale_states(entries, now=now)
    assert set(stale.keys()) == {"ga"}
    assert stale["ga"]["days_since"] == 90
    assert stale["ga"]["last_success"] == "2026-02-25T12:00:00Z"


def test_find_stale_states_state_with_no_success_is_stale() -> None:
    now = _dt.datetime(2026, 5, 26, 12, 0, 0, tzinfo=_dt.timezone.utc)
    entries = [
        _entry("xx", "stale", 1, now),
        _entry("xx", "stale", 7, now),
    ]
    stale = vm.find_stale_states(entries, now=now)
    assert "xx" in stale
    assert stale["xx"]["last_success"] is None
    assert stale["xx"]["days_since"] is None


def test_find_stale_states_states_with_no_entries_omitted() -> None:
    now = _dt.datetime(2026, 5, 26, 12, 0, 0, tzinfo=_dt.timezone.utc)
    stale = vm.find_stale_states([], now=now)
    assert stale == {}


def test_find_stale_states_recovered_counts_as_success() -> None:
    now = _dt.datetime(2026, 5, 26, 12, 0, 0, tzinfo=_dt.timezone.utc)
    entries = [
        # recovered 10 days ago — well within window.
        _entry("sd", "recovered", 10, now),
        _entry("sd", "stale", 1, now),
    ]
    stale = vm.find_stale_states(entries, now=now)
    assert "sd" not in stale


def test_find_stale_states_respects_custom_window() -> None:
    now = _dt.datetime(2026, 5, 26, 12, 0, 0, tzinfo=_dt.timezone.utc)
    entries = [_entry("vt", "ok", 45, now)]
    # 30-day window: stale.
    assert "vt" in vm.find_stale_states(entries, now=now, stale_days=30)
    # 60-day window: fresh.
    assert "vt" not in vm.find_stale_states(entries, now=now, stale_days=60)


def test_find_stale_states_skips_malformed_entries() -> None:
    now = _dt.datetime(2026, 5, 26, 12, 0, 0, tzinfo=_dt.timezone.utc)
    entries: list[dict[str, Any]] = [
        {"code": "vt", "verdict": "ok"},  # missing timestamp
        {"verdict": "ok", "timestamp": "2026-05-04T00:00:00Z"},  # missing code
        {"code": "ga", "verdict": "ok", "timestamp": "not-a-date"},  # unparseable
    ]
    # All three should be silently skipped; no entries with codes means no stale.
    assert vm.find_stale_states(entries, now=now) == {}
