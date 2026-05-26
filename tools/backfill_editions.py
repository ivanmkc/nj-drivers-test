#!/usr/bin/env python3
"""One-shot backfill of `edition` in every state's manual_provenance.json (#59 item 4).

For each `data/states/<code>/manual.pdf`, runs `extract_edition` on the PDF's
first pages and writes the result to `manual_provenance.json::edition` — but
only when that field is currently empty (preserves maintainer overrides like
SD's `"Rev Dec 2023"`).

Usage:
    python3 tools/backfill_editions.py              # all states
    python3 tools/backfill_editions.py al ca sd     # specific states
    python3 tools/backfill_editions.py --force      # overwrite even non-empty editions

Idempotent and read-only on PDFs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from _manual_fetch import extract_edition
from _util import STATES_DIR


def backfill(code: str, *, force: bool = False) -> tuple[str, str]:
    """Return (state_code, message). message describes what happened."""
    state_dir = Path(STATES_DIR) / code
    pdf_path = state_dir / "manual.pdf"
    prov_path = state_dir / "manual_provenance.json"
    if not pdf_path.exists():
        return code, f"skip (no manual.pdf at {pdf_path})"
    if not prov_path.exists():
        return code, f"skip (no manual_provenance.json at {prov_path})"

    with open(prov_path) as f:
        prov = json.load(f)
    current = (prov.get("edition") or "").strip()
    if current and not force:
        return code, f"keep existing edition {current!r}"

    edition = extract_edition(str(pdf_path))
    if not edition:
        return code, "no edition detected on first 5 pages"
    if edition == current:
        return code, f"unchanged ({edition!r})"

    prov["edition"] = edition
    with open(prov_path, "w") as f:
        json.dump(prov, f, indent=2)
        f.write("\n")
    return code, f"wrote {edition!r} (was {current!r})" if current else f"wrote {edition!r}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("codes", nargs="*", help="State codes; defaults to all states")
    parser.add_argument(
        "--force", action="store_true", help="Overwrite even when edition is already populated"
    )
    args = parser.parse_args(argv)

    if args.codes:
        codes = [c.lower() for c in args.codes]
    else:
        codes = sorted(d for d in os.listdir(STATES_DIR) if (Path(STATES_DIR) / d).is_dir())

    for code in codes:
        out_code, msg = backfill(code, force=args.force)
        print(f"  {out_code}: {msg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
