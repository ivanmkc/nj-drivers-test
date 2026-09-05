#!/usr/bin/env python3
"""Open a ``stale-source`` GitHub issue for every state whose manual URL has
not produced a successful fetch in the last ``STALE_DAYS`` days.

Reads ``data/source_liveness.jsonl``, finds stale states via
``verify_manuals.find_stale_states``, and shells out to ``gh issue create`` for
each. Skips states that already have an open ``stale-source`` issue (matched by
the bracketed state code in the title).

Invoked from ``.github/workflows/source-liveness.yml`` after the verify step.
Requires ``gh`` on PATH and a ``GH_TOKEN`` env var with ``issues: write``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys

import verify_manuals as vm


def _existing_open_issue(code: str) -> bool:
    """Return True iff an open ``stale-source`` issue for ``code`` already exists."""
    upper = code.upper()
    proc = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--label",
            "stale-source",
            "--state",
            "open",
            "--search",
            f"in:title [stale-source] {upper}",
            "--json",
            "number,title",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    # `gh` returns JSON list; presence of ANY result that mentions `[code]` is
    # enough — we use the bracketed code as the canonical marker.
    return f"[stale-source] {upper}" in proc.stdout


def _open_issue(code: str, info: dict[str, object]) -> None:
    days = info.get("days_since")
    if isinstance(days, int):
        window = f"{days} days"
    else:
        window = "forever (no success on record)"
    title = f"[stale-source] {code.upper()} — no successful fetch in {window}"
    last_success = info.get("last_success") or "(none on record)"
    last_seen = info.get("last_seen") or "(unknown)"
    body = (
        f"Automated stale-source detector flagged **{code.upper()}**.\n\n"
        f"- last successful verification: {last_success}\n"
        f"- last seen at all: {last_seen}\n"
        f"- days since last success: {days if days is not None else 'n/a'}\n\n"
        f"See `data/source_liveness.jsonl` for the timeline and "
        f"`tools/manual_urls.json` for the catalog entry."
    )
    subprocess.run(
        [
            "gh",
            "issue",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--label",
            "stale-source",
        ],
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log-path",
        default=vm.LIVENESS_LOG_PATH,
        help="Path to the JSONL liveness log (default: data/source_liveness.jsonl).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be filed without invoking `gh`.",
    )
    args = parser.parse_args(argv)

    entries = vm.load_liveness_log(args.log_path)
    stale = vm.find_stale_states(entries)
    if not stale:
        print("No stale states detected.")
        return 0

    opened = 0
    skipped = 0
    for code, info in sorted(stale.items()):
        if args.dry_run:
            print(f"[dry-run] would file issue for {code}: {info}")
            continue
        if _existing_open_issue(code):
            print(f"Skip {code}: existing open stale-source issue.")
            skipped += 1
            continue
        _open_issue(code, info)
        print(f"Opened stale-source issue for {code}.")
        opened += 1

    print(f"\nDone. opened={opened} skipped={skipped} stale_total={len(stale)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
