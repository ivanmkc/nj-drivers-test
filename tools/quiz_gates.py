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
DEFAULT_SAMPLE_SIZE = 0  # 0 = judge every non-sign question (#59 item 2). >0 dev override only.
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


class TopicCoverageJudgment(BaseModel):
    """LLM judgment for one topic against the question bank."""

    topic: str = Field(description="The topic being judged, verbatim from input")
    is_covered: bool = Field(
        description=(
            "True if at least one question in the bank tests this topic with adequate "
            "depth (asks the test-taker to know a key fact about the topic). False if "
            "the topic is unaddressed or only mentioned tangentially."
        )
    )
    covering_question_ids: list[int] = Field(
        default_factory=list,
        max_length=5,
        description="Up to 5 question IDs that test this topic (empty if not covered)",
    )
    note: str = Field(
        default="",
        description="One-sentence explanation (especially when is_covered=False)",
    )


class TopicCoverageReport(BaseModel):
    judgments: list[TopicCoverageJudgment] = Field(
        description="One judgment per input topic, in input order"
    )


# ---------------------------------------------------------------------------
# Top-level structured report — saved to data/states/<code>/verification_report.json
# ---------------------------------------------------------------------------


class SourceInfo(BaseModel):
    manual_url: str
    manual_pdf_sha256: str | None = None
    manual_text_sha256: str | None = None
    manual_text_chars: int
    manual_pages: int | None = None
    edition: str | None = None


class BankInfo(BaseModel):
    total_questions: int
    non_sign_questions: int
    sign_questions: int
    languages: list[str]


class PrecisionMetric(BaseModel):
    """Faithfulness gate output."""

    method: str = (
        "Gemini-3-flash-as-judge with structured pydantic response, batched per 10 questions"
    )
    sample_size: int
    judged_count: int
    avg_fidelity: float
    pct_at_10: float
    pct_above_9: float
    pct_above_7: float
    pct_zero: float
    flagged_question_ids: list[int]
    # Verbatim manual excerpts (≤3 each, 20-200 chars) keyed by question id (as str).
    # Per #59 item 1: persisted so reviewers can audit the per-question source trail.
    evidence_by_question_id: dict[str, list[str]] = Field(default_factory=dict)
    verdict: str  # PASS | SOFT_WARN | HARD_FAIL
    grade: str  # A-F


class TranslationAnchor(BaseModel):
    """One translation pair (EN ↔ target) scored for faithfulness."""

    question_id: int = Field(description="Numeric id of the question pair being judged")
    fidelity: int = Field(
        ge=0,
        le=10,
        description=(
            "0-10. 10 = translation preserves meaning, answer letter, and explanation facts "
            "exactly. 7-9 = natural rendering with negligible drift. 4-6 = adds or drops a fact, "
            "softens a directive, or changes nuance. 1-3 = wrong answer or substantive drift. "
            "0 = mistranslated or fabricated."
        ),
    )
    issue: str = Field(
        default="",
        description="One-sentence description of the drift when fidelity < 7. Empty otherwise.",
    )


class TranslationFaithfulnessReport(BaseModel):
    """Per-batch translation-judge result."""

    anchors: list[TranslationAnchor] = Field(
        description="One TranslationAnchor per input pair, in input order"
    )


class TranslationMetric(BaseModel):
    """Translation-faithfulness gate output for one target language."""

    method: str = "Gemini-3-flash bilingual judge, batched per 10 pairs, 100% coverage"
    judged_count: int
    avg_fidelity: float
    pct_at_10: float
    pct_above_9: float
    pct_above_7: float
    pct_zero: float
    drift_flagged_ids: list[int]
    verdict: str
    grade: str


class RecallMetric(BaseModel):
    """Topic-coverage gate output (LLM-judged per topic)."""

    method: str = (
        "Gemini-3.1-pro extracts 20-30 must-know topics; Gemini-3-flash judges coverage per topic"
    )
    topics_total: int
    topics_covered: int
    coverage_pct: float
    uncovered_topics: list[str]
    verdict: str
    grade: str


