#!/usr/bin/env python3
"""Audit driver's test questions for quality, accuracy, and groundedness.

Checks:
1. Structural validity (4 choices, valid answer, required fields)
2. Duplicate detection (within and across states)
3. LLM-based accuracy audit (uses Gemini to verify questions are factually correct)

Usage:
    python audit_questions.py                    # Audit all states
    python audit_questions.py nj ny              # Audit specific states
    python audit_questions.py --llm nj           # Run LLM accuracy check
"""

import hashlib
import json
import os
import sys

import yaml
from _util import STATES_DIR, questions_path, resolve_state_paths, strip_code_fences

DUPLICATE_OVERLAP_THRESHOLD = 0.7
MIN_QUESTION_LENGTH = 10
MAX_QUESTION_LENGTH = 500
LLM_AUDIT_SAMPLE_SIZE = 20


def load_questions(state_code: str) -> tuple[list[dict], dict]:
    paths = resolve_state_paths(state_code)
    q_path = paths["questions_en_path"]
    config_path = paths["config_path"]
    if not os.path.exists(q_path):
        return [], {}
    with open(q_path) as f:
        data = yaml.safe_load(f)
    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    return data.get("questions", []), config


def structural_audit(_state_code: str, questions: list[dict]) -> list[str]:
    """Check structural validity of questions."""
    issues = []
    seen_ids = set()
    valid_cats = {
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
    for i, q in enumerate(questions):
        qid = q.get("id", f"index-{i}")
        # Required fields
        for field in ["id", "question", "choices", "answer", "category"]:
            if field not in q:
                issues.append(f"Q{qid}: missing field '{field}'")
        # Choices
        choices = q.get("choices", {})
        if isinstance(choices, dict):
            if set(choices.keys()) != {"A", "B", "C", "D"}:
                issues.append(f"Q{qid}: choices keys are {set(choices.keys())}, expected A/B/C/D")
            # Empty choices
            for k, v in choices.items():
                if not v or not str(v).strip():
                    issues.append(f"Q{qid}: choice {k} is empty")
        else:
            issues.append(f"Q{qid}: choices is not a dict")
        # Answer validity
        answer = q.get("answer", "")
        if answer not in ("A", "B", "C", "D"):
            issues.append(f"Q{qid}: answer '{answer}' not in A/B/C/D")
        # Duplicate IDs
        if qid in seen_ids:
            issues.append(f"Q{qid}: duplicate ID")
        seen_ids.add(qid)
        # Question text length
        qt = q.get("question", "")
        if len(qt) < MIN_QUESTION_LENGTH:
            issues.append(f"Q{qid}: question too short ({len(qt)} chars)")
        if len(qt) > MAX_QUESTION_LENGTH:
            issues.append(f"Q{qid}: question very long ({len(qt)} chars)")
        # Category
        cat = q.get("category", "")
        if cat and cat not in valid_cats:
            issues.append(f"Q{qid}: unknown category '{cat}'")

    return issues


def translation_alignment_audit(state_code: str) -> list[str]:
    """Verify target-language banks are derived 1:1 from the English bank.

    Invariants (per #59 follow-up — the EN bank is the source of truth):
    - target IDs must equal EN IDs (same set, same count)
    - no orphan IDs in target that don't exist in EN
    - no missing IDs that exist in EN but not target

    If the invariant fails, the target bank is in an inconsistent state and
    must be regenerated from the current EN bank via translate.py.
    """
    issues: list[str] = []
    paths = resolve_state_paths(state_code)
    en_path = paths["questions_en_path"]
    if not os.path.exists(en_path):
        return issues
    with open(en_path) as f:
        en_questions = (yaml.safe_load(f) or {}).get("questions", [])
    en_ids = {q.get("id") for q in en_questions if "id" in q}
    for lang in ("es", "ja"):
        lang_path = questions_path(state_code, lang)
        if not os.path.exists(lang_path):
            continue
        with open(lang_path) as f:
            tgt_questions = (yaml.safe_load(f) or {}).get("questions", [])
        tgt_ids = {q.get("id") for q in tgt_questions if "id" in q}
        orphans = sorted(tgt_ids - en_ids)
        missing = sorted(en_ids - tgt_ids)
        if orphans:
            sample = ", ".join(str(o) for o in orphans[:5])
            more = f" (+{len(orphans) - 5} more)" if len(orphans) > 5 else ""
            issues.append(
                f"{lang.upper()} bank has {len(orphans)} orphan IDs not in EN: {sample}{more}. "
                f"Drop them or regenerate via `python3 tools/translate.py {state_code} {lang}`."
            )
        if missing:
            sample = ", ".join(str(m) for m in missing[:5])
            more = f" (+{len(missing) - 5} more)" if len(missing) > 5 else ""
            issues.append(
                f"{lang.upper()} bank is missing {len(missing)} IDs that exist in EN: {sample}{more}. "
                f"Re-run `python3 tools/translate.py {state_code} {lang}`."
            )
    return issues


def translation_staleness_audit(state_code: str) -> list[str]:
    """Flag translated banks whose en_source_sha256 doesn't match current questions_en.yaml.

    Per #59 item 6: if a maintainer regenerates EN questions but forgets to re-run
    translate.py, the ES/JA bank silently references stale EN content. Compare the
    hash recorded in the translated YAML against the current EN bytes.
    """
    issues: list[str] = []
    paths = resolve_state_paths(state_code)
    en_path = paths["questions_en_path"]
    if not os.path.exists(en_path):
        return issues
    with open(en_path, "rb") as f:
        current_en_sha = hashlib.sha256(f.read()).hexdigest()
    for lang in ("es", "ja"):
        lang_path = questions_path(state_code, lang)
        if not os.path.exists(lang_path):
            continue
        with open(lang_path) as f:
            tgt = yaml.safe_load(f) or {}
        recorded = (tgt.get("metadata") or {}).get("translation", {}).get("en_source_sha256")
        if recorded is None:
            # Pre-#59 translations have no provenance — informational, not a failure.
            issues.append(
                f"{lang.upper()} bank has no translation provenance "
                f"(generated before #59 item 6). Re-translate to record en_source_sha256."
            )
            continue
        if recorded != current_en_sha:
            issues.append(
                f"{lang.upper()} bank is stale: en_source_sha256={recorded[:12]}… "
                f"but current EN is {current_en_sha[:12]}…. Re-run "
                f"`python3 tools/translate.py {state_code} {lang}`."
            )
    return issues


def duplicate_audit(_state_code: str, questions: list[dict]) -> list[str]:
    """Check for duplicate questions within a state (skips image-based questions)."""
    issues = []
    seen = []
    for q in questions:
        if q.get("image"):
            continue  # Sign questions have intentionally similar text
        qt = q.get("question", "").lower().strip()
        words = set(qt.split())
        for idx, existing_words in seen:
            overlap = len(words & existing_words) / max(len(words | existing_words), 1)
            if overlap > DUPLICATE_OVERLAP_THRESHOLD:
                issues.append(f"Q{q['id']}: likely duplicate of Q{idx} (overlap={overlap:.0%})")
                break
        seen.append((q["id"], frozenset(words)))
    return issues


def content_audit(_state_code: str, questions: list[dict], _config: dict) -> list[str]:
    """Check question content for common issues."""
    issues = []

    for q in questions:
        qid = q.get("id", "?")
        choices = q.get("choices", {})
        answer = q.get("answer", "")
        explanation = q.get("explanation", "")

        # Check answer matches a valid choice
        if answer in choices:
            correct_text = str(choices[answer]).strip()
            if not correct_text:
                issues.append(f"Q{qid}: correct answer ({answer}) text is empty")

        # Check for "all of the above" / "none of the above" answers that might be wrong
        for k, v in choices.items():
            vl = str(v).lower()
            if "all of the above" in vl and k != "D":
                issues.append(
                    f"Q{qid}: 'all of the above' should typically be choice D, found in {k}"
                )
            if "none of the above" in vl and k != "D":
                issues.append(
                    f"Q{qid}: 'none of the above' should typically be choice D, found in {k}"
                )

        # Check explanation exists
        if not explanation or len(str(explanation)) < 10:
            issues.append(f"Q{qid}: missing or very short explanation")

    return issues


def llm_audit(state_code: str, questions: list[dict], config: dict) -> list[str]:
    """Use Gemini to verify factual accuracy of questions."""
    from google import genai

    MODEL = "gemini-3-flash-preview"
    CLIENT = genai.Client(vertexai=True, project="adk-coding-agents", location="global")

    state_name = config.get("name", state_code.upper())
    issues = []

    # Sample 20 questions for LLM audit (to keep costs low)
    import random

    sample = random.sample(questions, min(LLM_AUDIT_SAMPLE_SIZE, len(questions)))

    prompt = f"""You are auditing driver's test questions for {state_name}.
For each question below, verify:
1. Is the stated correct answer actually correct for {state_name}?
2. Are the facts in the question and explanation accurate?
3. Is the question clear and unambiguous?

For any issues found, output a JSON array of objects with "id" and "issue" fields.
If all questions are fine, output an empty array: []

Questions to audit:
{json.dumps([{"id": q["id"], "question": q["question"], "choices": q["choices"], "answer": q["answer"], "explanation": q.get("explanation", "")} for q in sample], indent=2)}"""

    try:
        response = CLIENT.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=4096,
            ),
        )
        if response.text is None:
            raise ValueError("Empty response from model")
        text = strip_code_fences(response.text)
        found = json.loads(text)
        for item in found:
            issues.append(f"Q{item['id']}: {item['issue']}")
    except Exception as e:
        issues.append(f"LLM audit error: {e}")

    return issues


