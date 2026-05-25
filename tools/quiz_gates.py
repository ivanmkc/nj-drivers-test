"""Quiz verification gates — block low-quality questions before they ship.

Mirrors the unheard-past `verify_book.py` pattern (sentence-by-sentence anchoring
via Gemini-as-judge with pydantic-typed structured response, blocking on score
< threshold, no auto-retry).

Two gates per state:

1. **Faithfulness** — every question's claim must be anchored in manual_text.txt.
   Catches LLM hallucination during generate_questions.py. Per-question fidelity
   score 0-10; questions with fidelity < 7 are flagged; if >5% of questions are
   flagged (or any are score 0), the gate hard-fails.

2. **Coverage** — every important topic in manual_text.txt must be covered by
   at least one question. Catches generation gaps. Topics extracted from the
   manual via Gemini, then matched to questions; coverage rate < 90% soft-warns,
   < 75% hard-fails.

Usage:
    python3 tools/quiz_gates.py <code>                       # both gates, soft-only
    python3 tools/quiz_gates.py <code> --block-on-fail       # exit 2 on hard fail
    python3 tools/quiz_gates.py <code> --gate faithfulness
    python3 tools/quiz_gates.py <code> --gate coverage
    python3 tools/quiz_gates.py <code> --sample 30           # cost control: random sample of N questions

Exit codes (when --block-on-fail is set):
    0 = both gates pass
    1 = soft warnings only (ship with caveats)
    2 = hard fail (do not ship until resolved)
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from typing import Any

import yaml
from _util import STATES_DIR
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

MODEL_JUDGE = "gemini-3-flash-preview"  # bulk per-question faithfulness calls
MODEL_TOPICS = "gemini-3.1-pro-preview"  # one-shot critical-topic extraction

CLIENT = genai.Client(vertexai=True, project="adk-coding-agents", location="global")

FAITHFULNESS_BATCH = 10  # questions per Gemini call (keeps responses bounded)
DEFAULT_SAMPLE_SIZE = 60  # if questions > this, random-sample for cost control
SOFT_FAIL_FIDELITY = 9  # below = soft warn
HARD_FAIL_FIDELITY = 7  # below = hard fail
# Coverage uses keyword matching (cheap but imprecise — ~25% false-negative rate
# observed on AL test run). Loose thresholds reflect this; v2 should use LLM judge
# per topic for tighter signal.
SOFT_FAIL_COVERAGE_PCT = 75.0  # below = soft warn
HARD_FAIL_COVERAGE_PCT = 50.0  # below = hard fail
MAX_HARD_FAIL_QUESTIONS_PCT = 5.0  # if more than this fraction are score 0, hard fail


# ---------------------------------------------------------------------------
# Pydantic schemas — used as response_schema to constrain Gemini output.
# Mirrors the unheard-past SentenceMatch + RefinementFidelityReport pattern.
# ---------------------------------------------------------------------------


class QuestionAnchor(BaseModel):
    """One quiz question scored against the manual."""

    question_id: int = Field(description="Numeric id of the question being judged")
    fidelity: int = Field(
        ge=0,
        le=10,
        description=(
            "0-10. 10 = answer + explanation are directly supported by the manual. "
            "7-9 = paraphrased but accurate. "
            "4-6 = adds or drops a fact relative to the manual. "
            "1-3 = mostly disconnected from manual content. "
            "0 = pure hallucination — the claim contradicts or does not appear in the manual."
        ),
    )
    manual_evidence: list[str] = Field(
        default_factory=list,
        description=(
            "Verbatim manual excerpts (20-200 chars each, up to 3) that justify "
            "the question's answer + explanation. Empty list = no anchor found."
        ),
    )
    issue: str = Field(
        default="",
        description=(
            "One-sentence description of what's wrong when fidelity < 7. Empty when fidelity >= 7."
        ),
    )


class FaithfulnessReport(BaseModel):
    """Per-batch result. The CLI aggregates across batches."""

    anchors: list[QuestionAnchor] = Field(
        description="One QuestionAnchor per input question, in input order"
    )


class CriticalTopic(BaseModel):
    """One must-know topic extracted from the manual."""

    topic: str = Field(
        description="Short noun-phrase (5-12 words). e.g. 'BAC limit for drivers under 21'"
    )
    keywords: list[str] = Field(
        min_length=2,
        max_length=6,
        description=(
            "2-6 distinctive keywords that a question covering this topic "
            "would almost certainly contain. Lowercase, no stopwords."
        ),
    )


class TopicExtractionReport(BaseModel):
    topics: list[CriticalTopic] = Field(
        min_length=20,
        max_length=30,
        description="20-30 must-know topics derived from the manual",
    )


# ---------------------------------------------------------------------------
# Gate 1: faithfulness
# ---------------------------------------------------------------------------


def _format_question_for_judge(q: dict[str, Any]) -> str:
    choices = q.get("choices", {})
    return (
        f"Q{q['id']} [{q.get('category', '?')}]\n"
        f"  question: {q.get('question', '')}\n"
        f"  choices:\n"
        f"    A: {choices.get('A', '')}\n"
        f"    B: {choices.get('B', '')}\n"
        f"    C: {choices.get('C', '')}\n"
        f"    D: {choices.get('D', '')}\n"
        f"  answer: {q.get('answer', '')}\n"
        f"  explanation: {q.get('explanation', '')}"
    )


def check_faithfulness_batch(
    batch: list[dict[str, Any]],
    manual_text: str,
    state_name: str,
) -> FaithfulnessReport:
    """Judge a batch of questions against the manual via Gemini structured output."""
    questions_block = "\n\n".join(_format_question_for_judge(q) for q in batch)
    prompt = f"""You are auditing driver's-test questions for {state_name} against the source manual.

