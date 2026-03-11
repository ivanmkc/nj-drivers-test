#!/usr/bin/env python3
"""Translate driver's test questions YAML to any language using Gemini.

Usage:
    python translate.py nj ja          # NJ questions -> Japanese
    python translate.py ny es          # NY questions -> Spanish
"""

import json
import os
import sys
import time
import yaml
from google import genai

MODEL = "gemini-3-flash-preview"
CLIENT = genai.Client(vertexai=True, project="adk-coding-agents", location="global")

LANG_NAMES = {
    "ja": "Japanese", "es": "Spanish", "zh": "Simplified Chinese",
    "ko": "Korean", "pt": "Portuguese", "fr": "French", "de": "German",
    "hi": "Hindi", "ar": "Arabic", "vi": "Vietnamese", "tl": "Tagalog", "ru": "Russian",
}


def get_system_prompt(lang_name: str) -> str:
    return f"""\
You are a professional English-to-{lang_name} translator specializing in driver education materials.
Translate the given questions, choices, and explanations into natural {lang_name}.
Keep the YAML structure keys (id, category, question, choices, answer, explanation) in English.
Keep choice labels (A, B, C, D) and answer values in English.
Keep category values in English.
Translate question text, choice text, and explanation text into {lang_name}.
Use polite/standard {lang_name} appropriate for a test-prep context.
For driving-specific terms, use the standard {lang_name} equivalents while keeping English abbreviations in parentheses where helpful (e.g., "BAC", "DUI", "GDL").
Preserve specific numbers, distances, speeds, fines, and legal references exactly.
Return valid JSON array only, no markdown fences."""


def translate_batch(questions: list[dict], lang_name: str) -> list[dict]:
    prompt = f"""\
Translate these driving test questions to {lang_name}. Return a JSON array with the same structure.

{json.dumps(questions, ensure_ascii=False, indent=2)}"""

    response = CLIENT.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=get_system_prompt(lang_name),
            temperature=0.1,
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
    if len(sys.argv) < 3:
        print("Usage: python translate.py <state_code> <lang_code>")
        print(f"  Languages: {', '.join(LANG_NAMES.keys())}")
        print("  Example: python translate.py nj ja")
        sys.exit(1)

    state_code = sys.argv[1].lower()
    lang_code = sys.argv[2].lower()
    lang_name = LANG_NAMES.get(lang_code)
    if not lang_name:
        print(f"Unknown language '{lang_code}'. Supported: {', '.join(LANG_NAMES.keys())}")
        sys.exit(1)

    state_dir = os.path.join(os.path.dirname(__file__), "states", state_code)
    input_path = os.path.join(state_dir, "questions_en.yaml")
    output_path = os.path.join(state_dir, f"questions_{lang_code}.yaml")

    if not os.path.exists(input_path):
        print(f"Source file not found: {input_path}")
        sys.exit(1)

    with open(input_path) as f:
        data = yaml.safe_load(f)

    questions = data["questions"]
    translated = []
    batch_size = 10
    total = len(questions)

    print(f"Translating {total} {state_code.upper()} questions to {lang_name} ({lang_code})...")

    for i in range(0, total, batch_size):
        batch = questions[i : i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        print(f"  Batch {batch_num}/{total_batches} (Q{batch[0]['id']}-Q{batch[-1]['id']})...", end=" ", flush=True)

        for attempt in range(3):
            try:
                result = translate_batch(batch, lang_name)
                translated.extend(result)
                print(f"OK ({len(result)} questions)")
                break
            except Exception as e:
                if attempt < 2:
                    wait = 2 ** (attempt + 1)
                    print(f"retry in {wait}s ({e})...", end=" ", flush=True)
                    time.sleep(wait)
                else:
                    print(f"FAILED: {e}")
                    translated.extend(batch)

        if i + batch_size < total:
            time.sleep(1)

    out_data = {
        "metadata": {
            "source": data["metadata"].get("source", ""),
            "source_original": data["metadata"].get("source", ""),
            "total_questions": len(translated),
            "language": lang_code,
            "categories": data["metadata"].get("categories", []),
        },
        "questions": translated,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(out_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\nDone! Wrote {len(translated)} questions to {output_path}")


if __name__ == "__main__":
    main()
