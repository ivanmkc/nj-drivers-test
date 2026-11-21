#!/usr/bin/env python3
"""Stop a release when a source/manual review remains explicitly unresolved."""

import json
from pathlib import Path

from _util import STATES_DIR


def pending_reviews(states_dir: str | Path = STATES_DIR) -> list[tuple[str, str]]:
    pending = []
    for path in sorted(Path(states_dir).glob("*/config.json")):
        config = json.loads(path.read_text())
        if config.get("content_review_required"):
            pending.append(
                (config["code"], config.get("content_review_note", "Content review pending"))
            )
    return pending


def main() -> int:
    pending = pending_reviews()
    for code, note in pending:
        print(f"::error::{code.upper()}: {note}")
    if pending:
        print(
            "Refresh and verify the affected banks, record evidence, then clear their review flags."
        )
        return 1
    print("No explicit content-review blockers. This is not proof of complete source freshness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
