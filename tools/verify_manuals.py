#!/usr/bin/env python3
"""HEAD-check every entry in ``tools/manual_urls.json`` and report drift.

Reads the catalog, issues ``HEAD`` (with ``Range``-GET fallback) against every
URL using a desktop ``User-Agent`` (some state CDNs 403 default ``curl``/python
clients), and validates:

* HTTP 200 after redirects.
* ``Content-Type`` matches expectation: ``application/pdf`` for ``.pdf`` URLs;
  ``text/html`` allowed for HTML index entries.
* ``Content-Length`` > 100 KB (catches the "200-but-tiny-error-page" pattern).
* Host is on the official state-government allowlist (``*.gov`` + a small
  documented exception list, see ``OFFICIAL_HOST_ALLOWLIST_NOTES``).

Usage:
    python3 tools/verify_manuals.py                    # report only
    python3 tools/verify_manuals.py --update-timestamps  # also write last_verified

Always exits 0 (so a scheduled CI job stays green and merely surfaces drift via
its tracking issue). Prints a summary block with pass/fail counts.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import requests

CATALOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual_urls.json")

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) drivers-test-verify/1.0"
TIMEOUT_SECONDS = 20
MIN_CONTENT_BYTES = 100 * 1024  # 100 KB

# State-agency hosts that are not under a `*.gov` TLD but ARE the official
# canonical source. Keep this list short and document the reason inline.
OFFICIAL_HOST_ALLOWLIST_EXCEPTIONS: dict[str, str] = {
    # South Carolina DMV uses the .com host (linked from sc.gov) for all
    # downloads. https://scdmvonline.com/ is the official online portal.
    "scdmvonline.com": "Official SC DMV portal (linked from sc.gov).",
    # Honolulu CSD hosts Hawaii's manual on a city-county subdomain that uses
    # *.gov, but legacy URLs may resolve to the bare honolulu.gov host.
    "www.honolulu.gov": "City and County of Honolulu official site.",
    "honolulu.gov": "City and County of Honolulu official site.",
    # Some state DOTs front their CDN via a non-.gov vanity host that
    # ultimately maps to the same .gov backing store. Add only after manual
    # verification that the asset is canonical.
}


@dataclass
class VerifyResult:
    """One row in the verification report."""

    code: str
    url: str
    http: int | None  # final status code, or None on connection failure
    content_type: str | None
    content_length: int | None
    expected_pdf: bool
    host_official: bool
    error: str | None = None
    redirected_to: str | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        """Single-word verdict: ``ok``, ``stale``, ``suspicious-host``, ``error``.

        ``ok`` requires:
        * No transport error.
        * Host on the official-state-agency allowlist.
        * HTTP 200 (after redirects).
        * Content-Type is either ``application/pdf`` or ``text/html``.
          When the URL path ends in ``.pdf``, the body MUST be ``application/pdf``
          (otherwise the link has been silently retargeted to a landing page).
        * Body is at least ``MIN_CONTENT_BYTES`` (or unknown — some servers
          omit Content-Length).
        """
        if self.error is not None:
            return "error"
        if not self.host_official:
            return "suspicious-host"
        if self.http != 200:
            return "stale"
        ct = (self.content_type or "").split(";")[0].strip().lower()
        if self.expected_pdf and ct != "application/pdf":
            # .pdf URL silently retargeted to an HTML landing page.
            return "stale"
        if ct not in ("application/pdf", "text/html"):
            return "stale"
        if self.content_length is not None and self.content_length < MIN_CONTENT_BYTES:
            return "stale"
        return "ok"


def _is_official_host(host: str) -> bool:
    """Return True if the host belongs to a state-government allowlist."""
    if not host:
        return False
    host = host.lower()
    if host in OFFICIAL_HOST_ALLOWLIST_EXCEPTIONS:
        return True
    # Strip leading "www." for the .gov check.
    naked = host[4:] if host.startswith("www.") else host
    parts = naked.split(".")
    # *.gov, *.<something>.gov, and *.gov.<state-cctld> are accepted.
    if parts and parts[-1] == "gov":
        return True
    # A handful of state portals use *.<state>.us — accept.
    if len(parts) >= 2 and parts[-1] == "us" and len(parts[-2]) == 2:
        return True
    return False


def _expect_pdf(url: str) -> bool:
    """Decide whether the URL should resolve to a PDF based on its path."""
    path = urlparse(url).path.lower()
    return path.endswith(".pdf")


def _head_or_get(
    url: str,
    *,
    session: requests.Session,
    timeout: int = TIMEOUT_SECONDS,
) -> tuple[requests.Response, str | None]:
    """Issue HEAD; on 4xx/5xx fall back to a 1-byte ranged GET.

    Some CDNs serve 405/403 on HEAD but happily honor ranged GET. Returns the
    final ``Response`` and the final URL string after redirects.
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    resp = session.head(url, allow_redirects=True, timeout=timeout, headers=headers)
    if resp.status_code >= 400:
        # Fall back to a tiny ranged GET — same data, cheaper than full GET.
        headers_get = dict(headers)
        headers_get["Range"] = "bytes=0-1023"
        resp = session.get(
            url, allow_redirects=True, timeout=timeout, headers=headers_get, stream=True
        )
        # Drain (it's only ~1KB) so the connection can be reused.
        try:
            _ = resp.content
        finally:
            resp.close()
    return resp, resp.url


