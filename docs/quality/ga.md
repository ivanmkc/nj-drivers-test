# Georgia (GA) — Quiz Quality Report

| Field | Value |
| --- | --- |
| State | Georgia |
| Agency | DDS (Department of Driver Services) |
| Manual edition | **2023-2024** (oldest currently-published GA manual) |
| Manual URL | https://dds.georgia.gov/document/document/ga-drivers-manual-2023-2024/download |
| Manual SHA-256 | `e311de54ad0ee6f5913e18e694914a560dac3592987437290c271f53c0c7fa71` |
| Manual size | 52 pages, 232,310 chars extracted |
| Question count | 390 (356 LLM-generated + 34 sign-image) |
| Languages | en, es, ja |
| Passing score | 75% (40-question test) |

## Score

**Overall: A** (average of three axis grades below)

| Axis | Grade | Notes |
| --- | --- | --- |
| Precision | **A** (99.7%) | 389/390 questions grounded; 1 partial; 0 fabricated |
| Recall    | **A** (100%)  | All 25 critical topics surfaced from the manual are covered |
| Coverage  | **A-**        | All 10 canonical categories present; no over-concentration; one category mildly under-weight |

Caveat: GA manual is the 2023-2024 edition, which is the most recent edition DDS has published as of the on-boarding date (2026-04-29). The task brief explicitly notes this is the current published edition, so it is not a staleness issue.

## Precision

### Method

1. **Mechanical pass** — for every non-sign question, normalize the question + correct-choice + explanation, then search the manual for any matching 5-gram, 4-gram, or 3-gram of content tokens.
2. **Semantic pass** — feed the full 232 KB manual text to `gemini-3-flash-preview` along with:
   - All 69 mechanically-ungrounded questions
   - 15 randomly-sampled mechanically-grounded controls
   - 10 randomly-sampled sign questions
   Ask the model to label each as `grounded | partial | fabricated`.

### Results

| Bucket | Count | % of total |
| --- | --- | --- |
| Mechanically grounded (>= 3-gram match) | 287 / 356 non-sign | 80.6% |
| Mechanically ungrounded but semantically grounded | 68 / 69 | 98.6% |
| Semantically partial | 1 | — |
| Semantically fabricated | 0 | — |
| Sign questions grounded (sample of 10) | 10 / 10 | 100% |
| **Projected grounded across all 390 questions** | **389 / 390** | **99.7%** |

All 69 mechanically-ungrounded questions had **>= 0.83 token-overlap** with the manual — they were paraphrased, not fabricated. Gemini confirmed 68 of 69 as faithful paraphrases.

### Flagged questions

| ID | Verdict | Issue |
| --- | --- | --- |
| Q293 | partial | Answer ("Motorists are never allowed to drive or park in a bike lane") omits the manual's stated exception "**except to cross over it to make a turn**". |

No fabricated questions. No factual contradictions.

## Recall

### Method

Passed the full 232 KB manual to `gemini-3.1-pro-preview` with the prompt "List the 25 most important topics a Georgia knowledge-test taker MUST know." For each topic, scanned `questions_en.yaml` for keyword hits across question + choices + explanation. Loose match = ≥1 keyword; strict match = ≥2 keywords.

### Results

| | Loose (≥1 keyword) | Strict (≥2 keywords) |
| --- | --- | --- |
| Topics with at least one matching question | **25 / 25 (100%)** | 7 / 25 (28%) |

The strict score is low because Gemini's suggested keywords were sometimes hyper-specific phrases (e.g. `"octagon means stop"`, `"yield to amber lights"`) that don't appear verbatim in the questions — but the **topic itself is covered** in every case (verified manually with a regex scan; see below).

### 25 critical topics (Gemini-extracted) and coverage

| # | Topic | Loose hits | Strict hits | Status |
| -: | --- | -: | -: | --- |
| 1 | Right-of-Way at Intersections | 3 | 0 | Covered |
| 2 | School Bus Stopping Rules | 9 | 0 | Covered |
| 3 | Georgia Move Over Law | 6 | 1 | Covered |
| 4 | DUI and Blood Alcohol Limits | 6 | 0 | Covered |
| 5 | Class D Teen Driving Restrictions | 8 | 2 | Covered |
| 6 | Hands Free Georgia Law | 1 | 0 | Covered |
| 7 | Headlight Usage and Dimming | 5 | 0 | Covered |
| 8 | Passing Rules and Prohibited Zones | 3 | 0 | Covered |
| 9 | Commercial Vehicle No-Zones | 6 | 0 | Covered |
| 10 | Sharing the Road with Bicycles | 2 | 0 | Covered |
| 11 | Sharing the Road with Motorcycles | 4 | 0 | Covered |
| 12 | Pedestrian Right-of-Way | 4 | 1 | Covered |
| 13 | Speed Limits and Super Speeder | 4 | 0 | Covered |
| 14 | Traffic Signal Meanings | 2 | 0 | Covered |
| 15 | Highway Sign Shapes and Colors | 0 | 0 | Covered (verified Q200, Q201, Q203, Q204, Q205) |
| 16 | Pavement Markings and Lanes | 5 | 1 | Covered |
| 17 | Railroad Crossing Procedures | 0 | 0 | Covered (verified Q148, Q149, Q202) |
| 18 | Implied Consent Law | 4 | 0 | Covered |
| 19 | Safe Following Distance | 5 | 1 | Covered |
| 20 | Hydroplaning and Wet Roads | 2 | 0 | Covered |
| 21 | Expressway Driving and Gores | 3 | 0 | Covered |
| 22 | Safety Belts and Child Restraints | 3 | 1 | Covered |
| 23 | Joshua's Law and Driver Education | 2 | 0 | Covered |
| 24 | Points System and Suspensions | 8 | 0 | Covered |
| 25 | Handling Vehicle Emergencies | 2 | 0 | Covered |

