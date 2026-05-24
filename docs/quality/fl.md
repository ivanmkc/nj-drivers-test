# Florida (FL) — Quiz Quality Report

| Field | Value |
| --- | --- |
| State | Florida |
| Agency | DHSMV (Department of Highway Safety and Motor Vehicles) |
| Manual edition | **rev. 08/2023** (Official Florida Driver License Handbook) |
| Manual URL | https://www.flhsmv.gov/pdf/handbooks/englishdriverhandbook.pdf |
| Manual SHA-256 | `5c0b8e495f955b9ee030058489b74b8876614251462211774c97ce98fb9ed269` |
| Manual size | 104 pages, 216,941 chars extracted |
| Question count | 345 (327 LLM-generated + 18 sign-image) |
| Languages | en, es, ja |
| Passing score | 80% (50-question Class E Knowledge Exam) |

## Score

**Overall: A** (96/100)

| Axis | Grade | Notes |
| --- | --- | --- |
| Precision | **A** (99.4%) | 343/345 grounded, 2 partial (Q27, Q29), 0 fabricated |
| Recall    | **A** (100%)  | All 25 critical FL-specific topics are covered |
| Coverage  | **A-**        | All 10 canonical categories present; mild thinness in `alcohol_drugs_health` |

## Precision

### Method

1. **Mechanical pass** — for every non-sign question, normalize `question + correct-choice + explanation`, then search the manual for matching 5-grams (and 4-grams as fallback). Any question with `>=1` 5-gram hit or `>=2` 4-gram hits is considered mechanically grounded.
2. **Semantic pass** — every mechanically-ungrounded question (16) plus a random control sample of 10 mechanically-grounded questions were sent to `gemini-3.1-pro-preview` along with the most-relevant 5 KB window of the manual. The model labeled each as `grounded | partial | fabricated | not_in_excerpt`.
3. **Targeted regrep** — `not_in_excerpt` items were independently regex-checked against the full `manual_text.txt` to confirm whether the underlying fact appears anywhere in the manual (the LLM window selection was just narrow).

### Results

| Bucket | Count | % of total |
| --- | --- | --- |
| Mechanically grounded (>=1 5-gram or >=2 4-gram match) | 311 / 327 non-sign | 95.1% |
| Mechanically ungrounded but semantically grounded | 14 / 16 | 87.5% |
| Semantically partial | 2 (Q27, Q29) | — |
| Semantically fabricated | 0 | — |
| Sign questions grounded (manual lists each sign + meaning) | 18 / 18 | 100% |
| **Projected grounded across all 345 questions** | **343 / 345** | **99.4%** |