def verify_entry(
    entry: dict[str, Any], *, session: requests.Session | None = None
) -> VerifyResult:
    """Verify a single catalog entry. Multi-URL entries verify the FIRST URL."""
    code = entry.get("code", "?")
    urls = entry.get("urls") or []
    primary_url = urls[0] if urls else entry.get("manual_url", "")
    if not primary_url:
        return VerifyResult(
            code=code,
            url="",
            http=None,
            content_type=None,
            content_length=None,
            expected_pdf=False,
            host_official=False,
            error="no URL configured",
        )

    expected_pdf = _expect_pdf(primary_url)
    host = urlparse(primary_url).hostname or ""
    host_official = _is_official_host(host)

    sess = session or requests.Session()
    try:
        resp, final_url = _head_or_get(primary_url, session=sess)
    except requests.RequestException as exc:
        return VerifyResult(
            code=code,
            url=primary_url,
            http=None,
            content_type=None,
            content_length=None,
            expected_pdf=expected_pdf,
            host_official=host_official,
            error=type(exc).__name__,
        )

    cl_raw = resp.headers.get("Content-Length")
    try:
        content_length = int(cl_raw) if cl_raw else None
    except ValueError:
        content_length = None

    # If the response had a Range body, Content-Length reflects the slice size.
    # Prefer Content-Range total when present (e.g. "bytes 0-1023/1234567").
    cr_raw = resp.headers.get("Content-Range")
    if cr_raw and "/" in cr_raw:
        try:
            content_length = int(cr_raw.split("/", 1)[1])
        except ValueError:
            pass

    return VerifyResult(
        code=code,
        url=primary_url,
        http=resp.status_code,
        content_type=resp.headers.get("Content-Type"),
        content_length=content_length,
        expected_pdf=expected_pdf,
        host_official=host_official,
        redirected_to=final_url if final_url and final_url != primary_url else None,
    )


def verify_all(
    entries: Iterable[dict[str, Any]],
    *,
    session: requests.Session | None = None,
) -> list[VerifyResult]:
    """Verify every entry. Caller may pass a pre-built session for tests."""
    sess = session or requests.Session()
    results: list[VerifyResult] = []
    for e in entries:
        results.append(verify_entry(e, session=sess))
    return results


def _human_bytes(n: int | None) -> str:
    if n is None:
        return "?"
    if n < 1024:
        return f"{n}B"
    if n < 1024 * 1024:
        return f"{n // 1024}KB"
    return f"{n / (1024 * 1024):.1f}MB"


def render_table(results: list[VerifyResult]) -> str:
    """Pretty-print results as a fixed-width table."""
    rows: list[tuple[str, ...]] = [("code", "verdict", "http", "content-type", "size", "url")]
    for r in results:
        ct = (r.content_type or "?").split(";")[0].strip()
        rows.append(
            (
                r.code,
                r.verdict,
                str(r.http) if r.http is not None else (r.error or "ERR"),
                ct,
                _human_bytes(r.content_length),
                (r.url[:78] + "...") if len(r.url) > 80 else r.url,
            )
        )
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    out_lines: list[str] = []
    for i, row in enumerate(rows):
        line = "  ".join(cell.ljust(widths[j]) for j, cell in enumerate(row))
        out_lines.append(line)
        if i == 0:
            out_lines.append("  ".join("-" * widths[j] for j in range(len(widths))))
    return "\n".join(out_lines)