def main() -> None:
    use_llm = "--llm" in sys.argv
    state_codes = [a for a in sys.argv[1:] if a != "--llm"]

    if not state_codes:
        state_codes = sorted(
            [d for d in os.listdir(STATES_DIR) if os.path.isdir(os.path.join(STATES_DIR, d))]
        )

    total_issues = 0
    total_questions = 0

    for code in state_codes:
        questions, config = load_questions(code)
        if not questions:
            print(f"\n{code.upper()}: no questions found")
            continue

        name = config.get("name", code.upper())
        print(f"\n{'=' * 60}")
        print(f"{name} ({code.upper()}) — {len(questions)} questions")
        print(f"{'=' * 60}")
        total_questions += len(questions)

        # Structural audit
        struct_issues = structural_audit(code, questions)
        if struct_issues:
            print(f"  STRUCTURAL ({len(struct_issues)} issues):")
            for issue in struct_issues[:10]:
                print(f"    - {issue}")
            if len(struct_issues) > 10:
                print(f"    ... and {len(struct_issues) - 10} more")

        # Duplicate audit
        dup_issues = duplicate_audit(code, questions)
        if dup_issues:
            print(f"  DUPLICATES ({len(dup_issues)} issues):")
            for issue in dup_issues[:10]:
                print(f"    - {issue}")
            if len(dup_issues) > 10:
                print(f"    ... and {len(dup_issues) - 10} more")

        # Translation alignment audit (EN is the source of truth — target derived from it)
        alignment_issues = translation_alignment_audit(code)
        if alignment_issues:
            print(f"  TRANSLATION ALIGNMENT ({len(alignment_issues)} issues):")
            for issue in alignment_issues:
                print(f"    - {issue}")

        # Translation staleness audit
        translation_issues = translation_staleness_audit(code)
        if translation_issues:
            print(f"  TRANSLATION STALENESS ({len(translation_issues)} issues):")
            for issue in translation_issues:
                print(f"    - {issue}")

        # Content audit
        content_issues = content_audit(code, questions, config)
        if content_issues:
            print(f"  CONTENT ({len(content_issues)} issues):")
            for issue in content_issues[:10]:
                print(f"    - {issue}")
            if len(content_issues) > 10:
                print(f"    ... and {len(content_issues) - 10} more")

        # LLM audit (optional)
        llm_issues = []
        if use_llm:
            print("  Running LLM accuracy audit...")
            llm_issues = llm_audit(code, questions, config)
            if llm_issues:
                print(f"  LLM AUDIT ({len(llm_issues)} issues):")
                for issue in llm_issues:
                    print(f"    - {issue}")

        state_issues = (
            len(struct_issues)
            + len(dup_issues)
            + len(alignment_issues)
            + len(translation_issues)
            + len(content_issues)
            + len(llm_issues)
        )
        total_issues += state_issues
        if state_issues == 0:
            print("  ✓ All checks passed")

    print(f"\n{'=' * 60}")
    print(
        f"TOTAL: {total_questions} questions across {len(state_codes)} states, {total_issues} issues found"
    )
    if total_issues > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
