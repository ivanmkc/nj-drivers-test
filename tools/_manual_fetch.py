"""Fetch + extract driver-manual text from PDF, multi-PDF, or HTML sources.

Used by ``setup_state.py``. Three input shapes are supported:

1. **Single PDF** — entry has ``manual_url`` ending in ``.pdf``. Download and
   extract via PyMuPDF.
2. **Multi-PDF** — entry has a non-empty ``urls`` list of PDF chapter URLs.
   Download each in declared order and concatenate, separated by
   ``\\n\\n=== chapter <n> ===\\n\\n`` markers.
3. **HTML index** — entry has ``manual_url`` whose response is HTML and ``urls``
   is absent. Scrape main-content text (BeautifulSoup) from the index page.

Always sends ``User-Agent: Mozilla/5.0`` (some state CDNs 403 default Python
clients).
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from typing import Any
from urllib.parse import urlparse

import requests
from _util import cache_path as _util_cache_path

# Full Chrome desktop UA. Bare "Mozilla/5.0" or Linux-suffixed UAs get 403/404
# from several state CDNs (confirmed 2026-04-29 on michigan.gov, mass.gov,
# publicsafety.ohio.gov, dmv.colorado.gov). Don't trim this without testing.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT_SECONDS = 60


def _http_get(url: str, *, dest: str | None = None) -> bytes:
    """GET ``url`` with a desktop UA. Optionally write to ``dest``. Returns body bytes."""
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    resp = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS, allow_redirects=True)
    resp.raise_for_status()
    if dest:
        with open(dest, "wb") as f:
            f.write(resp.content)
    return resp.content


def _is_pdf_url(url: str) -> bool:
    return urlparse(url).path.lower().endswith(".pdf")


def extract_pdf_text(pdf_path: str) -> str:
    """Extract concatenated page text from a PDF on disk via PyMuPDF."""
    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError:
        raise RuntimeError("PyMuPDF not installed. Run: pip install pymupdf") from None

    doc = fitz.open(pdf_path)
    try:
        out: list[str] = []
        for page in doc:
            out.append(str(page.get_text()))
            out.append("\n")
        return "".join(out)
    finally:
        doc.close()


# Edition-detection patterns. Ordered most-specific to least-specific; the first
# match wins. Each entry is (compiled regex, formatter); the formatter turns the
# regex match into a normalized string. Patterns are case-insensitive.
#
# Real-world examples observed across the 48 shipped state manuals:
#   AL: "June 2016 Edition"          MD: "December 2025 Edition"
#   TX: "Revised January 2026"       MO: "Revised August 2025"
#   ME: "Rev 11/23"                  FL: "rev. 08/2023"
#   NV: "March 2024"                 NJ: "2025"  (cover year)
#   OR: "2026 - 2027"                WI: "2025"
#   TN: "as of July 1, 2022"         AZ: "© 2025"  (copyright fallback)
_MONTH = (
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
)
# Year range in the plausible publication window. 1990 < year < 2100 is a
# reasonable guard against false positives like phone numbers or zip codes.
_YEAR = r"(?:19[9]\d|20\d{2})"


def _norm_month_year(m: re.Match[str]) -> str:
    return f"{m.group(1).title()} {m.group(2)}"


def _norm_rev_month_year(m: re.Match[str]) -> str:
    return f"Rev {m.group(1).title()} {m.group(2)}"


def _norm_rev_numeric(m: re.Match[str]) -> str:
    """Normalize ``Rev 11/23`` or ``rev. 08/2023`` -> ``Rev 11/2023``."""
    mm, yy = m.group(1), m.group(2)
    if len(yy) == 2:
        yy = "20" + yy
    return f"Rev {int(mm):02d}/{yy}"


def _norm_year_range(m: re.Match[str]) -> str:
    return f"{m.group(1)}-{m.group(2)}"


def _norm_year(m: re.Match[str]) -> str:
    return m.group(1)


def _norm_month_year_standalone(m: re.Match[str]) -> str:
    return f"{m.group(1).title()} {m.group(2)}"


_EditionFormatter = Any  # callable(re.Match[str]) -> str


_EDITION_PATTERNS: list[tuple[re.Pattern[str], _EditionFormatter]] = [
    # "Revised January 2026", "Revised: January 2026", "Updated August 2025"
    (
        re.compile(
            rf"\b(?:Rev(?:ised)?|Updated|Effective)\b[\s:.]*({_MONTH})\s+({_YEAR})",
            re.IGNORECASE,
        ),
        _norm_rev_month_year,
    ),
    # "Rev 11/23", "rev. 08/2023", "Revised 7/2022"
    (
        re.compile(
            r"\b(?:Rev(?:ised)?|Updated|Effective)\b[\s:.]*(\d{1,2})[/-](\d{2,4})\b",
            re.IGNORECASE,
        ),
        _norm_rev_numeric,
    ),
    # "June 2016 Edition", "December 2025 Edition"
    (
        re.compile(rf"\b({_MONTH})\s+({_YEAR})\s+Edition\b", re.IGNORECASE),
        _norm_month_year,
    ),
    # "2025 Edition", "2024 Driver Handbook", "2026 Driver's Manual"
    (
        re.compile(
            rf"\b({_YEAR})\s+(?:Edition|Driver(?:'s|’s|s’|s')?\s+"
            r"(?:Handbook|Manual|Guide|License))\b",
            re.IGNORECASE,
        ),
        _norm_year,
    ),
    # Year range, e.g. "2026 - 2027" (Oregon style cover), "2025-2026"
    (
        re.compile(rf"\b({_YEAR})\s*[-–]\s*({_YEAR})\b"),
        _norm_year_range,
    ),
    # Standalone "Month YYYY" near the cover (Nevada style).
    (
        re.compile(rf"\b({_MONTH})\s+({_YEAR})\b", re.IGNORECASE),
        _norm_month_year_standalone,
    ),
    # Copyright fallback: "© 2025" or "Copyright 2025".
    (
        re.compile(rf"(?:©|Copyright)\s*({_YEAR})", re.IGNORECASE),
        _norm_year,
    ),
    # Bare publication year as a last resort (e.g. NJ "2025" on cover).
    (
        re.compile(rf"\b({_YEAR})\b"),
        _norm_year,
    ),
]


def extract_edition(pdf_path: str, *, max_pages: int = 5) -> str:
    """Extract publication date / edition string from the cover of ``pdf_path``.

    Reads up to ``max_pages`` of front matter (most state manuals print the
    edition on the cover, inside-front, or the colophon page) and returns the
    first pattern hit. Returns an empty string when nothing matches.

    Normalized return formats include:
        - ``"Rev January 2026"``       (TX, MO)
        - ``"Rev 11/2023"``            (ME, FL)
        - ``"December 2025 Edition"``  (returned as ``"December 2025"``)
        - ``"2025-2026"``              (OR-style year range)
        - ``"2025"``                   (year-only, last resort)

    Read-only: opens the PDF in PyMuPDF and closes it; never writes.
    """
    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError:
        raise RuntimeError("PyMuPDF not installed. Run: pip install pymupdf") from None

    doc = fitz.open(pdf_path)
    try:
        n = min(max_pages, len(doc))
        text_parts: list[str] = []
        for i in range(n):
            text_parts.append(str(doc[i].get_text()))
        text = "\n".join(text_parts)
    finally:
        doc.close()

    return _extract_edition_from_text(text)


def _extract_edition_from_text(text: str) -> str:
    """Apply edition patterns to already-extracted page text. Exposed for tests."""
    for pattern, formatter in _EDITION_PATTERNS:
        m = pattern.search(text)
        if m:
            return formatter(m)
    return ""


def fetch_pdf_text(url: str, *, cache_path: str | None = None) -> str:
    """Download a PDF (caching to ``cache_path`` if given) and return extracted text."""
    if cache_path is None:
        cache_path = _util_cache_path(os.path.basename(urlparse(url).path) or "manual.pdf")
    if not os.path.exists(cache_path):
        print(f"  downloading {url} -> {cache_path}", flush=True)
        _http_get(url, dest=cache_path)
    else:
        print(f"  cached {cache_path}", flush=True)
    return extract_pdf_text(cache_path)


def fetch_html_text(url: str, body: bytes | None = None) -> str:
    """Fetch ``url`` as HTML (or parse pre-fetched ``body``), return main-content text."""
    try:
        from bs4 import BeautifulSoup  # type: ignore[import-not-found]
    except ImportError:
        raise RuntimeError(
            "beautifulsoup4 not installed. Run: pip install beautifulsoup4"
        ) from None

    if body is None:
        body = _http_get(url)
    soup = BeautifulSoup(body, "html.parser")
    # Strip the obvious chrome.
    for selector in ("nav", "header", "footer", "script", "style", "aside", "form"):
        for el in soup.find_all(selector):
            el.decompose()
    # Prefer <main>/<article>; fall back to <body>.
    main = soup.find("main") or soup.find("article") or soup.body or soup
    return main.get_text(separator="\n", strip=True)


def assemble_manual_text(entry: dict[str, Any], out_path: str, *, force: bool = False) -> str:
    """Resolve ``entry`` -> single text file at ``out_path``. Returns the text.

    Side effects: writes ``out_path``, downloads PDFs to a per-user scratch dir for caching.
    Skipped (no-op) if ``out_path`` already exists and ``force`` is False.
    """
    if os.path.exists(out_path) and not force:
        print(f"  manual text already extracted: {out_path}")
        with open(out_path) as f:
            return f.read()

    code = entry.get("code", "manual")
    urls = entry.get("urls") or []
    manual_url = entry.get("manual_url", "")
    recovery_url = entry.get("recovery_url", "")

    # When `recovery_url` is set, the canonical `manual_url` is known-broken
    # (e.g., agency migrated hosting) and we download from an Internet Archive
    # snapshot instead. `manual_url` stays the source of truth for *what* was
    # published; `recovery_url` is *where the bytes live now*.
    effective_url = recovery_url or manual_url
    if recovery_url:
        print(f"  using recovery_url (canonical {manual_url} is broken)")

    parts: list[str] = []
    if urls:
        # Multi-PDF: download and concatenate in declared order.
        if not all(_is_pdf_url(u) for u in urls):
            print("  WARNING: non-PDF URL in `urls` list; treating each as a PDF anyway.")
        for i, url in enumerate(urls, start=1):
            cache = _util_cache_path(f"{code}_chapter{i:02d}.pdf")
            text = fetch_pdf_text(url, cache_path=cache)
            parts.append(f"\n\n=== chapter {i} ===\n\n")
            parts.append(text)
    elif effective_url and _is_pdf_url(effective_url):
        # Single-PDF: existing happy path (recovery_url-aware).
        cache = _util_cache_path(f"{code}_manual.pdf")
        parts.append(fetch_pdf_text(effective_url, cache_path=cache))
    elif effective_url:
        # Extension-less URL: sniff the content. Several agencies serve PDFs
        # from download endpoints without a .pdf path (e.g. mass.gov
        # /doc/<name>/download); routing those to the HTML scraper would
        # "extract" raw PDF bytes as text.
        pdf_cache = _util_cache_path(f"{code}_manual.pdf")
        if os.path.exists(pdf_cache):
            print(f"  cached {pdf_cache}")
            parts.append(extract_pdf_text(pdf_cache))
        else:
            body = _http_get(effective_url)
            if body[:5] == b"%PDF-":
                with open(pdf_cache, "wb") as f:
                    f.write(body)
                parts.append(extract_pdf_text(pdf_cache))
            else:
                print(f"  scraping HTML at {effective_url}")
                parts.append(fetch_html_text(effective_url, body=body))
    else:
        raise ValueError(f"Catalog entry for {code!r} has neither manual_url nor urls.")

    text = "".join(parts)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        f.write(text)
    print(f"  wrote {len(text):,} chars -> {out_path}")
    return text


def find_curl() -> str | None:
    """Return path to system curl, or None. Used for legacy fallbacks."""
    return shutil.which("curl")


if __name__ == "__main__":
    # Tiny smoke entry: `python3 tools/_manual_fetch.py <url> <out_path>`.
    if len(sys.argv) != 3:
        print("usage: python3 tools/_manual_fetch.py <url> <out_path>", file=sys.stderr)
        sys.exit(2)
    entry = {"code": "smoke", "manual_url": sys.argv[1]}
    assemble_manual_text(entry, sys.argv[2], force=True)