class CoverageMetric(BaseModel):
    """Structural distribution: category balance, density, sign ratio."""

    method: str = "Category distribution + density (Qs/1000 manual chars) + sign ratio"
    category_distribution: dict[str, int]
    missing_categories: list[str]
    over_concentrated_categories: list[str]  # >40% in one category
    density_qs_per_1000_chars: float
    sign_ratio_pct: float
    verdict: str
    grade: str


class VerificationReport(BaseModel):
    """Top-level structured verification artifact, written per-state.

    Mirrors the unheard-past verify_book.py pattern: pydantic-typed, machine-readable,
    reproducible, with measurable precision/recall/coverage metrics against the source
    manual as ground truth.
    """

    schema_version: int = 2
    code: str
    name: str
    verified_at: str  # ISO-8601 UTC
    quiz_gates_version: str = "v2"
    source: SourceInfo
    bank: BankInfo
    precision: PrecisionMetric
    recall: RecallMetric
    coverage: CoverageMetric
    # Per-language translation faithfulness (#59 item 3). Keyed by ISO 639-1 code.
    # Absent when the state ships only EN.
    translation: dict[str, TranslationMetric] = Field(default_factory=dict)
    overall_verdict: str  # PASS | SOFT_WARN | HARD_FAIL | INCOMPLETE
    overall_grade: str  # A | B | C | D | F | INCOMPLETE
    notes: str = ""


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
            max_output_tokens=32768,
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
    """Run the faithfulness gate over every non-sign question (or a dev sample).

    Per #59 item 2: default behavior judges 100% of non-sign questions. A non-zero
    ``sample_size`` is a developer escape hatch for local iteration and should NOT
    be used by the bulk verification batch — the committed reports must show
    ``judged_count == non_sign_questions``.
    """
    non_sign = [q for q in questions if "image" not in q]
    total_non_sign = len(non_sign)
    if sample_size and total_non_sign > sample_size:
        rng = random.Random(42)
        non_sign = rng.sample(non_sign, sample_size)
        print(f"  DEV ESCAPE: sampled {sample_size} of {total_non_sign} non-sign questions")
    else:
        print(f"  Judging all {total_non_sign} non-sign questions (100% coverage)")

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


def _format_questions_for_topic_judge(questions: list[dict[str, Any]]) -> str:
    """Compact one-line-per-question summary for the topic-coverage LLM prompt."""
    lines = []
    for q in questions:
        # Skip image questions — they don't carry topic-specific text.
        if "image" in q:
            continue
        qid = q.get("id", "?")
        qtext = q.get("question", "").replace("\n", " ").strip()
        answer = q.get("answer", "")
        choices = q.get("choices", {})
        atext = str(choices.get(answer, "")).replace("\n", " ").strip()
        # Truncate to keep prompt size bounded
        if len(qtext) > 200:
            qtext = qtext[:200] + "..."
        if len(atext) > 100:
            atext = atext[:100] + "..."
        lines.append(f"Q{qid}: {qtext} → ({answer}) {atext}")
    return "\n".join(lines)


def judge_topic_coverage(
    topics: list[CriticalTopic],
    questions: list[dict[str, Any]],
    state_name: str,
) -> list[TopicCoverageJudgment]:
    """LLM-judged per-topic coverage. Replaces brittle keyword matching."""
    questions_block = _format_questions_for_topic_judge(questions)
    topics_block = "\n".join(f"- {t.topic}" for t in topics)
    prompt = f"""You are auditing a {state_name} driver's-test question bank for topic coverage.

For each TOPIC below, judge whether at least one QUESTION in the bank tests it with adequate depth (the question asks the test-taker to know a key fact about the topic, not just mention it tangentially).

TOPICS TO JUDGE ({len(topics)} total):
{topics_block}

QUESTIONS IN BANK (id, question text, correct-answer text):
{questions_block}

For each topic, return:
- is_covered: true/false
- covering_question_ids: up to 5 question IDs that test the topic
- note: one sentence (especially useful when is_covered=false)

The order of judgments MUST match the order of topics above."""
    response = CLIENT.models.generate_content(
        model=MODEL_JUDGE,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=TopicCoverageReport,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=32768,
        ),
    )
    if response.text is None:
        raise RuntimeError("Empty topic-coverage judge response")
    return TopicCoverageReport.model_validate_json(response.text).judgments


