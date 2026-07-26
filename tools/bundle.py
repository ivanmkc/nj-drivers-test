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

        states.append(
            {
                "code": state_code,
                "name": cfg["name"],
                "agency": cfg["agency"],
                "passing_score_pct": cfg["passing_score_pct"],
                "test_question_count": cfg["test_question_count"],
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