All 16 mechanically-flagged questions were verified — 14 were grounded paraphrases (the LLM-judge window simply didn't contain the right page, but a targeted `grep` against the full manual hit the relevant fact, e.g. `$48` initial license fee, `$130` reinstatement fee, `$150` PIP fee, `Minimum 180` DUI revocation, `12 inches` curb rule, `No Zone` definition, `Treat For Shock` first aid). The 10-question control sample showed 9 grounded, 1 `not_in_excerpt` whose fact (`$15 late fee`, Q80) was independently verified by regex.

### Flagged questions

| ID | Verdict | Issue |
| --- | --- | --- |
| Q27 | partial | Answer claim is correct (Drawbridge Signs is under "Specialized Signs and Signals"), but the explanation enumerates "Construction, Pedestrian, Railroad, and School Zone" as also being grouped there. Per the manual's table of contents (lines 497–515), Construction/Maintenance, Drawbridge, Pedestrian, Railroad Crossing, and School Zone are indeed all sub-sections of "Specialized Signs and Signals" — so the explanation is structurally accurate but the *literal* list never appears side-by-side in any single sentence. Reads as a faithful summary; flag is mostly a window/excerpt artifact. |
| Q29 | partial | Answer ("Golf Carts has a dedicated section in Sharing the Road") is correct. Explanation enumerates 6 sub-sections (Bicyclists, Commercial Motor Vehicles, Emergency Vehicles, Funeral Processions, Golf Carts, Low-Speed Vehicles) — all *do* have dedicated sections per the TOC (lines 657–697), but again as a structural summary rather than a quoted single sentence. Faithful; mostly window artifact. |

No fabricated questions. No factual contradictions with the manual.

## Recall

### Method

Passed the full 200 KB of `manual_text.txt` to `gemini-3.1-pro-preview` with the prompt: *"List the 25 most important topics a Florida Class E knowledge-test taker MUST know, focusing on Florida-specific items (No-Fault, school-zone enforcement, hurricane/weather, Move Over Law, point system, DUI/Implied Consent, etc.)"*. For each topic, scanned every question's `question + choices + explanation` for keyword hits.

### Results

| | Loose (≥1 keyword) | Strict (≥2 keywords) |
| --- | --- | --- |
| Topics with at least one matching question | **25 / 25 (100%)** | 25 / 25 (100%) |

### 25 critical topics (Gemini-extracted) and coverage

| # | Topic | Matching Qs |
| -: | --- | -: |
| 1 | Florida No-Fault Law & $10k PIP / $10k PDL minimums | 3 |
| 2 | School zone speed limits & camera enforcement fines | 14 |
| 3 | Move Over Law for emergency & disabled vehicles | 21 |
| 4 | Point system thresholds & suspension periods | 2 |
| 5 | DUI penalties, BAL limits & Implied Consent Law | 5 |
| 6 | Zero Tolerance Law for drivers under 21 (.02 BAL) | 8 |
| 7 | Minimum 3 feet clearance for passing bicyclists | 11 |
| 8 | Motorcycle sharing rules & full lane entitlement | 4 |
| 9 | Commercial vehicle No Zones & safe passing rules | 31 |
| 10 | Class E license GVWR cutoff (under 26,001 lbs) | 32 |
| 11 | Headlight requirements (sunset to sunrise & wipers on) | 2 |
| 12 | Child passenger safety seat & booster age requirements | 12 |
| 13 | Seat belt laws for front passengers & minors under 18 | 12 |
| 14 | Passing a stopped school bus penalties & camera rules | 18 |
| 15 | Standard speed limits (municipal, highway, school zones) | 27 |
| 16 | Turn signal distance requirement (100 feet before turn) | 75 |
| 17 | Traffic Law Substance Abuse Education (TLSAE) rules | 7 |
| 18 | Basic Driver Improvement (BDI) course mandatory triggers | 16 |
| 19 | Low visibility, fog, & rain driving rules | 31 |
| 20 | Right-of-way rules at open intersections & roundabouts | 26 |
| 21 | Traffic sign colors, shapes, & specific signage classes | 18 |
| 22 | Safe following distances (4 seconds in normal weather) | 7 |
| 23 | Littering penalties & points on driving record | 12 |
| 24 | Minor driving curfews & point restriction thresholds | 14 |
| 25 | Railroad crossing stops & dynamic envelope markings | 6 |

### FL-specific topic spot checks (requested in this verification task)

| FL-specific topic | Coverage |
| --- | --- |
| **Hurricane evacuation** | **Not covered — and the manual itself never mentions "hurricane" or "evacuation" in 216,941 chars.** This is a true gap in the *Official Florida Driver License Handbook*, not in our question bank. The handbook does cover hazardous-weather driving generically (rain, fog, smoke, flooded roads — see manual lines 5564–5598) and our questions reflect that (31 questions on low-visibility/rain/fog rules). Adding hurricane-evacuation questions would require either an external Florida Statutes source (FS §252) or noting "not covered by manual" in the question explanation, which our generator does not do. |
| **No-fault insurance ($10k PIP / $10k PDL)** | **Covered** — 5 questions reference PIP / PDL / No-Fault / Financial Responsibility (Q19, Q82, plus 3 others). Q19 names both laws; another question quizzes the exact $10k/$10k minimums; Q82 quizzes the $150 PIP reinstatement fee. |
| **School-zone rules** | **Well covered** — 14 questions hit "school zone" (HB 657 camera enforcement, $100 fine, 20 MPH limit, fines doubled, school zone signage). 18 additional questions cover school-bus passing (SB 766 / $200 civil penalty / camera enforced). Combined 32 questions on the school-zone/school-bus theme. |

## Coverage

### Category distribution (10 / 10 canonical categories present)

| Category | Questions | % | Status |
| --- | -: | -: | --- |
| safe_driving_rules | 71 | 20.6% | Heaviest (well under 40% cap) |
| license_system | 55 | 15.9% | |
| signs_and_signals | 43 | 12.5% | |
| penalties_and_points | 39 | 11.3% | |
| vehicle_information | 34 | 9.9% | |
| sharing_the_road | 29 | 8.4% | |
| defensive_driving | 27 | 7.8% | |
| driver_responsibility | 20 | 5.8% | |
| driver_testing | 16 | 4.6% | |
| alcohol_drugs_health | 11 | 3.2% | Lightest (see action below) |

- No missing categories.
- No category exceeds the 40% over-concentration threshold.
- `alcohol_drugs_health` is the lightest at 3.2%. Like other states, several DUI/Implied-Consent items live under `penalties_and_points` instead. Effective DUI-adjacent coverage (across both buckets) is meaningful, but a few more health-focused items (drowsy/drugged driving, vision standards, emotion/road-rage) would round it out.

### Question density vs manual size

- Manual: 216,941 chars (104 pages)
- Questions: 345
- Density: **1 question per 629 chars** (≈ 3.3 questions per page)

Density sits in the typical 500–1,000-chars-per-question band for this corpus. Not an outlier.

### Sign-question contribution

- 18 of 345 (5.2%) are sign-image questions
- 327 of 345 (94.8%) are LLM-generated from the manual text

Sign-question share is on the lower end versus other onboarded states (GA: 8.7%, NJ: ~10%). The manual's Chapter 6 (Traffic Controls) lists many warning, regulatory, and guide signs that could support 10–15 more image-tagged questions.

### Structural audit

`python3 tools/audit_questions.py fl` → **0 issues** (structural, duplicate, content, format).

## Recommended Actions

Priority ordered. None are blockers for shipping.

1. **(Low) Tighten Q27 and Q29 explanations** — Both questions are factually correct, but their explanations enumerate sub-section names as if quoting a single manual sentence. Either:
   - Rephrase the explanations to refer to the chapter's Table of Contents (e.g. *"Per the Chapter 6 TOC, Specialized Signs include Construction, Drawbridge, Pedestrian, Railroad Crossing, and School Zone signs."*), or
   - Trim the explanation to just the answer ("Drawbridge Signs & Signals appears under Specialized Signs and Signals.").

2. **(Low) Add 3–5 `alcohol_drugs_health` questions** — currently 11/345 (3.2%). The manual chapters 4 ("Before You Drive—You the Driver") and "Alcohol & Drug-Related Offenses" support more items on:
   - 0.08 / 0.04 / 0.02 BAL tiers (adult / CDL / under-21) — only partially quizzed
   - Drowsy driving (manual has a section)
   - Drugged driving (separate section)
   - Emotions / Road Rage (separate sections, manual p.36)
   - Vision standards for renewal

3. **(Low) Add 5–10 sign-image questions** — sign share is 5.2%, lower than peer states. The manual's Traffic Controls chapter (lines 479–574) supports adding more warning-, regulatory-, and guide-sign image questions from `data/signs/` (e.g. Winding Road, Drawbridge, Roundabout Ahead, Pedestrian Crossing).

4. **(Optional) Address the hurricane-evacuation gap** — A Florida driver's test app *without* hurricane-evacuation guidance is a noticeable omission *for users*, even though the official handbook doesn't address it. If we want this covered:
   - Pull from Florida Statutes §252 ("Emergency Management") or FDOT's hurricane evacuation route guidance, and
   - Either add a `manual_supplement.txt` for FL and re-run `generate_questions.py` with both sources, or add a single category-tagged "Florida Hazardous Weather" mini-section. Mark these questions clearly so their `explanation` does not falsely cite the Class E handbook.
   - Note: this should be a *product decision* (do we expand beyond the handbook?), not a question-bank bug.

5. **(Optional / monitoring)** When DHSMV publishes a 2024+ revision (current is rev. 08/2023), re-checksum `manual.pdf`, regenerate, and re-run this verification. Particular things to recheck: HB 657 (school-zone cameras), SB 766 (school-bus cameras), HB 949 (golf-cart minimum age), HB 425 (Move Over expansion), HB 1087 (job-training payment plans), SB 1718 (human-smuggling felony) — all of these are "PENDING STATUTE CHANGES FOR 2023" in the current handbook and may have evolved.

---

*Report generated 2026-04-29. Methodology: per `~/.claude/plans/agile-pondering-truffle.md`. Inputs: `data/states/fl/{questions_en.yaml, manual_text.txt, config.json, manual_provenance.json}` (read-only). Models: `gemini-3.1-pro-preview` for semantic precision and recall topic extraction (Vertex AI, project `adk-coding-agents`).*