def run_coverage_gate(
    questions: list[dict[str, Any]],
    manual_text: str,
    state_name: str,
) -> tuple[list[tuple[CriticalTopic, list[int]]], dict[str, Any]]:
    """Run the recall (topic-coverage) gate via LLM judge."""
    topics = extract_critical_topics(manual_text, state_name)
    judgments = judge_topic_coverage(topics, questions, state_name)

    # Align judgments to topics in case the LLM reordered.
    by_topic = {j.topic.strip().lower(): j for j in judgments}
    results = []
    for t in topics:
        j = by_topic.get(t.topic.strip().lower())
        qids = j.covering_question_ids if (j and j.is_covered) else []
        results.append((t, qids))

    n_topics = len(results)
    n_covered = sum(1 for _, qids in results if qids)
    coverage_pct = (n_covered / n_topics * 100.0) if n_topics else 0.0

    summary = {
        "total_topics": n_topics,
        "covered_topics": n_covered,
        "coverage_pct": round(coverage_pct, 1),
        "uncovered_topics": [t.topic for t, qids in results if not qids],
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
# Coverage gate (structural distribution — categories, density, sign ratio)
# ---------------------------------------------------------------------------

VALID_CATEGORIES = {
    "license_system",
    "driver_testing",
    "driver_responsibility",
    "safe_driving_rules",
    "defensive_driving",
    "alcohol_drugs_health",
    "penalties_and_points",
    "sharing_the_road",
    "vehicle_information",
    "signs_and_signals",
}
OVER_CONCENTRATION_PCT = 40.0


def run_structural_coverage_gate(
    questions: list[dict[str, Any]],
    manual_text: str,
) -> CoverageMetric:
    """Compute category distribution, density, sign ratio — no LLM call."""
    from collections import Counter

    total = len(questions)
    sign_count = sum(1 for q in questions if "image" in q)

    cat_counts = Counter(q.get("category", "?") for q in questions)
    distribution = dict(cat_counts)

    missing = sorted(VALID_CATEGORIES - set(distribution.keys()))

    over_concentrated = []
    if total:
        for cat, n in distribution.items():
            if (n / total) * 100.0 > OVER_CONCENTRATION_PCT:
                over_concentrated.append(cat)

    density = (total / (len(manual_text) / 1000.0)) if manual_text else 0.0
    sign_ratio = (sign_count / total * 100.0) if total else 0.0

    # Verdict: deduct 5 per missing category, 10 per over-concentrated.
    score = 100 - 5 * len(missing) - 10 * len(over_concentrated)
    if score >= 90:
        verdict, grade = "PASS", "A"
    elif score >= 80:
        verdict, grade = "PASS", "B"
    elif score >= 70:
        verdict, grade = "SOFT_WARN", "C"
    elif score >= 60:
        verdict, grade = "SOFT_WARN", "D"
    else:
        verdict, grade = "HARD_FAIL", "F"

    return CoverageMetric(
        category_distribution=distribution,
        missing_categories=missing,
        over_concentrated_categories=over_concentrated,
        density_qs_per_1000_chars=round(density, 2),
        sign_ratio_pct=round(sign_ratio, 1),
        verdict=verdict,
        grade=grade,
    )


# ---------------------------------------------------------------------------
# Gate 4: translation faithfulness (per #59 item 3)
# ---------------------------------------------------------------------------


def _format_pair_for_judge(en_q: dict[str, Any], tgt_q: dict[str, Any], tgt_lang: str) -> str:
    en_choices = en_q.get("choices", {})
    tgt_choices = tgt_q.get("choices", {})
    return (
        f"Q{en_q['id']}\n"
        f"  EN question:  {en_q.get('question', '')}\n"
        f"  EN A: {en_choices.get('A', '')}\n"
        f"  EN B: {en_choices.get('B', '')}\n"
        f"  EN C: {en_choices.get('C', '')}\n"
        f"  EN D: {en_choices.get('D', '')}\n"
        f"  EN answer: {en_q.get('answer', '')}\n"
        f"  EN explanation: {en_q.get('explanation', '')}\n"
        f"  {tgt_lang} question:  {tgt_q.get('question', '')}\n"
        f"  {tgt_lang} A: {tgt_choices.get('A', '')}\n"
        f"  {tgt_lang} B: {tgt_choices.get('B', '')}\n"
        f"  {tgt_lang} C: {tgt_choices.get('C', '')}\n"
        f"  {tgt_lang} D: {tgt_choices.get('D', '')}\n"
        f"  {tgt_lang} answer: {tgt_q.get('answer', '')}\n"
        f"  {tgt_lang} explanation: {tgt_q.get('explanation', '')}"
    )


TRANSLATION_BATCH = 10


def check_translation_batch(
    en_batch: list[dict[str, Any]],
    tgt_batch: list[dict[str, Any]],
    tgt_lang_name: str,
) -> TranslationFaithfulnessReport:
    """Judge a batch of EN/target pairs for translation faithfulness."""
    pairs_block = "\n\n".join(
        _format_pair_for_judge(en, tgt, tgt_lang_name)
        for en, tgt in zip(en_batch, tgt_batch, strict=True)
    )
    prompt = f"""You are auditing {tgt_lang_name} translations of US driver's-test questions for faithfulness to the English original.

For each pair, score 0-10. 10 = answer letter unchanged AND meaning preserved AND no facts added or dropped. Penalize: changed answer letter, softened directives ("must" → "should"), introduced facts not in EN, dropped legal references (BAC limits, fines, ages), drift in numbers.

If fidelity < 7, give a one-sentence drift description.

PAIRS TO JUDGE:
{pairs_block}
"""
    response = CLIENT.models.generate_content(
        model=MODEL_JUDGE,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=TranslationFaithfulnessReport,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=32768,
        ),
    )
    if response.text is None:
        raise RuntimeError(
            f"Empty translation-judge response for batch starting Q{en_batch[0]['id']}"
        )
    return TranslationFaithfulnessReport.model_validate_json(response.text)


