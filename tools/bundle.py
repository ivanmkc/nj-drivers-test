#!/usr/bin/env python3
"""Build questions_bundle.json.gz from states/ directory and copy to app assets."""

import gzip
import json
import os
import re
import shutil

import yaml
from _util import ROOT_DIR, STATES_DIR

SIGNS_DIR = os.path.join(ROOT_DIR, "data", "signs")
SHARED_DIR = os.path.join(ROOT_DIR, "shared")
IOS_RESOURCES = os.path.join(ROOT_DIR, "ios", "DriversTest", "DriversTest", "Resources")
ANDROID_ASSETS = os.path.join(ROOT_DIR, "android", "app", "src", "main", "assets")

# Trust metadata shipped with each state: per-question manual excerpts are
# capped so the bundle doesn't balloon (2 quotes x 220 chars ~= +1.9 MB raw).
MAX_EVIDENCE_QUOTES = 2
MAX_EVIDENCE_CHARS = 220


def load_trust_meta(state_dir: str) -> tuple[dict | None, dict[str, list[str]]]:
    """Return (verification summary, evidence-by-question-id) from a state's report.

    Returns (None, {}) when the state has no verification_report.json.
    """
    report_path = os.path.join(state_dir, "verification_report.json")
    if not os.path.exists(report_path):
        return None, {}
    with open(report_path) as f:
        report = json.load(f)
    precision = report.get("precision") or {}
    recall = report.get("recall") or {}
    source = report.get("source") or {}
    translations = report.get("translation") or {}
    summary = {
        "verified_at": report.get("verified_at"),
        "overall": report.get("overall_verdict"),
        "manual_url": source.get("manual_url"),
        "edition": source.get("edition") or None,
        "manual_pages": source.get("manual_pages"),
        "precision_avg_fidelity": precision.get("avg_fidelity"),
        "precision_grade": precision.get("grade"),
        "questions_judged": precision.get("judged_count"),
        "recall_coverage_pct": recall.get("coverage_pct"),
        "translations": {lang: t.get("verdict") for lang, t in translations.items()},
    }
    evidence = {}
    for qid, quotes in (precision.get("evidence_by_question_id") or {}).items():
        capped = [q[:MAX_EVIDENCE_CHARS] for q in quotes[:MAX_EVIDENCE_QUOTES] if q.strip()]
        if capped:
            evidence[qid] = capped
    return summary, evidence


def build_bundle():
    states = []

    for state_code in sorted(os.listdir(STATES_DIR)):
        state_dir = os.path.join(STATES_DIR, state_code)
        if not os.path.isdir(state_dir):
            continue
        config_path = os.path.join(state_dir, "config.json")
        if not os.path.exists(config_path):
            continue

        with open(config_path) as f:
            cfg = json.load(f)

        langs = {}
        for fname in sorted(os.listdir(state_dir)):
            match = re.match(r"questions_(\w+)\.yaml$", fname)
            if not match:
                continue
            lang = match.group(1)
            with open(os.path.join(state_dir, fname)) as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict) or "questions" not in data:
                raise ValueError(
                    f"{state_code}/{fname}: expected a mapping with a 'questions' key, "
                    f"got {type(data).__name__}"
                )
            langs[lang] = data["questions"]

        verification, evidence = load_trust_meta(state_dir)

        # Category breakdown from the EN bank; evidence excerpts attach to EN
        # questions only — other languages look the excerpt up by question id.
        categories: dict[str, int] = {}
        for q in langs.get("en", []):
            categories[q["category"]] = categories.get(q["category"], 0) + 1
            quotes = evidence.get(str(q.get("id")))
            if quotes:
                q["evidence"] = quotes

        states.append(
            {
                "code": state_code,
                "name": cfg["name"],
                "agency": cfg["agency"],
                "passing_score_pct": cfg["passing_score_pct"],
                "test_question_count": cfg["test_question_count"],
                "source": cfg.get("source"),
                "categories": categories,
                "verification": verification,
                "languages": langs,
            }
        )

    return {"states": states}


def write_bundle(bundle):
    os.makedirs(SHARED_DIR, exist_ok=True)
    json_path = os.path.join(SHARED_DIR, "questions_bundle.json")
    gz_path = os.path.join(SHARED_DIR, "questions_bundle.json.gz")

    json_bytes = json.dumps(bundle, separators=(",", ":")).encode()
    with open(json_path, "wb") as f:
        f.write(json_bytes)
    with gzip.open(gz_path, "wb") as f:
        f.write(json_bytes)

    print(f"  {json_path} ({len(json_bytes) / 1024 / 1024:.1f} MB)")
    print(f"  {gz_path} ({os.path.getsize(gz_path) / 1024 / 1024:.1f} MB)")


def copy_to_apps():
    gz_src = os.path.join(SHARED_DIR, "questions_bundle.json.gz")

    for dest_dir in [IOS_RESOURCES, ANDROID_ASSETS]:
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(gz_src, os.path.join(dest_dir, "questions_bundle.json.gz"))
        print(f"  Copied bundle -> {dest_dir}")

        # Copy sign images
        dest_signs = os.path.join(dest_dir, "signs")
        if os.path.isdir(SIGNS_DIR):
            if os.path.isdir(dest_signs):
                shutil.rmtree(dest_signs)
            shutil.copytree(SIGNS_DIR, dest_signs)
            count = len([f for f in os.listdir(dest_signs) if f.endswith(".png")])
            print(f"  Copied {count} sign images -> {dest_signs}")


if __name__ == "__main__":
    print("Building bundle...")
    bundle = build_bundle()
    total_langs = sum(len(s["languages"]) for s in bundle["states"])
    print(f"  {len(bundle['states'])} states, {total_langs} language files")
    write_bundle(bundle)
    print("Copying to apps...")
    copy_to_apps()
    print("Done.")
