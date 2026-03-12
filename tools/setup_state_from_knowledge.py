#!/usr/bin/env python3
"""Set up a new state using Gemini's knowledge (no PDF needed).

Usage:
    python setup_state_from_knowledge.py <code> <name> <agency> <pass_pct> <test_count> [source_desc] [manual_url]
"""

import json
import os
import subprocess
import sys


def main():
    if len(sys.argv) < 6:
        print("Usage: python setup_state_from_knowledge.py <code> <name> <agency> <pass_pct> <test_count> [source_desc] [manual_url]")
        sys.exit(1)

    code = sys.argv[1].lower()
    name = sys.argv[2]
    agency = sys.argv[3]
    pass_pct = int(sys.argv[4])
    test_count = int(sys.argv[5])
    source = sys.argv[6] if len(sys.argv) > 6 else f"2025 {name} Driver's Manual"
    manual_url = sys.argv[7] if len(sys.argv) > 7 else ""

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state_dir = os.path.join(base_dir, "data", "states", code)
    os.makedirs(state_dir, exist_ok=True)

    # Create config.json
    config = {
        "code": code,
        "name": name,
        "agency": agency,
        "manual_url": manual_url,
        "passing_score_pct": pass_pct,
        "test_question_count": test_count,
        "source": source,
    }
    config_path = os.path.join(state_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    print(f"Created {config_path}")

    # Generate questions from knowledge
    questions_path = os.path.join(state_dir, "questions_en.yaml")
    if not os.path.exists(questions_path):
        print(f"\nGenerating questions for {name}...")
        subprocess.run([
            sys.executable, os.path.join(base_dir, "generate_questions_from_knowledge.py"), code
        ], check=True)
    else:
        print(f"Questions already exist: {questions_path}")

    # Add sign questions
    print(f"\nAdding sign questions...")
    subprocess.run([
        sys.executable, os.path.join(base_dir, "add_sign_questions.py"), code
    ], check=True)

    # Translate to Spanish only (skip Japanese per user request)
    translate_script = os.path.join(base_dir, "translate.py")
    es_path = os.path.join(state_dir, "questions_es.yaml")
    if not os.path.exists(es_path):
        print(f"\nTranslating to Spanish...")
        subprocess.run([sys.executable, translate_script, code, "es"], check=True)
    else:
        print(f"Spanish translation already exists: {es_path}")

    print(f"\n=== {name} ({code.upper()}) setup complete! ===")


if __name__ == "__main__":
    main()
