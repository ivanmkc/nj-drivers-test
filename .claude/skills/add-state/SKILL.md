---
name: add-state
description: >
  Use this skill when the user wants to "add a new state", "onboard a state",
  "add jurisdiction", "import a state's manual", "set up <STATE>", or any
  variation of bringing a new US state, territory, Canadian province, or
  international jurisdiction into the question bank. Walks through the full
  pipeline: source the official manual, run `setup_state.py`, generate
  questions with Gemini, add sign questions, translate, audit, bundle, and
  smoke test on the platforms.

  Do NOT use this skill for: tweaking existing question wording (just edit the
  YAML), refreshing a stale manual URL only (no question regeneration needed —
  see the `refresh-manual-catalog` OpenSpec change), or general question-quality
  audits (`tools/audit_questions.py` is the entry point).
---

# Add a new state (or jurisdiction)

The pipeline is **YAML-source → bundle artifact → platforms**. Adding a state means producing a new `data/states/<code>/` directory grounded in the official manual, then letting `bundle.py` propagate it.

Reference docs already in the repo (read these first if anything below is unclear):
- [`README.md`](../../../README.md) §"Adding a New State" — the canonical short version
- [`CLAUDE.md`](../../../CLAUDE.md) — project-wide rules (line-length, audit threshold, "official sources only")
- [`SOURCES.md`](../../../SOURCES.md) — per-state metadata, useful as a template
- [`TODO_JURISDICTIONS.md`](../../../TODO_JURISDICTIONS.md) — what's done vs not
- [`INTERNATIONAL.md`](../../../INTERNATIONAL.md) — non-US jurisdictions and their caveats
- [`tools/manual_urls.json`](../../../tools/manual_urls.json) — catalog of (often stale) URLs

## Hard rules — never break these

