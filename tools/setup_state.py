#!/usr/bin/env python3
"""Set up a new state: download manual, extract text, create config, generate questions.

Usage:
    python setup_state.py <code> <name> <agency> <pass_pct> <test_count> <manual_url> [source_desc]

Example:
    python setup_state.py ca "California" "DMV" 83 46 "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/" "2025 California Driver Handbook"
"""

import json
import os
import subprocess
import sys


def main() -> None:
    if len(sys.argv) < 7:
        print(
            "Usage: python setup_state.py <code> <name> <agency> <pass_pct> <test_count> <manual_url> [source_desc]"
        )
        sys.exit(1)

    code = sys.argv[1].lower()
    name = sys.argv[2]
    agency = sys.argv[3]
    pass_pct = int(sys.argv[4])
    test_count = int(sys.argv[5])
    manual_url = sys.argv[6]
    source = sys.argv[7] if len(sys.argv) > 7 else f"2025 {name} Driver's Manual"

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

    # Download manual PDF if URL ends with .pdf
    manual_text_path = os.path.join("/tmp", f"{code}_manual_text.txt")
    pdf_path = os.path.join("/tmp", f"{code}_manual.pdf")

    if manual_url.endswith(".pdf"):
        if not os.path.exists(pdf_path):
            print(f"Downloading {manual_url}...")
            subprocess.run(["curl", "-sL", "-o", pdf_path, manual_url], check=True)
            print(f"Downloaded to {pdf_path}")
        else:
            print(f"PDF already exists: {pdf_path}")

        # Extract text
        if not os.path.exists(manual_text_path):
            print("Extracting text from PDF...")
            try:
                import fitz

                doc = fitz.open(pdf_path)
                text = ""
                for page in doc:
                    text += str(page.get_text()) + "\n"
                doc.close()
                with open(manual_text_path, "w") as f:
                    f.write(text)
                print(f"Extracted {len(text)} chars to {manual_text_path}")
            except ImportError:
                print("PyMuPDF not installed. Run: pip install pymupdf")
                sys.exit(1)
        else:
            print(f"Text already extracted: {manual_text_path}")
    else:
        print(
            f"Manual URL is not a PDF. You'll need to manually extract text to {manual_text_path}"
        )
        if not os.path.exists(manual_text_path):
            sys.exit(1)

    # Generate questions
    questions_path = os.path.join(state_dir, "questions_en.yaml")
    if not os.path.exists(questions_path):
        print(f"\nGenerating questions for {name}...")
        subprocess.run(
            [
                sys.executable,
                os.path.join(base_dir, "tools", "generate_questions.py"),
                code,
                manual_text_path,
            ],
            check=True,
        )
    else:
        print(f"Questions already exist: {questions_path}")

    # Add sign questions
    print("\nAdding sign questions...")
    subprocess.run(
        [sys.executable, os.path.join(base_dir, "tools", "add_sign_questions.py"), code],
        check=True,
    )

    # Translate
    translate_script = os.path.join(base_dir, "tools", "translate.py")
    for lang in ["es"]:
        lang_path = os.path.join(state_dir, f"questions_{lang}.yaml")
        if not os.path.exists(lang_path):
            print(f"\nTranslating to {lang}...")
            subprocess.run([sys.executable, translate_script, code, lang], check=True)
        else:
            print(f"Translation already exists: {lang_path}")

    print(f"\n=== {name} ({code.upper()}) setup complete! ===")


if __name__ == "__main__":
    main()
