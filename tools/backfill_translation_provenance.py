#!/usr/bin/env python3
"""Backfill translation provenance (en_source_sha256) for pre-#59 translated banks.

Older ES/JA banks were generated before translate.py recorded provenance, so
audit_questions.py flags them ("no translation provenance"). Re-translating ~100
clean banks just to stamp a hash would risk introducing new drift; instead, this
script stamps the hash of the *current* questions_en.yaml onto banks that the
verification pipeline has already judged faithful to that same EN content.

A bank is only stamped when ALL of these hold:
  1. metadata.translation.en_source_sha256 is absent (never overwrite a real stamp);
  2. the state's verification_report.json translation gate for that language is PASS;
  3. questions_en.yaml has not been modified (per git) since the report's
     verified_at timestamp — otherwise the PASS verdict may not describe the
     current EN content, and the bank must be re-translated instead.

Usage:
    python3 tools/backfill_translation_provenance.py            # apply
    python3 tools/backfill_translation_provenance.py --dry-run  # report only
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import yaml
from _util import STATES_DIR, questions_path, resolve_state_paths


def _en_last_commit_time(en_path: str) -> datetime | None:
    """Return the committer time of the last commit touching *en_path*, or None."""
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", en_path],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if not out:
        return None
    return datetime.fromisoformat(out)


def backfill_state(code: str, *, dry_run: bool) -> list[str]:
    """Stamp eligible banks for one state. Returns human-readable action lines."""
    actions: list[str] = []
    paths = resolve_state_paths(code)
    en_path = paths["questions_en_path"]
    report_path = os.path.join(STATES_DIR, code, "verification_report.json")
    if not os.path.exists(en_path) or not os.path.exists(report_path):
        return actions

    with open(report_path) as f:
        report = json.load(f)
    translation_gates = report.get("translation") or {}
    verified_at_raw = report.get("verified_at", "")
    try:
        verified_at = datetime.fromisoformat(verified_at_raw.replace("Z", "+00:00"))
    except ValueError:
        actions.append(f"{code}: SKIP — unparseable verified_at {verified_at_raw!r}")
        return actions

    with open(en_path, "rb") as f:
        en_sha256 = hashlib.sha256(f.read()).hexdigest()

    for lang in ("es", "ja"):
        lang_path = questions_path(code, lang)
        if not os.path.exists(lang_path):
            continue
        with open(lang_path) as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict) or "questions" not in data:
            actions.append(f"{code}/{lang}: SKIP — malformed YAML")
            continue
        metadata = data.setdefault("metadata", {})
        existing = (metadata.get("translation") or {}).get("en_source_sha256")
        if existing:
            continue  # already stamped (e.g. by a fresh translate.py run)

        gate = translation_gates.get(lang) or {}
        if gate.get("verdict") != "PASS":
            actions.append(
                f"{code}/{lang}: SKIP — translation gate verdict is "
                f"{gate.get('verdict') or 'missing'}; re-translate instead"
            )
            continue

        en_committed = _en_last_commit_time(en_path)
        if en_committed is not None and en_committed > verified_at:
            actions.append(
                f"{code}/{lang}: SKIP — questions_en.yaml changed after report "
                f"({en_committed.isoformat()} > {verified_at.isoformat()}); re-translate"
            )
            continue

        metadata["translation"] = {
            "backfilled_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "method": (
                "provenance backfill — bank verified against this EN content by the "
                "quiz_gates translation gate (verdict PASS)"
            ),
            "en_source_sha256": en_sha256,
        }
        if not dry_run:
            with open(lang_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        actions.append(f"{code}/{lang}: stamped {en_sha256[:12]}…")
    return actions


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    stamped = 0
    skipped = 0
    for code in sorted(os.listdir(STATES_DIR)):
        if not os.path.isdir(os.path.join(STATES_DIR, code)):
            continue
        for line in backfill_state(code, dry_run=dry_run):
            print(("[dry-run] " if dry_run else "") + line)
            if "stamped" in line:
                stamped += 1
            else:
                skipped += 1
    print(f"\n{stamped} banks stamped, {skipped} skipped{' (dry run)' if dry_run else ''}")


if __name__ == "__main__":
    main()
