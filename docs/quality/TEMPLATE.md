# Quiz Verification Template

Apply this template to **every supported state** to produce `docs/quality/<code>.md` — a precision / recall / coverage report grounded in the actual source manual.

This template defines:
1. The inputs each verifier reads
2. The three verification passes (Precision, Recall, Coverage) with **exact** LLM prompts
3. The scoring rubric (letter grades A–F)
4. The required output report format (markdown skeleton)
5. Edge-case handling (recovered:false, very large/small banks, multi-source manuals)
6. Implementation hints (which Vertex AI model, which helper functions to reuse)

A verifier — agent OR script OR human — that follows this template precisely will produce a consistent, comparable report for any state in the bundle.

---

## 1. Inputs

For state `<code>` (e.g., `nj`):

| File | Purpose | Required |
|------|---------|----------|
| `data/states/<code>/questions_en.yaml` | The question bank being verified | Yes |
| `data/states/<code>/manual_text.txt` | Source of truth (PyMuPDF-extracted text) | Yes* |
| `data/states/<code>/config.json` | State metadata (passing %, count, agency, manual_url) | Yes |
| `data/states/<code>/manual_provenance.json` | Edition, SHA-256, source URL, `recovered` flag | Yes |
| `data/states/<code>/manual.pdf` | Source PDF (Git LFS) | Optional* |

\* If `manual_provenance.json` has `pdf.recovered: false`, the manual files won't exist on disk. See **Edge cases / Recovered:false** below.

**Critical rule**: **NEVER use the `Read` tool on a `.pdf` file**. PyMuPDF or `head -c 5 | od -c` only. PDF Read crashes the agent (confirmed multiple times in onboarding).

---

## 2. Verification passes

### 2.1 Precision pass

**Goal**: measure what fraction of questions have explanations that actually trace to the source manual (vs. fabricated content the LLM hallucinated).

**Step 1 — Mechanical pre-screen.**

For each question in `questions_en.yaml` where the `image` field is NOT set (skip sign questions):

```python
import re, yaml
qs = yaml.safe_load(open(f'data/states/{code}/questions_en.yaml'))['questions']
manual_text = open(f'data/states/{code}/manual_text.txt').read().lower()
non_sign = [q for q in qs if 'image' not in q]

def phrases(text, n=5):
    """Extract distinctive 4–6-word phrases from text."""
    words = re.findall(r"\b[a-z][a-z'-]*\b", text.lower())
    # Skip stopwords-only n-grams
    stop = {'the','a','an','is','are','of','to','in','on','for','with','and','or','that','this','it','at','by','from','as','be'}
    grams = []
    for i in range(len(words)-4):
        gram = words[i:i+5]
        if sum(1 for w in gram if w in stop) < 3:
            grams.append(' '.join(gram))
    return grams[:n]

results = []  # (qid, classification, evidence)
for q in non_sign:
    exp = q.get('explanation', '')
    grams = phrases(exp)
    if not grams:
        results.append((q['id'], 'queue', 'no-distinctive-phrases'))
        continue
    matches = sum(1 for g in grams if g in manual_text)
    rate = matches / len(grams)
    if rate >= 0.6:
        results.append((q['id'], 'grounded', f'{matches}/{len(grams)} phrases match'))
    elif rate >= 0.2:
        results.append((q['id'], 'queue', f'{matches}/{len(grams)} — partial'))
    else:
        results.append((q['id'], 'queue', f'{matches}/{len(grams)} — suspect'))
```

**Step 2 — Semantic LLM judge** (for `queue` results).

Send each queued question to Gemini with the **exact prompt below**, including the most-relevant 1500-char excerpt of `manual_text.txt`. To find the excerpt, search the manual for keywords from the question stem; take the surrounding ±750 chars. If no excerpt found, use the first 1500 chars.

Model: `gemini-3-flash-preview` (bulk; cheap). Client config:
```python
from google import genai
CLIENT = genai.Client(vertexai=True, project="adk-coding-agents", location="global")
```

