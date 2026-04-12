#!/usr/bin/env python3
"""Generate supplemental questions for states with low question counts.

Reads existing questions, generates new ones avoiding duplicates, and merges.

Usage:
    python supplement_questions.py <state_code> <manual_text_file> [target_count]
    python supplement_questions.py ca /tmp/ca_manual_text.txt 300
"""

import json
import os
import sys
import time

import yaml
from _util import (
    chunk_text,
    deduplicate,
    resolve_state_paths,
    retry_with_backoff,
    strip_code_fences,
)
from google import genai

MODEL = "gemini-2.5-pro"
CLIENT = genai.Client(vertexai=True, project="adk-coding-agents", location="global")

SYSTEM_PROMPT = """\
You are an expert driver education test writer. Generate multiple-choice questions from the provided driver's manual text.

Rules:
1. Each question must have exactly 4 choices labeled A, B, C, D
2. Exactly one answer must be correct
3. Questions should cover: rules of the road, signs/signals, right-of-way, parking, alcohol/drugs, penalties, safe driving, vehicle operation, sharing the road, licensing
4. Questions must be factually accurate based on the manual text provided
5. Include a mix of difficulty levels
6. Explanations should cite the relevant rule or fact from the manual
7. Do NOT create questions that require viewing an image to answer
8. Return valid JSON only, no markdown fences
9. Make questions DIFFERENT from the existing ones listed below - cover different facts, scenarios, and details

Output format - JSON array:
[
  {
    "id": 1,
    "category": "safe_driving_rules",
    "question": "What is the speed limit in a school zone?",
    "choices": {"A": "15 mph", "B": "20 mph", "C": "25 mph", "D": "30 mph"},
    "answer": "B",
    "explanation": "The speed limit in school zones is 20 mph when children are present."
  }
]

Categories to use: license_system, driver_testing, driver_responsibility, safe_driving_rules, defensive_driving, alcohol_drugs_health, penalties_and_points, sharing_the_road, vehicle_information, signs_and_signals"""


def generate_batch(
    text_chunk: str, start_id: int, state_name: str, existing_summary: str, num_questions: int = 20
) -> list[dict]:
    prompt = f"""\
Generate {num_questions} NEW and UNIQUE multiple-choice driver's test questions from this section of the {state_name} driver's manual.
Start question IDs at {start_id}.

IMPORTANT: Do NOT duplicate any of these existing question topics:
{existing_summary}

Focus on specific facts, numbers, distances, penalties, and scenarios from the manual text that are NOT already covered above.

Manual text:
{text_chunk}"""

    response = CLIENT.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.4,
            max_output_tokens=65536,
        ),
    )
    if response.text is None:
        raise ValueError("Empty response from model")
    text = strip_code_fences(response.text)
    return json.loads(text)


def load_existing(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("questions", [])


def summarize_existing(questions: list[dict]) -> str:
    """Create a compact summary of existing question topics to avoid duplicates."""
    lines = []
    for q in questions:
        lines.append(f"- {q['question'][:80]}")
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 3:
        print(
            "Usage: python supplement_questions.py <state_code> <manual_text_file> [target_count]"
        )
        sys.exit(1)

    state_code = sys.argv[1].lower()
    manual_file = sys.argv[2]
    target_count = int(sys.argv[3]) if len(sys.argv) > 3 else 300

    paths = resolve_state_paths(state_code)
    config_path = paths["config_path"]
    output_path = paths["questions_en_path"]

    if not os.path.exists(config_path):
        print(f"Config not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    with open(manual_file) as f:
        manual_text = f.read()

    state_name = config["name"]
    existing = load_existing(output_path)
    print(f"{state_name}: {len(existing)} existing questions, target {target_count}")

    if len(existing) >= target_count:
        print("Already at target count, skipping.")
        return

    existing_summary = summarize_existing(existing)
    # Truncate summary if too long (keep last 200 lines for context window)
    summary_lines = existing_summary.split("\n")
    if len(summary_lines) > 200:
        existing_summary = (
            "\n".join(summary_lines[:200]) + f"\n... and {len(summary_lines) - 200} more"
        )

    chunks = chunk_text(manual_text)
    total_chunks = len(chunks)
    new_questions = []
    next_id = len(existing) + 1
    needed = target_count - len(existing)

    print(f"Generating ~{needed} more questions from {total_chunks} chunks...")

    for i, chunk in enumerate(chunks):
        if len(new_questions) >= needed:
            break

        batch_num = i + 1
        qs_per_chunk = min(25, max(15, needed // total_chunks + 5))
        print(f"  Chunk {batch_num}/{total_chunks} ({qs_per_chunk} qs)...", end=" ", flush=True)

        try:
            questions = retry_with_backoff(
                lambda ch=chunk, nid=next_id, qpc=qs_per_chunk: generate_batch(
                    ch, nid, state_name, existing_summary, num_questions=qpc
                )
            )
            for q in questions:
                q["id"] = next_id
                next_id += 1
            new_questions.extend(questions)
            print(f"OK ({len(questions)} new, total new: {len(new_questions)})")
        except Exception:
            pass  # retry_with_backoff already printed the failure

        if i + 1 < total_chunks:
            time.sleep(1)

    # Deduplicate new questions against existing ones, then merge
    unique_new = deduplicate(new_questions, existing_questions=existing)
    unique = existing + unique_new

    # Re-number
    for i, q in enumerate(unique, 1):
        q["id"] = i

    categories = sorted(set(q["category"] for q in unique))

    out_data = {
        "metadata": {
            "source": config.get("source", f"{state_name} Driver's Manual"),
            "total_questions": len(unique),
            "categories": categories,
        },
        "questions": unique,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(out_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    dupes = len(new_questions) - len(unique_new)
    print(
        f"\nDone! {len(existing)} existing + {len(new_questions)} new - {dupes} dupes = {len(unique)} total"
    )
    print(f"Wrote to {output_path}")


if __name__ == "__main__":
    main()
