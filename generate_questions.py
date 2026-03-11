#!/usr/bin/env python3
"""Generate driver's test questions from manual text using Gemini.

Usage:
    python generate_questions.py <state_code> <manual_text_file>
    python generate_questions.py ny /tmp/ny_manual_text.txt
"""

import json
import os
import sys
import time
import yaml
from google import genai

MODEL = "gemini-3.1-pro-preview"
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

Output format - JSON array:
[
  {
    "id": 1,
    "category": "safe_driving_rules",
    "question": "What is the speed limit in a school zone in New York?",
    "choices": {"A": "15 mph", "B": "20 mph", "C": "25 mph", "D": "30 mph"},
    "answer": "B",
    "explanation": "The speed limit in school zones in New York is 20 mph when children are present."
  }
]

Categories to use: license_system, driver_testing, driver_responsibility, safe_driving_rules, defensive_driving, alcohol_drugs_health, penalties_and_points, sharing_the_road, vehicle_information, signs_and_signals"""


def generate_batch(text_chunk: str, start_id: int, state_name: str, num_questions: int = 15) -> list[dict]:
    prompt = f"""\
Generate {num_questions} multiple-choice driver's test questions from this section of the {state_name} driver's manual.
Start question IDs at {start_id}.

Manual text:
{text_chunk}"""

    response = CLIENT.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
            max_output_tokens=8192,
        ),
    )
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[: text.rfind("```")]
        text = text.strip()
    return json.loads(text)


def chunk_text(text: str, chunk_size: int = 10000, overlap: int = 500) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Try to break at a paragraph boundary
            newline_pos = text.rfind("\n\n", start + chunk_size - 1000, end + 500)
            if newline_pos > start:
                end = newline_pos
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_questions.py <state_code> <manual_text_file>")
        sys.exit(1)

    state_code = sys.argv[1].lower()
    manual_file = sys.argv[2]

    state_dir = os.path.join(os.path.dirname(__file__), "states", state_code)
    config_path = os.path.join(state_dir, "config.json")
    output_path = os.path.join(state_dir, "questions_en.yaml")

    if not os.path.exists(config_path):
        print(f"Config not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    with open(manual_file) as f:
        manual_text = f.read()

    state_name = config["name"]
    chunks = chunk_text(manual_text)
    total_chunks = len(chunks)
    all_questions = []
    next_id = 1

    print(f"Generating questions for {state_name} from {len(chunks)} chunks...")

    for i, chunk in enumerate(chunks):
        batch_num = i + 1
        print(f"  Chunk {batch_num}/{total_chunks}...", end=" ", flush=True)

        for attempt in range(3):
            try:
                questions = generate_batch(chunk, next_id, state_name, num_questions=15)
                # Re-number to avoid gaps
                for q in questions:
                    q["id"] = next_id
                    next_id += 1
                all_questions.extend(questions)
                print(f"OK ({len(questions)} questions, total: {len(all_questions)})")
                break
            except Exception as e:
                if attempt < 2:
                    wait = 2 ** (attempt + 1)
                    print(f"retry in {wait}s ({e})...", end=" ", flush=True)
                    time.sleep(wait)
                else:
                    print(f"FAILED: {e}")

        if i + 1 < total_chunks:
            time.sleep(1)

    # Deduplicate by question text similarity
    seen = set()
    unique = []
    for q in all_questions:
        key = q["question"].lower().strip()
        words = set(key.split())
        is_dup = False
        for existing_words in seen:
            overlap = len(words & existing_words) / max(len(words | existing_words), 1)
            if overlap > 0.5:
                is_dup = True
                break
        if not is_dup:
            seen.add(frozenset(words))
            unique.append(q)

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

    print(f"\nDone! Wrote {len(unique)} unique questions to {output_path}")
    print(f"Categories: {', '.join(categories)}")


if __name__ == "__main__":
    main()