Prompt (verbatim, do not modify):
```
You are auditing a driver's-test question against the source manual.

MANUAL EXCERPT (most relevant ~1500 chars):
{passage}

QUESTION (ID {qid}):
{question_text}

CHOICES:
A: {A}
B: {B}
C: {C}
D: {D}

STATED CORRECT ANSWER: {answer}
EXPLANATION: {explanation}

Reply with EXACTLY ONE of these three tokens (lowercase, no other text):
- grounded   — the manual supports both the answer and the explanation
- partial    — the manual partially supports (answer is correct but explanation embellishes, or vice versa)
- fabricated — the manual contradicts the answer/explanation, or the topic does not appear in the manual at all
```

Aggregate per-state:
- `n_grounded` = (mechanical grounded) + (LLM grounded)
- `n_partial`  = (LLM partial)
- `n_fabricated` = (LLM fabricated)
- `precision_rate` = n_grounded / total

**Cost control**: if non-sign question count > 400 (e.g., TN, PA, LA, KS), randomly sample 100 for LLM judge instead of all `queue` items. Note "(sampled)" in the report.

**Precision grade**:

| Grade | Threshold |
|-------|-----------|
| A | ≥ 95% grounded |
| B | 90% – 94% |
| C | 80% – 89% |
| D | 70% – 79% |
| F | < 70% |

---

### 2.2 Recall pass

**Goal**: measure what fraction of the manual's important topics are actually tested by at least one question.

**Step 1 — Extract critical topics from the manual.**