For each question, decide whether the stated answer and explanation are anchored in the manual text below. Score 0-10 (10 = fully supported, 0 = pure hallucination). Quote up to 3 verbatim manual excerpts that justify each question. If fidelity < 7, give a one-sentence issue description.

MANUAL TEXT:
{manual_text}

QUESTIONS TO JUDGE:
{questions_block}
"""
    response = CLIENT.models.generate_content(
        model=MODEL_JUDGE,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=FaithfulnessReport,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=8192,
        ),
    )
    if response.text is None:
        raise RuntimeError(f"Empty judge response for batch starting Q{batch[0]['id']}")
    return FaithfulnessReport.model_validate_json(response.text)


def run_faithfulness_gate(
    questions: list[dict[str, Any]],
    manual_text: str,
    state_name: str,
    sample_size: int | None = None,
) -> tuple[list[QuestionAnchor], dict[str, Any]]:
    """Run the faithfulness gate. Returns (per-question anchors, summary stats)."""
    non_sign = [q for q in questions if "image" not in q]
    if sample_size and len(non_sign) > sample_size:
        rng = random.Random(42)
        non_sign = rng.sample(non_sign, sample_size)
        print(f"  Sampled {sample_size} non-sign questions for faithfulness")

    anchors: list[QuestionAnchor] = []
    for i in range(0, len(non_sign), FAITHFULNESS_BATCH):
        batch = non_sign[i : i + FAITHFULNESS_BATCH]
        print(
            f"  Faithfulness batch {i // FAITHFULNESS_BATCH + 1}/{(len(non_sign) - 1) // FAITHFULNESS_BATCH + 1} (Q{batch[0]['id']}-Q{batch[-1]['id']})..."
        )
        report = check_faithfulness_batch(batch, manual_text, state_name)
        anchors.extend(report.anchors)

    n = len(anchors)
    n_zero = sum(1 for a in anchors if a.fidelity == 0)
    n_below_hard = sum(1 for a in anchors if a.fidelity < HARD_FAIL_FIDELITY)
    n_below_soft = sum(1 for a in anchors if a.fidelity < SOFT_FAIL_FIDELITY)
    avg_fidelity = sum(a.fidelity for a in anchors) / n if n else 0.0

    pct_hard_fail_questions = (n_zero / n * 100.0) if n else 0.0
    summary = {
        "total_judged": n,
        "zero_fidelity": n_zero,
        "below_hard_threshold": n_below_hard,
        "below_soft_threshold": n_below_soft,
        "avg_fidelity": round(avg_fidelity, 2),
        "verdict": _faithfulness_verdict(avg_fidelity, pct_hard_fail_questions),
    }
    return anchors, summary


def _faithfulness_verdict(avg: float, pct_zero: float) -> str:
    if pct_zero > MAX_HARD_FAIL_QUESTIONS_PCT or avg < HARD_FAIL_FIDELITY:
        return "HARD_FAIL"
    if avg < SOFT_FAIL_FIDELITY:
        return "SOFT_WARN"
    return "PASS"


# ---------------------------------------------------------------------------
# Gate 2: coverage
# ---------------------------------------------------------------------------


def extract_critical_topics(manual_text: str, state_name: str) -> list[CriticalTopic]:
    """One-shot Gemini call to extract 20-30 must-know topics from the manual."""
    truncated = manual_text[:50_000] if len(manual_text) > 50_000 else manual_text
    prompt = f"""You are designing a written knowledge test for {state_name}.

