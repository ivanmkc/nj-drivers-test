# Illinois (IL) — Quiz Quality Verification

- **State**: Illinois
- **Agency**: Illinois Secretary of State (SOS)
- **Manual URL**: https://www.ilsos.gov/publications/pdf_publications/dsd_a112.pdf
- **Source description**: 2025 Illinois Rules of the Road (ilsos.gov)
- **Edition**: unknown (provenance edition field empty)
- **Question count (en)**: 413
- **Translations available**: English, Spanish
- **Manual recovered**: **NO** (`pdf.recovered: false` in `manual_provenance.json`)
- **Provenance note**: "URL ... returned intermittent HTTP/2 INTERNAL_ERROR / connection resets on 2026-04-29; manual download flaky from this server, will retry on next refresh; pre-existing question bank retained from prior onboarding."

## Score

**Grade: INCOMPLETE — source manual not recovered.**

Per the verification methodology (`/home/ivanmkc/.claude/plans/agile-pondering-truffle.md`), precision and recall scoring require a local copy of `manual_text.txt` (PyMuPDF-extracted from the official `manual.pdf`) so that each question's explanation can be grep-matched and LLM-judged against the manual. For Illinois, neither file exists on disk:

- `data/states/il/manual.pdf` — missing (download retried, server returned HTTP/2 INTERNAL_ERROR / connection resets on 2026-04-29)
- `data/states/il/manual_text.txt` — missing (no source text to extract from)
- `data/states/il/manual_provenance.json` — present but `pdf.recovered = false`, `text = {}`, `sources = []`

As a result, the 413 questions currently shipped for Illinois **cannot be precision-checked against their cited source** in this verification pass. The bank was retained from a prior onboarding run that did have access to the manual, but the source artifact required to re-validate it is not in the repository today.

Only the following dimensions can be scored from local artifacts:

| Dimension     | Grade | Notes                                                                   |
| ------------- | ----- | ----------------------------------------------------------------------- |
| Precision     | N/A   | Source manual not available; cannot grep/LLM-judge against ground truth |
| Recall        | N/A   | Cannot derive "must-know" topic list without manual text                |
| Coverage      | B+    | Healthy 10/10 category coverage; one category (license_system) heavy    |
| Structural    | A     | `tools/audit_questions.py il` → 0 issues (413 Qs, all fields valid)     |

## Precision

**Not measurable in this pass.**

The precision methodology requires:

1. Mechanical pass — grep distinctive 4–6-word phrases from each question's `explanation` against `manual_text.txt`.
2. Semantic pass — for un-matched questions (plus a random control sample), submit them to Gemini together with the relevant manual passage and ask whether the answer + explanation accurately reflect the manual.

Both passes are blocked because `manual_text.txt` does not exist. No fabricated/grounded counts can be reported.

**What is known about the bank from structural inspection** (not a precision substitute):

- 413 questions total; 18 sign questions carry an `image:` field, ~395 are LLM-generated text questions.
- Spot-reads of explanations show prose references to the source ("According to the manual...", "Step 4 of the REAL ID application process requires...", etc.), which is consistent with the prior onboarding having had the manual in context — but **none of these claims can be verified today** because the cited document is not present. Notably, explanations do not include page/chapter anchors (`Ch. X` / `p. Y`), so even after the manual is recovered, precision checking will rely on phrase matching and LLM judging rather than direct anchor lookups.
- `tools/audit_questions.py il` reports 0 issues: no within-state duplicates, all required fields populated, all answers map to a valid choice, all categories are canonical.

Flagged questions: **none flagged in this pass** — but absence of flags here is the absence of a check, not a clean bill of health.

## Recall

**Not measurable in this pass.**

The recall methodology requires sending `manual_text.txt` to Gemini to extract the 25 "must-know" topics, then matching each topic against the question bank. Without the manual text there is no authoritative topic list to match against, so no recall percentage can be computed.