Send `manual_text.txt` to Gemini (truncate to first 50,000 chars if larger; that's typically more than enough to cover all key sections). Model: `gemini-3.1-pro-preview` (this needs high-quality output).

Prompt (verbatim, substitute `{state_name}`):
```
You are reviewing the {state_name} driver's manual to design a written knowledge test.

Identify EXACTLY 25 topics that any test-taker MUST know to pass the {state_name} written exam, based on the manual content below. Each topic should be a short noun-phrase or short clause (5–12 words). Cover a balanced spread of categories: rules of the road, signs/signals, right-of-way, parking, alcohol/drugs, penalties, safe driving, vehicle operation, sharing the road, licensing.

Return ONLY a JSON array of 25 strings, no commentary, no markdown fences.

Example shape:
["Right-of-way at uncontrolled intersections", "Maximum BAC for drivers 21+", ...]

MANUAL TEXT:
{manual_text_truncated}
```

Parse the response as JSON. If parse fails, retry once with explicit "Return ONLY valid JSON" emphasis.

**Step 2 — Match topics to questions.**

For each topic, extract its distinctive keywords (drop stopwords, keep nouns/verbs/numbers). A topic is **covered** if at least one question in `questions_en.yaml` matches:
- The topic's keywords appear (case-insensitive) in either `question` or `explanation`
- Use simple keyword set-overlap; ≥50% of topic keywords present → covered

```python
def keywords(topic):
    stop = {'the','a','an','is','are','of','to','in','on','for','with','and','or','at','by','from','as','be','must','should','your','you','any'}
    return {w.lower() for w in re.findall(r"\b[A-Za-z][A-Za-z'-]+\b", topic) if w.lower() not in stop and len(w) > 2}

def covers(question, topic_kw):
    text = (question['question'] + ' ' + question.get('explanation','')).lower()
    matched = sum(1 for kw in topic_kw if kw in text)
    return matched / max(len(topic_kw), 1) >= 0.5
```

`coverage_rate` = (topics with ≥1 covering question) / 25.

**Recall grade**:

| Grade | Threshold |
|-------|-----------|
| A | ≥ 90% (23–25 covered) |
| B | 80% – 89% (20–22) |
| C | 70% – 79% (18–19) |
| D | 60% – 69% (15–17) |
| F | < 60% (< 15) |

---

### 2.3 Coverage pass

**Goal**: measure category balance and question-bank density.

**Step 1 — Category distribution.**

Canonical categories (10):
```
license_system, driver_testing, driver_responsibility,
safe_driving_rules, defensive_driving, alcohol_drugs_health,
penalties_and_points, sharing_the_road, vehicle_information,
signs_and_signals
```

Compute counts and percentages per category. Flag:
- **Missing category** (0 questions): -5 points each
- **Over-concentration** (>40% of all questions in one category): -10 points
- **All 10 represented, no over-concentration**: 0 deductions

**Step 2 — Density.**

```
density = len(questions) / (len(manual_text) / 1000)
```
Expected range: **0.5 – 3.0** questions per 1000 chars of manual.

- Outside range → flag in report, but **no automatic deduction** (some manuals are exceptionally short or repetitive).

**Step 3 — Sign-question ratio.**

```
sign_ratio = count(image:-tagged) / total
```
Expected: ~10% (typical: 34 standard signs / ~300 total).

- < 5% or > 25%: flag, no deduction.

**Coverage grade**:

| Score (start 100, apply deductions) | Grade |
|-------------------------------------|-------|
| 90 – 100 | A |
| 80 – 89 | B |
| 70 – 79 | C |
| 60 – 69 | D |
| < 60 | F |

---

### 2.4 Overall grade

GPA-style average of (Precision, Recall, Coverage):

```
gpa_value = {A:4, B:3, C:2, D:1, F:0}
gpa = (gpa_value[P] + gpa_value[R] + gpa_value[C]) / 3
```

| GPA | Overall |
|-----|---------|
| ≥ 3.5 | A |
| ≥ 2.5 | B |
| ≥ 1.5 | C |
| ≥ 0.5 | D |
| < 0.5 | F |

---

## 3. Report format (`docs/quality/<code>.md`)

Use **exactly** this skeleton. Substitute `{placeholders}`. Do not add or rename H2 sections.

```markdown
# {State Name} ({CODE}) Quality Report

**Date**: {YYYY-MM-DD}
**Manual edition**: {edition from manual_provenance.json}
**Source URL**: {manual_url from config.json}
**Questions**: {total} (LLM-generated: {n_llm}, sign: {n_sign})

## Score

| Axis | Grade | Detail |
|------|-------|--------|
| Precision | {A-F} | {n_grounded}/{n_non_sign} grounded ({pct}%) |
| Recall    | {A-F} | {n_covered}/25 critical topics covered ({pct}%) |
| Coverage  | {A-F} | {brief: balanced / missing-cat / over-concentrated} |
| **Overall** | **{A-F}** | GPA {x.xx} |

## Precision

Total non-sign questions evaluated: {n}
- Grounded: {n_grounded} ({pct}%)
- Partial:  {n_partial}  ({pct}%)
- Fabricated: {n_fabricated} ({pct}%)
- LLM-judged subset: {n_judged} ({"sampled" if applicable})

### Flagged questions

| ID | Category | Verdict | Notes |
|----|----------|---------|-------|
| {Q#} | {cat} | partial | {short reason} |
| {Q#} | {cat} | fabricated | {short reason} |

(If empty: "No questions flagged — all explanations trace cleanly to the manual.")

## Recall

25 critical topics extracted from the manual:

| # | Topic | Covered? | Covering Q IDs |
|---|-------|----------|----------------|
| 1 | {topic 1} | ✓ | {ids} |
| 2 | {topic 2} | ✗ | — |
| ... | ... | ... | ... |

Coverage rate: {n_covered}/25 = {pct}%

## Coverage

### Category distribution

| Category | Count | % |
|----------|-------|---|
| license_system | {n} | {pct}% |
| driver_testing | {n} | {pct}% |
| ... | ... | ... |

{Flags: "Missing: <none>" or "Missing: penalties_and_points, vehicle_information"}
{"Over-concentration: signs_and_signals at 42%" — if applicable}

### Density

| Metric | Value | Notes |
|--------|-------|-------|
| Manual size | {n} chars | |
| Total questions | {n} | |
| Density | {x.xx} Qs / 1000 chars | Expected 0.5–3.0 |
| Sign questions | {n} ({pct}%) | Expected ~10% |

## Recommended Actions

- **Q{#}** ({state}): {short directive — "remove (fabricated content)" / "rewrite (explanation embellishes)" / "verify $X fine amount (2017 edition, may be outdated)"}
- **Topic gap**: {topic name} is in the manual but no question covers it. Consider adding 1–2 questions.

(If empty: "No specific actions; quiz is well-grounded and balanced.")
```

---

## 4. Edge cases

### 4.1 `recovered: false` states (e.g., IL, MA, SD as of 2026-05-23)

If `manual_provenance.json` has `pdf.recovered: false`, the manual files don't exist on disk. Produce this report:

```markdown
# {State Name} ({CODE}) Quality Report

**Date**: {YYYY-MM-DD}
**Status**: INCOMPLETE — source manual not recovered

## Score

| Axis | Grade |
|------|-------|
| Precision | N/A |
| Recall    | N/A |
| Coverage  | {grade from structural-only pass} |
| **Overall** | **INCOMPLETE** |

## Notes

- `manual_provenance.json` records `pdf.recovered: false`.
- Provenance note: "{note field from provenance}"
- Existing {n} questions cannot be precision- or recall-verified against the source manual.
- Coverage pass (categories, density, sign ratio) IS computed — those are structural.

## Recommended Actions

- Recover the source manual (browser-automation work tracked in `openspec/changes/refresh-manual-catalog/`).
- Once recovered: re-run verification per this template.
```

### 4.2 Very large question banks (> 500 non-sign questions)

States likely to hit this: **TN (874)**, **PA (507)**, **LA (588)**, **KS (468)**, **MA (456)**, **UT (427)**.

- Precision step 2 (LLM judge) sampled to **100 random `queue` questions** instead of all
- Add `(sampled)` to the Precision section header and `## Precision` table row
- Recall and Coverage proceed normally (cheap regardless of bank size)

### 4.3 Very small question banks (< 200 non-sign questions)

States likely to hit this: **MD (202 incl. signs)**, **AK (20+34)**, **VT (20+34)**.

- All three passes proceed normally
- If Recall is also low (< 70%): add a Recommended Action flagging probable under-coverage; suggest re-running generation with a longer-form prompt

### 4.4 Multi-source manuals (e.g., MI)

- `manual_text.txt` is the concatenated text from all `urls` entries
- `manual_part_*.pdf` files may also be present in `data/states/<code>/`
- Verification operates on the concatenated text — no special handling needed for the parts
- If chapter headers appear repeatedly in the text (a known multi-source artifact), they may inflate keyword-match noise; note in Recommended Actions if Precision is unexpectedly low

### 4.5 Stale-edition states (e.g., LA 2017, HI 2018)

- Specific dollar amounts (fines, fees), demerit-point values, BAC limits, and statutory references may be outdated
- During Precision, the LLM judge MAY mark questions as "fabricated" if the manual genuinely doesn't contain the specific number — that's correct behavior (the question may have been hallucinated against general knowledge)
- Add to Recommended Actions: "Source manual is from {year}; flag any questions citing specific dollar amounts or BAC limits for human review against current state law"

---

## 5. Implementation hints

### Helper functions to reuse

- `tools/_util.py:resolve_state_paths(code)` — returns dict of canonical file paths
- `tools/audit_questions.py:load_questions(code)` — returns `(questions, config)` tuple
- Vertex AI client config (from `tools/generate_questions.py:21-22`):
  ```python
  from google import genai
  CLIENT = genai.Client(vertexai=True, project="adk-coding-agents", location="global")
  ```

### Model selection

| Model | Use for |
|-------|---------|
| `gemini-3-flash-preview` | Bulk semantic precision judging (cheap, many calls) |
| `gemini-3.1-pro-preview` | Recall topic extraction (one call, high quality matters) |

### Pre-flight check

Before running the three passes, always run:
```bash
python3 tools/audit_questions.py <code>
```
to confirm structural validity. If audit fails, fix structural issues first; precision/recall results aren't meaningful on broken data.

### Output requirements

- File path: `docs/quality/<code>.md`
- Minimum size: 500 bytes
- Required H2 sections (in order): `## Score`, `## Precision`, `## Recall`, `## Coverage`, `## Recommended Actions`
- Encoding: UTF-8
- Trailing newline at EOF

### Performance budget

A typical state (~300 questions, ~200KB manual) should produce a report in 3–6 minutes:
- Precision: ~30s mechanical + ~2–4 min LLM judge (depends on queue size)
- Recall: ~30s LLM topic extraction + ~5s matching
- Coverage: < 5s (pure stats)

Total Gemini calls per state: typically 1 (recall) + 30–80 (precision judge) = ~30–80 calls. Vertex AI handles this easily within free-tier quotas.

---

## 6. Versioning

This template is **v1**. Future revisions may add:
- Semantic similarity (embeddings) instead of keyword matching for recall
- Per-category precision/recall sub-grades
- Cross-state comparison (e.g., "states whose CT/UT/AK precision is below median")
- ES-translation verification (current template covers only EN)

When changing the template, bump the version in the report header so old reports remain interpretable.