def summarize(results: list[VerifyResult]) -> dict[str, int]:
    """Return verdict-count tallies."""
    tally: dict[str, int] = {}
    for r in results:
        tally[r.verdict] = tally.get(r.verdict, 0) + 1
    return tally


def update_timestamps(
    catalog: list[dict[str, Any]],
    results: list[VerifyResult],
    *,
    today: _dt.date | None = None,
) -> list[dict[str, Any]]:
    """Return a NEW catalog list with ``last_verified`` written for every ok row."""
    today = today or _dt.datetime.now(_dt.timezone.utc).date()
    by_code = {r.code: r for r in results}
    updated: list[dict[str, Any]] = []
    for entry in catalog:
        new_entry = dict(entry)
        result = by_code.get(entry.get("code", ""))
        if result is not None and result.verdict == "ok":
            new_entry["last_verified"] = today.isoformat()
        updated.append(new_entry)
    return updated


def load_catalog(path: str = CATALOG_PATH) -> list[dict[str, Any]]:
    """Load the catalog. Skips the leading ``_schema_doc`` sentinel if present.

    Strict JSON doesn't allow comments, so the schema is documented at the top
    of ``manual_urls.json`` via a sentinel object whose only key is
    ``_schema_doc``. Real entries always have a ``code`` key.
    """
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list at {path}, got {type(data).__name__}")
    return [e for e in data if isinstance(e, dict) and "code" in e]


def _load_raw_catalog(path: str) -> list[dict[str, Any]]:
    """Load the raw JSON list, including any sentinel entries."""
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list at {path}, got {type(data).__name__}")
    return data


def save_catalog(catalog: list[dict[str, Any]], path: str = CATALOG_PATH) -> None:
    """Write back the catalog, preserving any leading sentinel (e.g. ``_schema_doc``)."""
    try:
        raw = _load_raw_catalog(path)
        sentinels = [e for e in raw if isinstance(e, dict) and "code" not in e]
    except (FileNotFoundError, ValueError):
        sentinels = []
    real_entries = [e for e in catalog if isinstance(e, dict) and "code" in e]
    out = sentinels + real_entries
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update-timestamps",
        action="store_true",
        help="Write last_verified=<today> back to entries that pass verification.",
    )
    parser.add_argument(
        "--catalog",
        default=CATALOG_PATH,
        help="Path to manual_urls.json (default: tools/manual_urls.json).",
    )
    parser.add_argument(
        "--codes",
        nargs="*",
        help="Optional state codes to verify (default: all entries).",
    )
    args = parser.parse_args(argv)

    catalog = load_catalog(args.catalog)
    if args.codes:
        wanted = {c.lower() for c in args.codes}
        entries = [e for e in catalog if e.get("code", "").lower() in wanted]
    else:
        entries = catalog

    results = verify_all(entries)

    print(render_table(results))
    print()
    tally = summarize(results)
    print(
        "summary: "
        + " ".join(f"{k}={v}" for k, v in sorted(tally.items()))
        + f"  total={len(results)}"
    )

    failures = [r for r in results if r.verdict != "ok"]
    if failures:
        print("\nfailures:")
        for r in failures:
            extra = []
            if r.error:
                extra.append(f"error={r.error}")
            if r.redirected_to:
                extra.append(f"redirected_to={r.redirected_to}")
            extra_str = (" " + " ".join(extra)) if extra else ""
            print(f"  {r.code}: {r.verdict} (http={r.http} ct={r.content_type}){extra_str}")

    if args.update_timestamps:
        updated = update_timestamps(catalog, results)
        save_catalog(updated, args.catalog)
        ok_count = sum(1 for r in results if r.verdict == "ok")
        print(f"\nUpdated last_verified on {ok_count} entries -> {args.catalog}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