def run_translation_faithfulness_gate(
    en_questions: list[dict[str, Any]],
    tgt_questions: list[dict[str, Any]],
    tgt_lang_code: str,
    tgt_lang_name: str,
) -> tuple[list[TranslationAnchor], dict[str, Any]]:
    """Judge every translated pair for faithfulness. 100% coverage (#59 items 2+3).

    Pairs EN and target questions by ``id``. Skips IDs missing in either side and
    skips sign questions (they only translate the prompt, which is constant across
    states and not test-language-sensitive).
    """
    en_by_id = {q["id"]: q for q in en_questions if "image" not in q}
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for tgt_q in tgt_questions:
        if "image" in tgt_q:
            continue
        en_q = en_by_id.get(tgt_q.get("id"))
        if en_q is None:
            continue
        pairs.append((en_q, tgt_q))

    print(f"  Judging {len(pairs)} {tgt_lang_code.upper()} translation pairs (100% coverage)")

    anchors: list[TranslationAnchor] = []
    for i in range(0, len(pairs), TRANSLATION_BATCH):
        batch = pairs[i : i + TRANSLATION_BATCH]
        en_batch = [en for en, _ in batch]
        tgt_batch = [tgt for _, tgt in batch]
        print(
            f"  Translation batch {i // TRANSLATION_BATCH + 1}/"
            f"{(len(pairs) - 1) // TRANSLATION_BATCH + 1} "
            f"(Q{en_batch[0]['id']}-Q{en_batch[-1]['id']})..."
        )
        report = check_translation_batch(en_batch, tgt_batch, tgt_lang_name)
        anchors.extend(report.anchors)

    n = len(anchors)
    n_zero = sum(1 for a in anchors if a.fidelity == 0)
    avg_fidelity = sum(a.fidelity for a in anchors) / n if n else 0.0
    pct_zero = (n_zero / n * 100.0) if n else 0.0
    summary = {
        "total_judged": n,
        "zero_fidelity": n_zero,
        "avg_fidelity": round(avg_fidelity, 2),
        "verdict": _faithfulness_verdict(avg_fidelity, pct_zero),
    }
    return anchors, summary


