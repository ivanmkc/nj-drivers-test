#!/usr/bin/env python3
"""Generate driver's test questions using Gemini's knowledge of state driving rules.

Unlike generate_questions.py which requires manual text, this generates questions
from the model's training knowledge of state-specific driving laws and regulations.

Usage:
    python generate_questions_from_knowledge.py <state_code>
    python generate_questions_from_knowledge.py pa
"""

import json
import os
import sys
import time
import yaml
from google import genai

MODEL = "gemini-3-flash-preview"
CLIENT = genai.Client(vertexai=True, project="adk-coding-agents", location="global")

CATEGORIES = [
    ("license_system", "Driver licensing, GDL, permit requirements, ID documents"),
    ("driver_testing", "Written test, road test, vision test requirements"),
    ("driver_responsibility", "Insurance, registration, accident reporting, financial responsibility"),
    ("safe_driving_rules", "Speed limits, lane usage, turns, passing, parking, school zones, work zones"),
    ("defensive_driving", "Following distance, scanning, adverse conditions, night driving, hydroplaning"),
    ("alcohol_drugs_health", "DUI/DWI laws, BAC limits, implied consent, drug effects, medical conditions"),
    ("penalties_and_points", "Point system, fines, license suspension/revocation, violations"),
    ("sharing_the_road", "Pedestrians, cyclists, motorcycles, trucks, school buses, emergency vehicles"),
    ("vehicle_information", "Equipment requirements, tires, brakes, lights, mirrors, emissions"),
    ("signs_and_signals", "Traffic signs, signals, pavement markings, hand signals"),
]

SYSTEM_PROMPT = """\
You are an expert driver education test writer. Generate accurate multiple-choice questions based on the official driver's manual and driving laws for the specified jurisdiction (US state, Canadian province, or territory).

Rules:
1. Each question must have exactly 4 choices labeled A, B, C, D — use ONLY the single uppercase letters A, B, C, D as keys
2. Exactly one answer must be correct
3. Questions must be factually accurate for the SPECIFIC JURISDICTION requested
4. Include jurisdiction-specific rules, fines, BAC limits, point systems, speed limits, etc.
5. Include a mix of difficulty levels
6. Explanations should cite the relevant jurisdiction-specific rule or fact
7. Do NOT create questions that require viewing an image to answer
8. Do NOT repeat questions across batches
9. Each question must be a complete, self-contained sentence (not a sentence fragment or fill-in-the-blank)
10. Use the correct units for the jurisdiction (mph for US, km/h for Canada)
11. Return valid JSON only, no markdown fences

Output format - JSON array:
[
  {
    "id": 1,
    "category": "safe_driving_rules",
    "question": "In Pennsylvania, what is the speed limit in a residential area unless otherwise posted?",
    "choices": {"A": "20 mph", "B": "25 mph", "C": "30 mph", "D": "35 mph"},
    "answer": "B",
    "explanation": "In Pennsylvania, the default speed limit in residential areas is 25 mph unless otherwise posted."
  }
]"""


def generate_category_batch(state_name: str, state_code: str, category: str, category_desc: str,
                            start_id: int, num_questions: int, existing_questions: list[str]) -> list[dict]:
    exclude_text = ""
    if existing_questions:
        sample = existing_questions[:20]
        exclude_text = f"\n\nDo NOT generate questions similar to these already-generated questions:\n" + "\n".join(f"- {q}" for q in sample)

    prompt = f"""\
Generate {num_questions} multiple-choice driver's test questions for {state_name} ({state_code.upper()}).

Category: {category} — {category_desc}

Focus on {state_name}-specific rules, laws, fines, and regulations. Use accurate jurisdiction-specific details like:
- Speed limits, BAC limits, point values specific to {state_name}
- Penalties, fines, suspension periods specific to {state_name}
- GDL/permit rules and age requirements specific to {state_name}
- Insurance and registration requirements specific to {state_name}

Each question MUST be a complete sentence (e.g. "What is the speed limit..." not "The speed limit is:").
Choice keys MUST be exactly A, B, C, D — no other characters.

Start question IDs at {start_id}.{exclude_text}"""

    response = CLIENT.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.4,
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_questions_from_knowledge.py <state_code>")
        sys.exit(1)

    state_code = sys.argv[1].lower()
    state_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "states", state_code)
    config_path = os.path.join(state_dir, "config.json")
    output_path = os.path.join(state_dir, "questions_en.yaml")

    if not os.path.exists(config_path):
        print(f"Config not found: {config_path}. Run setup first.")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    if os.path.exists(output_path):
        print(f"Questions already exist: {output_path}")
        sys.exit(0)

    state_name = config["name"]
    all_questions = []
    existing_q_texts = []
    next_id = 1

    # Generate ~30 questions per category (10 categories = ~300 total)
    questions_per_category = 30

    print(f"Generating questions for {state_name} from model knowledge...")
    for i, (cat_key, cat_desc) in enumerate(CATEGORIES):
        print(f"  [{i+1}/{len(CATEGORIES)}] {cat_key}...", end=" ", flush=True)

        # Generate in 2 batches of 15 to stay within token limits
        cat_questions = []
        for batch in range(2):
            batch_size = 15
            for attempt in range(3):
                try:
                    questions = generate_category_batch(
                        state_name, state_code, cat_key, cat_desc,
                        next_id, batch_size, existing_q_texts
                    )
                    for q in questions:
                        q["id"] = next_id
                        q["category"] = cat_key
                        next_id += 1
                    cat_questions.extend(questions)
                    existing_q_texts.extend(q["question"] for q in questions)
                    break
                except Exception as e:
                    if attempt < 2:
                        wait = 2 ** (attempt + 1)
                        print(f"retry in {wait}s ({e})...", end=" ", flush=True)
                        time.sleep(wait)
                    else:
                        print(f"batch FAILED: {e}", end=" ", flush=True)
            time.sleep(0.5)

        all_questions.extend(cat_questions)
        print(f"OK ({len(cat_questions)} questions, total: {len(all_questions)})")

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
