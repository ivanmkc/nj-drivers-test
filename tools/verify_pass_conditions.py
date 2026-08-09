#!/usr/bin/env python3
"""Verify each state's pass conditions (passing_score_pct, test_question_count)
against its own manual text.

config.json pass conditions were originally filled during onboarding (Gemini
search) and are otherwise unverified — the quiz gates verify questions, not
config metadata. Many official manuals state the knowledge-test format
explicitly ("The test has 25 questions; you must answer 20 correctly"). This
tool extracts what the manual actually says (with verbatim evidence) and
diffs it against config.json.

Usage:
    python3 tools/verify_pass_conditions.py            # all states, report only
    python3 tools/verify_pass_conditions.py nj ca      # subset
    python3 tools/verify_pass_conditions.py --json out.json
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

# Keywords that mark passages likely to describe the knowledge-test format.
KEYWORDS = re.compile(
    r"knowledge test|written test|knowledge exam|written exam|multiple.choice|"
    r"questions on the|test consists|must answer|answer.{0,30}correctly|"
    r"passing score|correct answers|to pass the",
    re.IGNORECASE,
)
CONTEXT_LINES = 4
MAX_SNIPPET_CHARS = 15_000


class PassConditions(BaseModel):
    """What the manual states about the knowledge-test format."""

    stated: bool = Field(
        description=(
            "True only if the excerpts EXPLICITLY state the number of test "
            "questions and/or the passing requirement. False if silent or vague."
        )
    )
    question_count: int | None = Field(
        default=None, description="Number of questions on the knowledge test, if stated"
    )
    passing_count: int | None = Field(
        default=None, description="Number of correct answers required to pass, if stated"
    )
    passing_pct: int | None = Field(
        default=None, description="Passing score percentage, if stated as a percent"
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Verbatim excerpts (up to 3, <=200 chars) stating the test format",
    )


def candidate_snippets(manual_text: str) -> str:
    """Concatenate keyword-hit passages with surrounding context."""
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


def extract(state_name: str, snippets: str) -> PassConditions:
    prompt = f"""These are excerpts from the official {state_name} driver manual.

Determine what the manual EXPLICITLY states about the written knowledge test format:
how many questions it has, and what is required to pass (a count of correct answers
and/or a percentage). Only report values the text actually states — do not infer
from general knowledge, and do not confuse practice-quiz or CDL/motorcycle test
formats with the standard (Class D / non-commercial) knowledge test.

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
                response_schema=PassConditions,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                max_output_tokens=4096,
            ),
        )
    )
    if response.text is None:
        raise RuntimeError(f"Empty response for {state_name}")
    return PassConditions.model_validate_json(response.text)


def check_state(code: str) -> dict:
    state_dir = os.path.join(STATES_DIR, code)
    config_path = os.path.join(state_dir, "config.json")
    manual_path = os.path.join(state_dir, "manual_text.txt")
    with open(config_path) as f:
        cfg = json.load(f)
    result: dict = {
        "code": code,
        "config_pct": cfg["passing_score_pct"],
        "config_count": cfg["test_question_count"],
    }
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
    if not found.stated:
        result["status"] = "NOT_STATED"
        return result

    # Derive a percent when the manual gives counts ("20 of 25 correctly").
    derived_pct = found.passing_pct
    if derived_pct is None and found.passing_count and found.question_count:
        derived_pct = round(100 * found.passing_count / found.question_count)

    issues = []
    if found.question_count is not None and found.question_count != cfg["test_question_count"]:
        issues.append(
            f"count: config {cfg['test_question_count']} vs manual {found.question_count}"
        )
    if derived_pct is not None and abs(derived_pct - cfg["passing_score_pct"]) > 1:
        issues.append(f"pct: config {cfg['passing_score_pct']} vs manual {derived_pct}")
    result["derived_pct"] = derived_pct
    result["status"] = "MISMATCH" if issues else "MATCH"
    result["issues"] = issues
    return result


def main() -> None:
    argv = sys.argv[1:]
    json_out = None
    if "--json" in argv:
        i = argv.index("--json")
        json_out = argv[i + 1]
        argv = argv[:i] + argv[i + 2 :]
    args = [a for a in argv if not a.startswith("--")]
    codes = args or sorted(
        d
        for d in os.listdir(STATES_DIR)
        if os.path.exists(os.path.join(STATES_DIR, d, "config.json"))
    )
    results = []
    for code in codes:
        r = check_state(code)
        results.append(r)
        detail = "; ".join(r.get("issues", [])) or r.get("status")
        print(
            f"{code:4} {r['status']:14} {detail if r['status'] == 'MISMATCH' else ''}", flush=True
        )

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