A surface-level inspection of question categories does suggest the bank covers the standard Illinois topics one would expect — license tiers (GDL, REAL ID), DUI / BAC limits and zero-tolerance, school zones, work zones, sharing the road with motorcycles / bicycles / pedestrians / large vehicles, signs and signals, parking, points system — but confirming any of this against the actual SOS manual must wait until `manual.pdf` is successfully downloaded.

## Coverage

This dimension **can** be measured from local artifacts.

### Category distribution (10/10 canonical categories present)

| Category               |  Count | Share |
| ---------------------- | -----: | ----: |
| license_system         |    104 | 25.2% |
| safe_driving_rules     |     96 | 23.2% |
| signs_and_signals      |     47 | 11.4% |
| penalties_and_points   |     42 | 10.2% |
| vehicle_information    |     31 |  7.5% |
| sharing_the_road       |     30 |  7.3% |
| driver_responsibility  |     20 |  4.8% |
| defensive_driving      |     19 |  4.6% |
| alcohol_drugs_health   |     14 |  3.4% |
| driver_testing         |     10 |  2.4% |
| **Total**              |    413 |  100% |

- All 10 canonical categories are populated — no missing category.
- No category exceeds the 40% over-concentration threshold defined in the plan; the heaviest, `license_system` at 25.2%, is elevated but defensible for a state with a multi-tier GDL + REAL ID + commercial endorsement landscape.
- `alcohol_drugs_health` (3.4%) and `driver_testing` (2.4%) are the thinnest slices; that is typical across the 34-state baseline and not on its own a defect.

### Sign-question contribution

- 18 of 413 questions (~4.4%) carry an `image:` field (sign questions). The remaining 47 questions in the `signs_and_signals` category are text-only sign / signal items. Combined, the bank's signs/signals coverage is roughly 11.4% — in line with peer states.

### Question count vs manual size

- Cannot be computed: `manual_text.txt` length is unknown (file missing). The 413-question bank is on the larger end of the verified-state range (which spans ~202 [MD] to ~874 [TN]); whether 413 is proportional to the 2025 Illinois manual's actual content depends on a manual length number we do not have.

## Recommended Actions

Listed in priority order.

1. **Recover `manual.pdf` and regenerate `manual_text.txt`.** This is the single blocker for a real precision/recall grade. The `ilsos.gov` host was flaky on 2026-04-29. Suggested retry paths:
   - Re-run the download via `tools/refresh_state.py il` (or whichever wrapper the repo uses) on a different day / from a different network egress.
   - If the HTTP/2 error persists, fall back to HTTP/1.1 (`curl --http1.1 -L -o manual.pdf <url>`) — the symptom (HTTP/2 INTERNAL_ERROR + connection resets) is a known class of issue with some state SOS CDNs.
   - As a last resort, source the PDF from the Internet Archive snapshot of the same URL and update `manual_provenance.json` `sources[]` accordingly.
2. **Re-run this quality verifier** once `manual_text.txt` exists. The precision and recall sections will then produce actual numbers and a real letter grade. Do not treat the current "Coverage: B+" as a state-level grade — it is one of three dimensions.
3. **Hold the 413-question bank as-is in the meantime.** It passes structural audit and is internally consistent. Until the manual is re-recovered, regenerating questions would only swap one ungrounded bank for another.
4. **Track the staleness risk explicitly.** The provenance `edition` field is empty and `downloaded_at` is the placeholder `2026-04-29T12:00:00Z` from the backfill. Once the manual is recovered, populate `edition` (e.g. "2025") and the real `downloaded_at` so a future refresh job can detect drift.
5. **Consider tightening `license_system` (25.2%).** Not urgent and not a defect, but if a future regeneration pass happens, requesting a slightly flatter distribution (target ≤ 22% for any single category) would improve test-taker coverage of thinner topics like `alcohol_drugs_health` and `driver_testing`.
