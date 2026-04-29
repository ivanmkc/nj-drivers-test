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
import shutil
import sys
from typing import Any
from urllib.parse import urlparse

import requests

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) drivers-test-fetch/1.0"
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


def fetch_pdf_text(url: str, *, cache_path: str | None = None) -> str:
    """Download a PDF (caching to ``cache_path`` if given) and return extracted text."""
    if cache_path is None:
        cache_path = os.path.join("/tmp", os.path.basename(urlparse(url).path) or "manual.pdf")
    if not os.path.exists(cache_path):
        print(f"  downloading {url} -> {cache_path}", flush=True)
        _http_get(url, dest=cache_path)
    else:
        print(f"  cached {cache_path}", flush=True)
    return extract_pdf_text(cache_path)


def fetch_html_text(url: str) -> str:
    """Fetch ``url`` as HTML, strip nav/footer, return main-content text."""
    try:
        from bs4 import BeautifulSoup  # type: ignore[import-not-found]
    except ImportError:
        raise RuntimeError(
            "beautifulsoup4 not installed. Run: pip install beautifulsoup4"
        ) from None

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

    Side effects: writes ``out_path``, downloads PDFs to ``/tmp`` for caching.
    Skipped (no-op) if ``out_path`` already exists and ``force`` is False.
    """
    if os.path.exists(out_path) and not force:
        print(f"  manual text already extracted: {out_path}")
        with open(out_path) as f:
            return f.read()

    code = entry.get("code", "manual")
    urls = entry.get("urls") or []
    manual_url = entry.get("manual_url", "")

    parts: list[str] = []
    if urls:
        # Multi-PDF: download and concatenate in declared order.
        if not all(_is_pdf_url(u) for u in urls):
            print("  WARNING: non-PDF URL in `urls` list; treating each as a PDF anyway.")
        for i, url in enumerate(urls, start=1):
            cache = os.path.join("/tmp", f"{code}_chapter{i:02d}.pdf")
            text = fetch_pdf_text(url, cache_path=cache)
            parts.append(f"\n\n=== chapter {i} ===\n\n")
            parts.append(text)
    elif manual_url and _is_pdf_url(manual_url):
        # Single-PDF: existing happy path.
        cache = os.path.join("/tmp", f"{code}_manual.pdf")
        parts.append(fetch_pdf_text(manual_url, cache_path=cache))
    elif manual_url:
        # HTML index: scrape main-content text.
        print(f"  scraping HTML at {manual_url}")
        parts.append(fetch_html_text(manual_url))
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
