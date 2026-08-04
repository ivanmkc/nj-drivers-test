#!/usr/bin/env python3
"""Find official driver manual PDF URLs using Gemini with Google Search grounding.

Usage:
    python find_manuals.py                    # Find all missing states
    python find_manuals.py oh mi co az        # Find specific states
"""

import json
import os
import sys

from _util import strip_code_fences
from google import genai

MODEL = "gemini-2.5-flash"
CLIENT = genai.Client(vertexai=True, project="adk-coding-agents", location="global")

# All 50 US states + DC
ALL_STATES = {
    "al": ("Alabama", "ALEA"),
    "ak": ("Alaska", "DMV"),
    "az": ("Arizona", "MVD"),
    "ar": ("Arkansas", "DFA"),
    "ca": ("California", "DMV"),
    "co": ("Colorado", "DMV"),
    "ct": ("Connecticut", "DMV"),
    "dc": ("District of Columbia", "DMV"),
    "de": ("Delaware", "DMV"),
    "fl": ("Florida", "DHSMV"),
    "ga": ("Georgia", "DDS"),
    "hi": ("Hawaii", "DOT"),
    "id": ("Idaho", "ITD"),
    "il": ("Illinois", "SOS"),
    "in": ("Indiana", "BMV"),
    "ia": ("Iowa", "DOT"),
    "ks": ("Kansas", "DOR"),
    "ky": ("Kentucky", "KYTC"),
    "la": ("Louisiana", "OMV"),
    "me": ("Maine", "BMV"),
    "md": ("Maryland", "MVA"),
    "ma": ("Massachusetts", "RMV"),
    "mi": ("Michigan", "SOS"),
    "mn": ("Minnesota", "DVS"),
    "ms": ("Mississippi", "DPS"),
    "mo": ("Missouri", "DOR"),
    "mt": ("Montana", "DOJ"),
    "ne": ("Nebraska", "DMV"),
    "nv": ("Nevada", "DMV"),
    "nh": ("New Hampshire", "DOS"),
    "nj": ("New Jersey", "MVC"),
    "nm": ("New Mexico", "MVD"),
    "ny": ("New York", "DMV"),
    "nc": ("North Carolina", "DMV"),
    "nd": ("North Dakota", "DOT"),
    "oh": ("Ohio", "BMV"),
    "ok": ("Oklahoma", "DPS"),
    "or": ("Oregon", "DMV"),
    "pa": ("Pennsylvania", "PennDOT"),
    "ri": ("Rhode Island", "DMV"),
    "sc": ("South Carolina", "DMV"),
    "sd": ("South Dakota", "DPS"),
    "tn": ("Tennessee", "DOS"),
    "tx": ("Texas", "DPS"),
    "ut": ("Utah", "DLD"),
    "vt": ("Vermont", "DMV"),
    "va": ("Virginia", "DMV"),
    "wa": ("Washington", "DOL"),
    "wv": ("West Virginia", "DMV"),
    "wi": ("Wisconsin", "DMV"),
    "wy": ("Wyoming", "DOT"),
}


def find_existing():
    """Return set of state codes that already have question data."""
    base = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "states"
    )
    existing = set()
    for code in os.listdir(base):
        en_path = os.path.join(base, code, "questions_en.yaml")
        if os.path.exists(en_path):
            existing.add(code)
    return existing


def find_manual_urls(states: list[tuple[str, str, str]]) -> dict:
    """Use Gemini with Google Search to find manual PDF URLs for given states."""
    state_list = "\n".join(f"- {code}: {name} ({agency})" for code, name, agency in states)

    prompt = f"""Find the official driver's manual/handbook PDF download URL for each of these US states.
I need the DIRECT URL to the PDF file (ending in .pdf or a direct download link).
Search each state's DMV/DOT/DPS official website for their current driver manual.

States:
{state_list}

Return ONLY valid JSON (no markdown fences) in this format:
{{
  "results": [
    {{
      "code": "xx",
      "name": "State Name",
      "agency": "DMV",
      "manual_url": "https://...",
      "source_description": "2025 State Driver Manual (website.gov)",
      "passing_score_pct": 80,
      "test_question_count": 25
    }}
  ]
}}

For passing_score_pct and test_question_count, find the actual values from each state's DMV website.
If you cannot find a direct PDF URL for a state, set manual_url to null."""

    response = CLIENT.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            tools=[genai.types.Tool(google_search=genai.types.GoogleSearch())],
            temperature=0.1,
            max_output_tokens=8192,
        ),
    )

    if response.text is None:
        raise ValueError("Empty response from model")
    text = strip_code_fences(response.text)

    return json.loads(text)


def main() -> None:
    existing = find_existing()

    if len(sys.argv) > 1:
        codes = [c.lower() for c in sys.argv[1:]]
    else:
        codes = [c for c in ALL_STATES if c not in existing]

    if not codes:
        print("All states already have question data!")
        return

    states = [(c, ALL_STATES[c][0], ALL_STATES[c][1]) for c in codes if c in ALL_STATES]
    print(f"Searching for manual URLs for {len(states)} states...")

    # Process in batches of 10 to avoid overwhelming the model
    all_results = []
    for i in range(0, len(states), 10):
        batch = states[i : i + 10]
        batch_names = ", ".join(s[1] for s in batch)
        print(f"\n  Batch {i // 10 + 1}: {batch_names}...")
        try:
            data = find_manual_urls(batch)
            results = data.get("results", [])
            all_results.extend(results)
            for r in results:
                url = r.get("manual_url") or "NOT FOUND"
                print(f"    {r['code'].upper()}: {url}")
        except Exception as e:
            print(f"    ERROR: {e}")

    # Merge into the existing catalog (keyed by state code) so a partial run
    # never wipes previously-found entries.
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual_urls.json")
    catalog: dict[str, dict] = {}
    if os.path.exists(output_path):
        with open(output_path) as f:
            for entry in json.load(f):
                catalog[entry["code"]] = entry
    for r in all_results:
        catalog.setdefault(r["code"], {}).update(r)
    merged = sorted(catalog.values(), key=lambda e: e["code"])
    with open(output_path, "w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")

    found = [r for r in all_results if r.get("manual_url")]
    print(f"\nFound {len(found)}/{len(states)} manual URLs")
    print(f"Results saved to {output_path}")

    # Print setup commands for found states
    if found:
        print("\nRun these to process the found states:")
        for r in found:
            code = r["code"]
            name = r["name"]
            agency = r["agency"]
            pct = r.get("passing_score_pct", 80)
            count = r.get("test_question_count", 25)
            url = r["manual_url"]
            source = r.get("source_description", f"{name} Driver's Manual")
            print(
                f'  python3 tools/setup_state.py {code} "{name}" "{agency}" {pct} {count} "{url}" "{source}"'
            )


if __name__ == "__main__":
    main()