1. **Ground every question in an official manual.** Never generate from LLM knowledge alone. Every entry's `explanation` must cite the manual.
2. **Official `.gov` hosts only.** Reject `driving-tests.org`, `dmvquestionbank.com`, `usdrivertraining.com`, etc. They mirror the same PDFs but they aren't authoritative.
3. **YAML is source; JSON/gzip is compiled.** Edit `data/states/<code>/questions_*.yaml`. Never edit `shared/questions_bundle.json` or any platform's copy under `Resources/`/`assets/`.
4. **English required; Spanish high-value.** Japanese is no longer in scope — do NOT generate `questions_ja.yaml` for new states. (Existing JA files for the 23 already-shipped states stay; just don't add more.)
5. **One state per PR/change.** Bundle artifacts churn; reviewing one state at a time keeps diffs sane.
6. **All Python tools run from the repo root** as `python3 tools/<script>.py`. Never `cd tools && python3 <script>.py` — the `_util.py` path resolution assumes repo-root cwd.

## Pipeline

### Step 0 — Verify the catalog entry (or find a fresh URL)

The URL in `tools/manual_urls.json` is probably stale. **Always verify before running anything.**

```bash
# Always pass a real UA — many state CDNs 403 default curl.
curl -sIL -A "Mozilla/5.0" "<candidate-url>" | grep -iE "^(HTTP|content-type|content-length|location)"
```

Acceptable verdicts:
- HTTP 200 + `Content-Type: application/pdf` + `Content-Length > 100KB` → use as-is.
- HTTP 200 + `Content-Type: text/html` → manual is web-only or split into chapters. See **Multi-source manuals** below.
- 302 → 200 → fine, same as above (note the final URL).
- 302 → 404, 403, "200 but tiny size" → URL is dead/blocked. **Find a new one.**

To find a new URL:
```bash
python3 tools/find_manuals.py <code>   # uses Gemini-with-Google-Search
```
Then re-verify with the curl command above. Update the entry in `tools/manual_urls.json` once you have a working URL.

### Step 1 — Run the onboarding pipeline

Single-PDF, happy path:
```bash
python3 tools/setup_state.py <code> "<Name>" "<AGENCY>" <pass_pct> <test_count> "<verified_url>" "<source_desc>"
# Example:
python3 tools/setup_state.py ga "Georgia" "DDS" 75 40 \
  "https://dds.georgia.gov/.../GeorgiaDriversManual.pdf" \
  "2026 Georgia Driver's Manual (dds.georgia.gov)"
```

This script chains: download PDF → extract text with PyMuPDF → write `config.json` → call `generate_questions.py` → call `add_sign_questions.py` → call `translate.py <code> es`. All side-effects land under `data/states/<code>/` plus `/tmp/<code>_manual.pdf`, `/tmp/<code>_manual_text.txt`.

If a sub-step is already done (existing `questions_en.yaml`, etc.), it's skipped — safe to re-run.

### Step 2 — Audit and bundle

```bash
python3 tools/audit_questions.py    # validates all states; expect zero new failures
python3 tools/bundle.py             # rebuilds shared/ + ios/Resources/ + android/assets/ + frontend/public/
ruff check . && ruff format --check . && pyright
```

If audit fails on the new state: don't relax the audit, fix the underlying questions (usually a missing/weak `explanation`).

### Step 3 — Spot-check 10 questions

Open `data/states/<code>/questions_en.yaml` and read 10 random entries. For each:
- The fact in `question`/`explanation` is in the manual you sourced.
- The `explanation` cites a chapter or page (e.g. "Ch. 4, p. 32").
- The correct answer matches the manual.

If multiple are wrong: re-check that the extracted text in `/tmp/<code>_manual_text.txt` is sensible (not garbled), then re-run `generate_questions.py`. If only 1-2 are wrong: hand-edit those YAML entries.

### Step 4 — Platform smoke tests

The bundle needs to actually load on each platform with the new state visible.

- **Web/frontend** (fastest): `cd frontend && npm run dev`, open localhost:5173, pick the new state, run a test, confirm pass/fail thresholds match the state's `passing_score_pct`/`test_question_count`.
- **iOS**: open `ios/DriversTest/DriversTest.xcodeproj` in Xcode, Cmd+R to a simulator, same checks. Bundle rebuilds via the Xcode run-script phase.
- **Android**: `cd android && ./gradlew assembleDebug`, install on emulator, same checks. Bundle rebuilds via the `bundleQuestions` Gradle task.

Skipping a platform is okay if you genuinely can't test it (no Mac, no emulator) — but **say so in the PR description**. Don't claim "tested on all platforms" if you didn't.

## Multi-source manuals (when the PDF doesn't exist or is split)

Some agencies (Michigan, Georgia as of 2025+) ship the manual as either:
- An HTML index of chapter links, **no single PDF.**
- Multiple chapter PDFs, no monolith.

`setup_state.py` only handles single PDFs natively. Workaround until [`refresh-manual-catalog`](../../../openspec/changes/refresh-manual-catalog/proposal.md) lands proper support:

1. Manually download each chapter PDF (or scrape each HTML chapter to text):
   ```bash
   for url in URL1 URL2 URL3; do
     curl -sL -A "Mozilla/5.0" -o "/tmp/<code>_part_$(basename $url).pdf" "$url"
   done
   ```
2. Extract each, then concatenate:
   ```bash
   python3 -c "
   import fitz, sys
   out = []
   for p in sys.argv[1:]:
       doc = fitz.open(p)
       out.append('\\n\\n=== ' + p + ' ===\\n\\n')
       for page in doc:
           out.append(page.get_text())
   open('/tmp/<code>_manual_text.txt', 'w').write(''.join(out))
   " /tmp/<code>_part_*.pdf
   ```
3. Set `manual_url` in `config.json` to the canonical entry-point URL (the contents page, not a single chapter), since this is what gets shown to users as the source citation.
4. Run the pipeline starting from `generate_questions.py` directly — `setup_state.py`'s download step is bypassed because the text file already exists.

Document any gotchas (page-number garbage, repeated chapter headers) in the PR so the proper multi-source feature can absorb them.

## What goes in `config.json`

```json
{
  "code": "ga",
  "name": "Georgia",
  "agency": "DDS",
  "manual_url": "https://dds.georgia.gov/...",
  "passing_score_pct": 75,
  "test_question_count": 40,
  "source": "2026 Georgia Driver's Manual (dds.georgia.gov)"
}
```

- `code`: lowercase 2-letter state code (`ga`, `mi`); for non-US use `<country>-<region>` like `ca-bc`, `au-nsw`.
- `passing_score_pct` and `test_question_count`: **verify on the official DMV/DOT site, not third-party.** These vary widely (FL: 80%/50, GA: 75%/40, NM: 72%/25, ID: 85%/40, MA: 72%/25).
- `source`: the human-readable citation that appears in the UI footer.

## Question YAML format (reminder)

```yaml
metadata:
  source: "Official Manual Name"
  total_questions: 307
  categories: [license_system, safe_driving_rules, ...]
questions:
  - id: 1
    category: "safe_driving_rules"
    question: "What should you do at a red light?"
    choices:
      A: "Speed up"
      B: "Stop"
      C: "Honk"
      D: "Reverse"
    answer: "B"
    explanation: "You must stop at a red light. (Ch. 4, p. 32)"
    image: "stop_sign.png"   # optional, only for sign questions
```

Valid categories (don't invent new ones — bundle audit will reject them):
`license_system`, `driver_testing`, `driver_responsibility`, `safe_driving_rules`, `defensive_driving`, `alcohol_drugs_health`, `penalties_and_points`, `sharing_the_road`, `vehicle_information`, `signs_and_signals`

## Pre-commit checklist

- [ ] `data/states/<code>/{config.json,questions_en.yaml}` exist; `questions_es.yaml` exists if reasonably possible.
- [ ] 10-question manual spot-check passed; explanations cite the manual.
- [ ] `tools/audit_questions.py` clean.
- [ ] `tools/bundle.py` produces a bundle including the new state with a sane size delta (typically +50-150KB per state).
- [ ] `ruff check . && ruff format --check . && pyright` green.
- [ ] At least one platform smoke-tested (state appears, test runs, pass/fail threshold correct).
- [ ] `tools/manual_urls.json` updated if the URL changed.
- [ ] `SOURCES.md` updated with the new state's entry (mirrors existing format).
- [ ] `TODO_JURISDICTIONS.md` checkbox flipped to `[x]`.
- [ ] **Generated bundle artifacts NOT committed** (`shared/`, `ios/.../Resources/`, `android/.../assets/`, `frontend/public/questions_bundle.json` are gitignored — never `git add` them).

## Don't do this

- Don't `git add shared/`, `frontend/public/questions_bundle.json`, or anything under `Resources/`/`assets/`. They're rebuilt every build.
- Don't generate questions from a manual you haven't read. If the extracted text is gibberish, fix that first.
- Don't pad question counts. ~250-450 questions per state is the established range. More isn't better; quality > quantity.
- Don't translate before English is final. Re-translation is expensive and the YAML diffs are noisy.
- Don't relax the audit script to make a state pass. Fix the questions.
- Don't add a state to multiple PRs at once. Bundle conflicts are painful.
- Don't trust `tools/manual_urls.json` blindly — verify with curl first.
