#!/usr/bin/env python3
"""Reconcile ES/JA banks to be 1:1 derivations of the EN bank.

For each state, for each non-EN bank:
  - Drop ORPHAN questions (IDs present in target but not EN). These accumulated
    over time when add_sign_questions.py ran more than once on a translation,
    appending duplicate sign Qs with new IDs.
  - Report MISSING questions (IDs present in EN but not in target). These need
    re-translation via translate.py — this script doesn't make Gemini calls.

Usage:
    python3 tools/reconcile_translations.py             # all states, dry-run
    python3 tools/reconcile_translations.py --apply     # actually drop orphans
    python3 tools/reconcile_translations.py al fl --apply
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml
from _util import STATES_DIR


def reconcile_one(code: str, *, apply: bool) -> dict[str, dict[str, list[int] | bool]]:
    """Return a per-lang summary for state ``code``."""
    state_dir = Path(STATES_DIR) / code
    en_path = state_dir / "questions_en.yaml"
    if not en_path.exists():
        return {}
    with open(en_path) as f:
        en_data = yaml.safe_load(f) or {}
    en_ids = {q.get("id") for q in en_data.get("questions", []) if "id" in q}

    summary: dict[str, dict[str, list[int] | bool]] = {}
    for lang in ("es", "ja"):
        lang_path = state_dir / f"questions_{lang}.yaml"
        if not lang_path.exists():
            continue
        with open(lang_path) as f:
            tgt_data = yaml.safe_load(f) or {}
        tgt_questions = tgt_data.get("questions", [])
        tgt_ids = {q.get("id") for q in tgt_questions if "id" in q}
        orphans = sorted(tgt_ids - en_ids)
        missing = sorted(en_ids - tgt_ids)
        applied = False
        if orphans and apply:
            kept = [q for q in tgt_questions if q.get("id") in en_ids]
            tgt_data["questions"] = kept
            if "metadata" in tgt_data and "total_questions" in tgt_data["metadata"]:
                tgt_data["metadata"]["total_questions"] = len(kept)
            with open(lang_path, "w") as f:
                yaml.safe_dump(
                    tgt_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False
                )
            applied = True
        summary[lang] = {"orphans": orphans, "missing": missing, "applied": applied}
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("codes", nargs="*", help="State codes; defaults to all states")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually drop orphan IDs (default: dry-run, report only)",
    )
    args = parser.parse_args(argv)

    if args.codes:
        codes = [c.lower() for c in args.codes]
    else:
        codes = sorted(d for d in os.listdir(STATES_DIR) if (Path(STATES_DIR) / d).is_dir())

    total_orphans = 0
    total_missing = 0
    need_retranslate: list[tuple[str, str, int]] = []

    for code in codes:
        s = reconcile_one(code, apply=args.apply)
        for lang, info in s.items():
            orphan_ids = info["orphans"]
            missing_ids = info["missing"]
            assert isinstance(orphan_ids, list) and isinstance(missing_ids, list)
            if not orphan_ids and not missing_ids:
                continue
            verb = "dropped" if info["applied"] else "would drop"
            parts = []
            if orphan_ids:
                parts.append(
                    f"{verb} {len(orphan_ids)} orphan{'s' if len(orphan_ids) > 1 else ''}"
                )
                total_orphans += len(orphan_ids)
            if missing_ids:
                parts.append(f"{len(missing_ids)} MISSING (needs translate.py)")
                total_missing += len(missing_ids)
                need_retranslate.append((code, lang, len(missing_ids)))
            print(f"  {code} {lang}: {'; '.join(parts)}")

    print("\nsummary:")
    print(f"  total orphans across catalog: {total_orphans}")
    print(f"  total missing across catalog: {total_missing}")
    if need_retranslate:
        print("\nStates needing translate.py re-run:")
        for code, lang, n in need_retranslate:
            print(f"  python3 tools/translate.py {code} {lang}  # {n} missing IDs")
    if not args.apply and total_orphans:
        print("\n(dry-run — re-run with --apply to drop orphans)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