LANG_NAMES_FOR_JUDGE = {
    "es": "Spanish",
    "ja": "Japanese",
    "zh": "Simplified Chinese",
    "ko": "Korean",
}


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


def _grade_precision(avg: float, pct_zero: float) -> str:
    if pct_zero > MAX_HARD_FAIL_QUESTIONS_PCT:
        return "F"
    if avg >= 9.5:
        return "A"
    if avg >= 9.0:
        return "B"
    if avg >= 8.0:
        return "C"
    if avg >= 7.0:
        return "D"
    return "F"


def _grade_recall(pct: float) -> str:
    if pct >= 90:
        return "A"
    if pct >= 80:
        return "B"
    if pct >= 70:
        return "C"
    if pct >= 60:
        return "D"
    return "F"


def _overall_grade(p: str, r: str, c: str) -> str:
    if "F" in (p, r, c):
        return "F"
    rank = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
    gpa = (rank[p] + rank[r] + rank[c]) / 3
    if gpa >= 3.5:
        return "A"
    if gpa >= 2.5:
        return "B"
    if gpa >= 1.5:
        return "C"
    if gpa >= 0.5:
        return "D"
    return "F"


def build_verification_report(
    code: str,
    questions: list[dict[str, Any]],
    manual_text: str,
    state_name: str,
    sample_size: int | None,
) -> VerificationReport:
    """Run all three gates and assemble a structured VerificationReport."""
    import hashlib
    from datetime import datetime, timezone

    state_dir = os.path.join(STATES_DIR, code)
    config_path = os.path.join(state_dir, "config.json")
    prov_path = os.path.join(state_dir, "manual_provenance.json")
    es_path = os.path.join(state_dir, "questions_es.yaml")
    ja_path = os.path.join(state_dir, "questions_ja.yaml")

    config = json.load(open(config_path)) if os.path.exists(config_path) else {}
    provenance = json.load(open(prov_path)) if os.path.exists(prov_path) else {}

    languages = ["EN"]
    if os.path.exists(es_path):
        languages.append("ES")
    if os.path.exists(ja_path):
        languages.append("JA")

    source = SourceInfo(
        manual_url=config.get("manual_url", provenance.get("manual_url", "")),
        manual_pdf_sha256=(provenance.get("pdf") or {}).get("sha256"),
        manual_text_sha256=(provenance.get("text") or {}).get("sha256")
        or hashlib.sha256(manual_text.encode()).hexdigest(),
        manual_text_chars=len(manual_text),
        manual_pages=(provenance.get("pdf") or {}).get("page_count"),
        edition=provenance.get("edition"),
    )

    sign_count = sum(1 for q in questions if "image" in q)
    bank = BankInfo(
        total_questions=len(questions),
        non_sign_questions=len(questions) - sign_count,
        sign_questions=sign_count,
        languages=languages,
    )

    # --- Precision (faithfulness) ---
    print("[Precision: faithfulness]")
    anchors, faith_summary = run_faithfulness_gate(questions, manual_text, state_name, sample_size)
    n = faith_summary["total_judged"]
    pct_at_10 = (sum(1 for a in anchors if a.fidelity == 10) / n * 100.0) if n else 0.0
    pct_above_9 = (sum(1 for a in anchors if a.fidelity >= 9) / n * 100.0) if n else 0.0
    pct_above_7 = (sum(1 for a in anchors if a.fidelity >= 7) / n * 100.0) if n else 0.0
    pct_zero = (faith_summary["zero_fidelity"] / n * 100.0) if n else 0.0
    evidence_by_id = {str(a.question_id): a.manual_evidence for a in anchors if a.manual_evidence}
    precision = PrecisionMetric(
        sample_size=sample_size if sample_size else 0,
        judged_count=n,
        avg_fidelity=faith_summary["avg_fidelity"],
        pct_at_10=round(pct_at_10, 1),
        pct_above_9=round(pct_above_9, 1),
        pct_above_7=round(pct_above_7, 1),
        pct_zero=round(pct_zero, 1),
        flagged_question_ids=[a.question_id for a in anchors if a.fidelity < HARD_FAIL_FIDELITY],
        evidence_by_question_id=evidence_by_id,
        verdict=faith_summary["verdict"],
        grade=_grade_precision(faith_summary["avg_fidelity"], pct_zero),
    )

    # --- Recall (topic coverage, LLM-judged) ---
    print("\n[Recall: topic-coverage, LLM-judged]")
    _, recall_summary = run_coverage_gate(questions, manual_text, state_name)
    recall = RecallMetric(
        topics_total=recall_summary["total_topics"],
        topics_covered=recall_summary["covered_topics"],
        coverage_pct=recall_summary["coverage_pct"],
        uncovered_topics=recall_summary["uncovered_topics"],
        verdict=recall_summary["verdict"],
        grade=_grade_recall(recall_summary["coverage_pct"]),
    )

    # --- Coverage (structural distribution) ---
    print("\n[Coverage: structural distribution]")
    coverage = run_structural_coverage_gate(questions, manual_text)

    # --- Translation faithfulness, per shipped non-English bank ---
    translation: dict[str, TranslationMetric] = {}
    for lang_code in ("es", "ja"):
        lang_path = os.path.join(state_dir, f"questions_{lang_code}.yaml")
        if not os.path.exists(lang_path):
            continue
        lang_name = LANG_NAMES_FOR_JUDGE.get(lang_code)
        if lang_name is None:
            continue
        print(f"\n[Translation: {lang_code.upper()} faithfulness, LLM-judged]")
        with open(lang_path) as f:
            tgt_questions = (yaml.safe_load(f) or {}).get("questions", [])
        if not tgt_questions:
            continue
        t_anchors, t_summary = run_translation_faithfulness_gate(
            questions, tgt_questions, lang_code, lang_name
        )
        t_n = t_summary["total_judged"]
        t_pct_at_10 = (sum(1 for a in t_anchors if a.fidelity == 10) / t_n * 100.0) if t_n else 0.0
        t_pct_above_9 = (
            (sum(1 for a in t_anchors if a.fidelity >= 9) / t_n * 100.0) if t_n else 0.0
        )
        t_pct_above_7 = (
            (sum(1 for a in t_anchors if a.fidelity >= 7) / t_n * 100.0) if t_n else 0.0
        )
        t_pct_zero = (t_summary["zero_fidelity"] / t_n * 100.0) if t_n else 0.0
        translation[lang_code] = TranslationMetric(
            judged_count=t_n,
            avg_fidelity=t_summary["avg_fidelity"],
            pct_at_10=round(t_pct_at_10, 1),
            pct_above_9=round(t_pct_above_9, 1),
            pct_above_7=round(t_pct_above_7, 1),
            pct_zero=round(t_pct_zero, 1),
            drift_flagged_ids=[
                a.question_id for a in t_anchors if a.fidelity < HARD_FAIL_FIDELITY
            ],
            verdict=t_summary["verdict"],
            grade=_grade_precision(t_summary["avg_fidelity"], t_pct_zero),
        )

    # --- Overall ---
    rank = {"PASS": 0, "SOFT_WARN": 1, "HARD_FAIL": 2}
    verdicts = [precision.verdict, recall.verdict, coverage.verdict] + [
        m.verdict for m in translation.values()
    ]
    overall_verdict = max(verdicts, key=lambda v: rank[v])
    overall_grade = _overall_grade(precision.grade, recall.grade, coverage.grade)

    return VerificationReport(
        code=code,
        name=state_name,
        verified_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        source=source,
        bank=bank,
        precision=precision,
        recall=recall,
        coverage=coverage,
        translation=translation,
        overall_verdict=overall_verdict,
        overall_grade=overall_grade,
    )