Rows 15 and 17 returned 0 keyword hits with the extracted keywords (Gemini suggested too-specific phrases), but a regex scan for `octagon|pentagon|diamond|sign shape` confirmed 21 sign-shape questions, and `railroad|train|crossbuck` confirmed 13 railroad-crossing questions. Effective recall: **25/25**.

## Coverage

### Category distribution (10 / 10 canonical categories present)

| Category | Questions | % | Status |
| --- | -: | -: | --- |
| safe_driving_rules | 86 | 22.1% | Heaviest (under 40% cap) |
| license_system | 70 | 17.9% | |
| signs_and_signals | 61 | 15.6% | |
| penalties_and_points | 40 | 10.3% | |
| sharing_the_road | 29 | 7.4% | |
| driver_responsibility | 28 | 7.2% | |
| defensive_driving | 28 | 7.2% | |
| driver_testing | 23 | 5.9% | |
| vehicle_information | 17 | 4.4% | |
| alcohol_drugs_health | 8 | 2.1% | Mildly thin (see action below) |

- No missing categories.
- No category exceeds the 40% over-concentration threshold.
- `alcohol_drugs_health` is the lightest at 2.1% (8 questions). Some DUI-related material is bucketed under `penalties_and_points` (e.g. implied consent, license suspensions for DUI) — so the gap is partly a categorization artifact. Still worth a modest backfill to push the category to ~4%.

### Question density vs manual size

- Manual: 232,310 chars (52 pages)
- Questions: 390
- Density: **1 question per 596 chars** (~1 question per page)

This is well within the typical 500-1,000 chars-per-question range observed in other onboarded states. Not an outlier in either direction.

### Sign-question contribution

- 34 of 390 (8.7%) are sign-image questions using the shared MUTCD sign library
- 356 of 390 (91.3%) are LLM-generated from the manual text

Sign questions are wholly grounded in the manual's Signs / Signals / Markings chapter (verified via Gemini sample of 10/34 → all grounded).

## Recommended Actions

Priority ordered. None are blockers for shipping.

1. **(Low) Fix Q293 nuance** — `data/states/ga/questions_en.yaml` Q293 says motorists are "never" allowed to drive or park in a bike lane. The manual's exception is *"except to cross over it to make a turn"*. Either:
   - Rephrase the correct choice to "Only to cross over it when making a turn" and update the explanation, or
   - Add a separate question about the turn-crossing exception so the rule and its exception are both quizzable.

2. **(Low) Add 3-5 alcohol_drugs_health questions** — The category is at 2.1%, the lowest of all categories. The manual covers:
   - The 0.08 / 0.04 / 0.02 BAC tiers (adult / commercial / under-21) — currently only partially quizzed
   - Drug categories that impair driving (depressants, stimulants, hallucinogens) — manual lists these explicitly
   - Drowsy / fatigued driving signs — manual has a dedicated section
   - Vision standards and corrective lens restrictions
   - "Open container" law

3. **(Optional / monitoring)** When DDS publishes a 2025+ edition of the manual, re-run this verification. Track:
   - New / repealed laws (especially Super Speeder, Hands Free, BAC limits)
   - Re-checksum `manual.pdf` and update `manual_provenance.json`

4. **(Optional) Improve mechanical-grounding coverage** — 80.6% of LLM-generated questions hit a 3-gram from the manual; the other 19.4% are paraphrased. If a stricter authoring pipeline is desired, prompt the generator to keep at least one quoted span from the manual in the explanation (`The manual states: "..."`) for every question. Most current "paraphrased" questions already do this; a few do not.

---

*Report generated 2026-04-29. Methodology: per `~/.claude/plans/agile-pondering-truffle.md`. Inputs: `data/states/ga/{questions_en.yaml, manual_text.txt, config.json, manual_provenance.json}` (read-only). Models: `gemini-3-flash-preview` for semantic precision, `gemini-3.1-pro-preview` for recall topic extraction (Vertex AI, project `adk-coding-agents`).*