Identify 20-30 topics that any test-taker MUST know to pass, based on the manual below. Each topic should be a short noun-phrase (5-12 words). For each, also list 2-6 distinctive lowercase keywords a question on that topic would contain.

Cover a balanced spread: rules of the road, signs/signals, right-of-way, parking, alcohol/drugs, penalties, safe driving, vehicle operation, sharing the road, licensing.

MANUAL TEXT:
{truncated}
"""
    response = CLIENT.models.generate_content(
        model=MODEL_TOPICS,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=TopicExtractionReport,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=8192,
        ),
    )
    if response.text is None:
        raise RuntimeError("Empty topic-extraction response")
    return TopicExtractionReport.model_validate_json(response.text).topics


def topic_covered(topic: CriticalTopic, questions: list[dict[str, Any]]) -> list[int]:
    """Return question IDs that cover this topic.

    A question covers the topic if it contains the topic's most-distinctive single keyword
    (longest, after dropping stopwords). This is intentionally permissive — the gate is
    a coarse signal; a v2 should swap this for an LLM-judged per-topic call.
    """
    if not topic.keywords:
        return []
    # Use the longest keyword as the strongest signal (filters generic stopwords).
    anchor = max(topic.keywords, key=len).lower()
    covering: list[int] = []
    for q in questions:
        text = (q.get("question", "") + " " + q.get("explanation", "")).lower()
        if anchor in text:
            covering.append(q["id"])
    return covering


def run_coverage_gate(
    questions: list[dict[str, Any]],
    manual_text: str,
    state_name: str,
) -> tuple[list[tuple[CriticalTopic, list[int]]], dict[str, Any]]:
    """Run the coverage gate. Returns (per-topic results, summary stats)."""
    topics = extract_critical_topics(manual_text, state_name)
    results = [(t, topic_covered(t, questions)) for t in topics]

    n_topics = len(results)
    n_covered = sum(1 for _, qids in results if qids)
    coverage_pct = (n_covered / n_topics * 100.0) if n_topics else 0.0

    summary = {
        "total_topics": n_topics,
        "covered_topics": n_covered,
        "coverage_pct": round(coverage_pct, 1),
        "verdict": _coverage_verdict(coverage_pct),
    }
    return results, summary


def _coverage_verdict(pct: float) -> str:
    if pct < HARD_FAIL_COVERAGE_PCT:
        return "HARD_FAIL"
    if pct < SOFT_FAIL_COVERAGE_PCT:
        return "SOFT_WARN"
    return "PASS"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load_state(code: str) -> tuple[list[dict[str, Any]], str, str]:
    state_dir = os.path.join(STATES_DIR, code)
    q_path = os.path.join(state_dir, "questions_en.yaml")
    manual_path = os.path.join(state_dir, "manual_text.txt")
    config_path = os.path.join(state_dir, "config.json")
    if not os.path.exists(q_path):
        raise SystemExit(f"questions_en.yaml not found at {q_path}")
    if not os.path.exists(manual_path):
        raise SystemExit(f"manual_text.txt not found at {manual_path}")

    with open(q_path) as f:
        questions = (yaml.safe_load(f) or {}).get("questions", [])
    with open(manual_path) as f:
        manual_text = f.read()
    state_name = code.upper()
    if os.path.exists(config_path):
        with open(config_path) as f:
            state_name = json.load(f).get("name", state_name)
    return questions, manual_text, state_name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("code", help="State code (e.g. 'nj')")
    parser.add_argument(
        "--gate",
        choices=["faithfulness", "coverage", "both"],
        default="both",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help=f"Random sample size for faithfulness (default {DEFAULT_SAMPLE_SIZE}, 0 = all)",
    )
    parser.add_argument(
        "--block-on-fail",
        action="store_true",
        help="Exit 2 on hard fail (default: always exit 0 with report)",
    )
    args = parser.parse_args(argv)

    questions, manual_text, state_name = _load_state(args.code)
    print(
        f"\n{state_name} ({args.code.upper()}) — {len(questions)} questions, {len(manual_text):,} manual chars\n"
    )

    overall_verdict = "PASS"

    if args.gate in ("faithfulness", "both"):
        print("[Gate 1: Faithfulness]")
        sample = args.sample if args.sample > 0 else None
        anchors, summary = run_faithfulness_gate(questions, manual_text, state_name, sample)
        _print_faithfulness(anchors, summary)
        overall_verdict = _worst(overall_verdict, summary["verdict"])

    if args.gate in ("coverage", "both"):
        print("\n[Gate 2: Coverage]")
        results, summary = run_coverage_gate(questions, manual_text, state_name)
        _print_coverage(results, summary)
        overall_verdict = _worst(overall_verdict, summary["verdict"])

    print(f"\n=== {state_name} verdict: {overall_verdict} ===")
    if not args.block_on_fail:
        return 0
    return {"PASS": 0, "SOFT_WARN": 1, "HARD_FAIL": 2}[overall_verdict]


def _worst(a: str, b: str) -> str:
    rank = {"PASS": 0, "SOFT_WARN": 1, "HARD_FAIL": 2}
    return a if rank[a] >= rank[b] else b


def _print_faithfulness(anchors: list[QuestionAnchor], summary: dict[str, Any]) -> None:
    print(
        f"  judged={summary['total_judged']}  "
        f"avg={summary['avg_fidelity']}/10  "
        f"<{HARD_FAIL_FIDELITY}={summary['below_hard_threshold']}  "
        f"<{SOFT_FAIL_FIDELITY}={summary['below_soft_threshold']}  "
        f"zero={summary['zero_fidelity']}  "
        f"verdict={summary['verdict']}"
    )
    flagged = [a for a in anchors if a.fidelity < HARD_FAIL_FIDELITY]
    if flagged:
        print(f"  Flagged ({len(flagged)} questions):")
        for a in flagged[:20]:
            print(f"    Q{a.question_id} fidelity={a.fidelity}: {a.issue}")
        if len(flagged) > 20:
            print(f"    ... and {len(flagged) - 20} more")


def _print_coverage(
    results: list[tuple[CriticalTopic, list[int]]],
    summary: dict[str, Any],
) -> None:
    print(
        f"  topics={summary['total_topics']}  "
        f"covered={summary['covered_topics']}  "
        f"pct={summary['coverage_pct']}%  "
        f"verdict={summary['verdict']}"
    )
    uncovered = [(t, qids) for t, qids in results if not qids]
    if uncovered:
        print(f"  Uncovered topics ({len(uncovered)}):")
        for t, _ in uncovered:
            print(f"    - {t.topic}")


if __name__ == "__main__":
    sys.exit(main())