def write_verification_report(code: str, report: VerificationReport) -> str:
    """Write verification_report.json to data/states/<code>/."""
    state_dir = os.path.join(STATES_DIR, code)
    os.makedirs(state_dir, exist_ok=True)
    out_path = os.path.join(state_dir, "verification_report.json")
    with open(out_path, "w") as f:
        f.write(report.model_dump_json(indent=2) + "\n")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("code", help="State code (e.g. 'nj')")
    parser.add_argument(
        "--sample",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help=(
            f"DEV ONLY: random sample size for precision gate. Default {DEFAULT_SAMPLE_SIZE} "
            "(0 = judge all non-sign questions, the production default). "
            "Non-zero values are for local iteration and must NOT be used by the bulk "
            "verification batch — committed reports must judge 100% of every state's bank."
        ),
    )
    parser.add_argument(
        "--block-on-fail",
        action="store_true",
        help="Exit 2 on hard fail (default: always exit 0 with report)",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write data/states/<code>/verification_report.json with structured pydantic output",
    )
    args = parser.parse_args(argv)

    questions, manual_text, state_name = _load_state(args.code)
    print(
        f"\n{state_name} ({args.code.upper()}) — {len(questions)} questions, {len(manual_text):,} manual chars"
    )

    sample = args.sample if args.sample > 0 else None
    report = build_verification_report(args.code, questions, manual_text, state_name, sample)

    # Pretty-print summary to stdout.
    print(
        f"\n  Precision: avg={report.precision.avg_fidelity}/10  "
        f"pct@10={report.precision.pct_at_10}%  "
        f"flagged={len(report.precision.flagged_question_ids)}  "
        f"verdict={report.precision.verdict}  grade={report.precision.grade}"
    )
    print(
        f"  Recall:    {report.recall.topics_covered}/{report.recall.topics_total} topics  "
        f"({report.recall.coverage_pct}%)  "
        f"verdict={report.recall.verdict}  grade={report.recall.grade}"
    )
    print(
        f"  Coverage:  {len(report.coverage.category_distribution)} categories  "
        f"density={report.coverage.density_qs_per_1000_chars} Qs/1k chars  "
        f"signs={report.coverage.sign_ratio_pct}%  "
        f"verdict={report.coverage.verdict}  grade={report.coverage.grade}"
    )
    if report.coverage.missing_categories:
        print(f"             missing categories: {', '.join(report.coverage.missing_categories)}")
    if report.coverage.over_concentrated_categories:
        print(
            f"             over-concentrated:  {', '.join(report.coverage.over_concentrated_categories)}"
        )
    for lang_code, tmetric in report.translation.items():
        print(
            f"  Translation ({lang_code.upper()}): avg={tmetric.avg_fidelity}/10  "
            f"pct@10={tmetric.pct_at_10}%  drift_flagged={len(tmetric.drift_flagged_ids)}  "
            f"verdict={tmetric.verdict}  grade={tmetric.grade}"
        )
    if report.recall.uncovered_topics:
        print(f"  Uncovered topics ({len(report.recall.uncovered_topics)}):")
        for t in report.recall.uncovered_topics[:10]:
            print(f"    - {t}")
        if len(report.recall.uncovered_topics) > 10:
            print(f"    ... and {len(report.recall.uncovered_topics) - 10} more")

    print(f"\n  === Overall: {report.overall_verdict} (grade {report.overall_grade}) ===")

    if args.write_report:
        out = write_verification_report(args.code, report)
        print(f"\nWrote {out}")

    if not args.block_on_fail:
        return 0
    return {"PASS": 0, "SOFT_WARN": 1, "HARD_FAIL": 2}[report.overall_verdict]


if __name__ == "__main__":
    sys.exit(main())
