#!/usr/bin/env python3
"""Set up a new state: download manual, extract text, create config, generate questions.

Usage (per-state CLI form, unchanged):
    python3 tools/setup_state.py <code> <name> <agency> <pass_pct> <test_count> <manual_url> [source_desc]

Catalog-driven form (looks up everything in tools/manual_urls.json by code):
    python3 tools/setup_state.py --from-catalog <code>

Example:
    python3 tools/setup_state.py ca "California" "DMV" 83 46 \
        "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/" \
        "2025 California Driver Handbook"

When the resolved catalog entry has a non-empty ``urls`` list (multi-PDF
manual), each URL is downloaded in declared order and concatenated. When
``manual_url`` is HTML and ``urls`` is absent, the page is scraped via
BeautifulSoup. Single-PDF behavior is identical to the pre-change pipeline.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any

from _manual_fetch import assemble_manual_text
from _util import cache_path


def _resolve_entry(argv: list[str]) -> dict[str, Any]:
    """Parse argv into a catalog-shaped entry dict."""
    if len(argv) >= 3 and argv[1] == "--from-catalog":
        code = argv[2].lower()
        catalog_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual_urls.json")
        with open(catalog_path) as f:
            data = json.load(f)
        for raw in data:
            if isinstance(raw, dict) and raw.get("code", "").lower() == code:
                return dict(raw)
        raise SystemExit(f"No catalog entry found for code={code!r} in {catalog_path}")

    if len(argv) < 7:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    code = argv[1].lower()
    return {
        "code": code,
        "name": argv[2],
        "agency": argv[3],
        "passing_score_pct": int(argv[4]),
        "test_question_count": int(argv[5]),
        "manual_url": argv[6],
        "source_description": (argv[7] if len(argv) > 7 else f"2025 {argv[2]} Driver's Manual"),
    }


def _write_config(state_dir: str, entry: dict[str, Any]) -> str:
    """Materialize ``data/states/<code>/config.json`` from the entry."""
    os.makedirs(state_dir, exist_ok=True)
    config = {
        "code": entry["code"],
        "name": entry["name"],
        "agency": entry["agency"],
        "manual_url": entry.get("manual_url", ""),
        "passing_score_pct": int(entry["passing_score_pct"]),
        "test_question_count": int(entry["test_question_count"]),
        "source": entry.get("source_description") or entry.get("source") or entry["name"],
    }
    config_path = os.path.join(state_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    print(f"Created {config_path}")
    return config_path


def main() -> None:
    entry = _resolve_entry(sys.argv)
    code = entry["code"]
    name = entry["name"]

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state_dir = os.path.join(base_dir, "data", "states", code)
    _write_config(state_dir, entry)

    # Download + extract manual text.
    manual_text_path = cache_path(f"{code}_manual_text.txt")
    print(f"\nResolving manual text for {name} ({code})...")
    assemble_manual_text(entry, manual_text_path)

    # Generate questions if not already present.
    questions_path = os.path.join(state_dir, "questions_en.yaml")
    if not os.path.exists(questions_path):
        print(f"\nGenerating questions for {name}...")
        subprocess.run(
            [
                sys.executable,
                os.path.join(base_dir, "tools", "generate_questions.py"),
                code,
                manual_text_path,
            ],
            check=True,
        )
    else:
        print(f"Questions already exist: {questions_path}")

    # Add sign questions.
    print("\nAdding sign questions...")
    subprocess.run(
        [sys.executable, os.path.join(base_dir, "tools", "add_sign_questions.py"), code],
        check=True,
    )

    # Translate.
    translate_script = os.path.join(base_dir, "tools", "translate.py")
    for lang in ["es"]:
        lang_path = os.path.join(state_dir, f"questions_{lang}.yaml")
        if not os.path.exists(lang_path):
            print(f"\nTranslating to {lang}...")
            subprocess.run([sys.executable, translate_script, code, lang], check=True)
        else:
            print(f"Translation already exists: {lang_path}")

    print(f"\n=== {name} ({code.upper()}) setup complete! ===")


if __name__ == "__main__":
    main()
