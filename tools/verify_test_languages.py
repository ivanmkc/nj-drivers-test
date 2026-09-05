#!/usr/bin/env python3
"""Extract which languages each state's OFFICIAL knowledge test is offered in.

The app lets users practice in any bundled language (en/es/ja/fr), but that is
not a claim about the real DMV test — some states offer the knowledge test in
30+ languages, others in English only. This tool extracts what each manual
explicitly states (with verbatim evidence) so the UI can label app languages
as "usable on the official test" vs "practice only", and say nothing where
the manual is silent.

Usage:
    python3 tools/verify_test_languages.py                    # report only
    python3 tools/verify_test_languages.py --apply            # write config.json
    python3 tools/verify_test_languages.py nj ca --json out.json
"""

from __future__ import annotations

import json
import os
import re
import sys

from _util import STATES_DIR, retry_with_backoff
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

MODEL = "gemini-3-flash-preview"
CLIENT = genai.Client(vertexai=True, project="adk-coding-agents", location="global")

KEYWORDS = re.compile(
    r"language|interpreter|translat|english only|en español|bilingual|"
    r"offered in|available in|audio (?:version|test)|oral test",
    re.IGNORECASE,
)
CONTEXT_LINES = 4
MAX_SNIPPET_CHARS = 15_000


class TestLanguages(BaseModel):
    """What the manual states about knowledge-test language availability."""

    stated: bool = Field(
        description=(
            "True only if the excerpts EXPLICITLY state which language(s) the "
            "official knowledge test is offered in, or explicitly mention "
            "interpreter/translation policy for the test. False if silent."
        )
    )
    languages: list[str] = Field(
        default_factory=list,
        description=(
            "English names of languages the official knowledge test is stated to be "
            "available in (e.g. ['English', 'Spanish']). Use ['many'] only if the "
            "manual says the test is offered in many/multiple languages without "
            "listing them."
        ),
    )
    interpreter_allowed: bool | None = Field(
        default=None,
        description="True/False only if the manual explicitly addresses interpreter use",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Verbatim excerpts (up to 3, <=250 chars) supporting the answer",
    )


def candidate_snippets(manual_text: str) -> str:
    lines = manual_text.splitlines()
    keep: set[int] = set()
    for i, line in enumerate(lines):
        if KEYWORDS.search(line):
            keep.update(range(max(0, i - CONTEXT_LINES), min(len(lines), i + CONTEXT_LINES + 1)))
    out: list[str] = []
    prev = -2
    for i in sorted(keep):
        if i != prev + 1:
            out.append("…")
        out.append(lines[i])
        prev = i
    return "\n".join(out)[:MAX_SNIPPET_CHARS]


def extract(state_name: str, snippets: str) -> TestLanguages:
    prompt = f"""These are excerpts from the official {state_name} driver manual.

Determine what the manual EXPLICITLY states about which language(s) the official
written knowledge test can be taken in, and whether interpreters are addressed.
Only report what the text states — do not infer from general knowledge. Ignore
statements about the manual/handbook itself being available in other languages;
only the TEST's language availability counts.

EXCERPTS:
{snippets}
"""
    response = retry_with_backoff(
        lambda: CLIENT.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=TestLanguages,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                max_output_tokens=4096,
            ),
        )
    )
    if response.text is None:
        raise RuntimeError(f"Empty response for {state_name}")
    return TestLanguages.model_validate_json(response.text)


def check_state(code: str, *, apply: bool) -> dict:
    state_dir = os.path.join(STATES_DIR, code)
    config_path = os.path.join(state_dir, "config.json")
    manual_path = os.path.join(state_dir, "manual_text.txt")
    with open(config_path) as f:
        cfg = json.load(f)
    result: dict = {"code": code}
    if not os.path.exists(manual_path):
        result["status"] = "NO_MANUAL_TEXT"
        return result

    with open(manual_path) as f:
        snippets = candidate_snippets(f.read())
    if not snippets.strip("…\n "):
        result["status"] = "NOT_STATED"
        return result

    found = extract(cfg["name"], snippets)
    result["manual"] = found.model_dump()
    result["status"] = "STATED" if found.stated else "NOT_STATED"

    if apply:
        if found.stated and found.languages:
            cfg["official_test_languages"] = found.languages
            cfg["official_test_languages_evidence"] = found.evidence[:2]
        else:
            cfg.pop("official_test_languages", None)
            cfg.pop("official_test_languages_evidence", None)
        with open(config_path, "w") as f:
            json.dump(cfg, f, indent=2)
            f.write("\n")
        result["applied"] = found.stated and bool(found.languages)
    return result


def main() -> None:
    argv = sys.argv[1:]
    json_out = None
    if "--json" in argv:
        i = argv.index("--json")
        json_out = argv[i + 1]
        argv = argv[:i] + argv[i + 2 :]
    apply = "--apply" in argv
    args = [a for a in argv if not a.startswith("--")]
    codes = args or sorted(
        d
        for d in os.listdir(STATES_DIR)
        if os.path.exists(os.path.join(STATES_DIR, d, "config.json"))
    )
    results = []
    for code in codes:
        r = check_state(code, apply=apply)
        results.append(r)
        langs = (r.get("manual") or {}).get("languages") or []
        print(f"{code:4} {r['status']:12} {', '.join(langs)}", flush=True)

    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"\nsummary: {counts}")
    if json_out:
        with open(json_out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"details -> {json_out}")


if __name__ == "__main__":
    main()
