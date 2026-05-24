# North Carolina (NC) Quality Verification Report

**State**: North Carolina
**Agency**: DMV
**Manual edition**: 2025 North Carolina Driver's Handbook (ncdot.gov), revised May 2025
**Manual provenance**: `manual.pdf` SHA-256 `54993e10…1e25eca` (108 pages, 7,951,616 bytes); `manual_text.txt` 228,540 chars extracted via PyMuPDF 1.27.2
**Question bank**: `data/states/nc/questions_en.yaml` — 376 questions (EN/ES/JA)
**Verified at**: 2026-04-29

## Score

| Axis | Grade | Notes |
| --- | --- | --- |
| Precision | A | 96.6% of non-sign questions land a verbatim 5-or-6-word phrase from the explanation or 4–5-word phrase from the correct answer inside the extracted manual text. All 12 phrase-mismatches were manually re-checked and **all 12 are in fact grounded** in the manual — the misses are caused by table/list formatting (the manual stores the fact as a 2-column table row that doesn't form a contiguous prose phrase). Effective precision is ~100%. |
| Recall | A | 38 of 39 critical-topic probes return ≥1 matching question (97%). The lone gap (Insurance Points / SDIP) corresponds to a topic the manual itself dismisses in three sentences with "contact your insurance agent" — not a meaningful omission. |
| Coverage | A− | All 10 canonical categories are present; none are over-concentrated (max 23.9% in `license_system`). Density is healthy (≈1 question per 608 chars, ≈3.5 questions per PDF page). Minor deduction: `driver_testing` (2.1%) and `driver_responsibility` (2.7%) are thin relative to the content available on those topics in Chapter 1 and the intro. |
| **Overall** | **A** | Question bank is well-grounded, broadly representative of the 2025 handbook, and categorically balanced. |

## Precision

Method: For each non-sign question, extract every 5-word and 6-word phrase from `explanation` and every 4-word and 5-word phrase from the correct-answer choice (after normalizing case, smart quotes, en/em-dashes, and whitespace). Mark "grounded" if any such phrase appears verbatim in `manual_text.txt`. Hand-review every "ungrounded" question against the manual.

| Bucket | Count | % of non-sign |
| --- | ---: | ---: |
| Total questions | 376 | — |
| Sign / image questions (excluded from phrase test) | 18 | — |
| **Non-sign questions evaluated** | **358** | **100.0%** |
| Phrase-grounded (automatic) | 346 | 96.6% |
| Phrase-missed but verified grounded on hand-review | 12 | 3.4% |
| Fabricated / unsupported | 0 | 0.0% |

### Hand-reviewed "phrase-mismatch" questions (all confirmed grounded)

| ID | Why the phrase matcher missed | Manual evidence |
| --- | --- | --- |
| 5 | Source is a bulleted list on p. 4, not prose | "Order Personalized Plates" appears verbatim in the Available Online Services list |
| 6 | Answer wording differs slightly | "A fee of $16.75 is charged and may be paid with any credit or debit card." |
| 56 | Source is Table 1 with mid-line wrapping | "No laminated copies or plastic replicas" appears in the birth-certificate row |
| 80 | Source is a TOC entry, not prose | "Vision, Traffic Signs, Knowledge Test, Driving Skills…" listed under Ch. 1 |
| 91 | Source is Table cell ("66 and older / 5 years") | Age-vs-duration table in renewal section |
| 102 | Source is dotted-leader fee table | "Restoration Fee (alcohol)…$167.25" in Schedule of Fees |
| 104 | Source is Table cell ("18–65 / 8 years") | Same age-vs-duration table |
| 349, 350, 351 | All three reference back-cover address block | "1515 N. Church Street, Rocky Mount, NC 27804 — no driver license/ID or title/registration services provided at this location" |
| 355 | URL appears in many places, but with non-phrase context | "MyNCDMV.gov" appears 40+ times |
| 358 | Date is inline mid-paragraph | "Revised May 2025." |

No fabricated content was detected. No claim was found that contradicts the manual.

## Recall

Method: 39 critical topics enumerated from the NC manual's table of contents (Chapters 1–7). For each topic, search the full question corpus (question + choices + explanation, normalized) for any matching keyword.

| # | Topic | Question hits |
| ---: | --- | ---: |
| 1 | Learner Permit eligibility / age | 15 |
| 2 | Graduated / Provisional licensing (15–18) | 15 |
| 3 | Required documents / proof of identity | 10 |
| 4 | Liability insurance requirement | 10 |
| 5 | REAL ID | 5 |
| 6 | Renewal of driver license | 18 |
| 7 | Duplicate license / address change | 4 |
| 8 | Identification cards | 16 |
| 9 | Driving While Impaired / BAC limits | 34 |
| 10 | Alcohol and the young driver | 1 |
| 11 | Driver license points | 11 |
| 12 | **Insurance points / SDIP** | **0 (gap)** |
| 13 | License suspension / revocation | 28 |
| 14 | Driver License Restoration | 5 |
| 15 | Seat belts and child restraints | 8 |
| 16 | Distracted driving / texting | 5 |
| 17 | Drowsy driving | 3 |
| 18 | Speed limits / speeding | 30 |
| 19 | Following distance (3–4 second rule) | 1 |
| 20 | Turning / lane changing / passing | 31 |
| 21 | Parking rules | 11 |
| 22 | Roundabouts / traffic circles | 10 |
| 23 | School buses | 9 |
| 24 | Emergency / law-enforcement vehicles (Move Over) | 19 |
| 25 | Funeral procession | 2 |
| 26 | Hazardous driving (rain / fog / snow / ice) | 142 |
| 27 | Night driving / sun glare | 13 |
| 28 | Work zones | 2 |
| 29 | Emergencies (brake failure / blowout / skid) | 5 |
| 30 | Crashes / reporting / hit-and-run | 17 |
| 31 | Traffic signals (red / yellow / green / flashing) | 34 |
| 32 | Pavement markings | 2 |
| 33 | Signs (regulatory / warning / guide colors & shapes) | 21 |
| 34 | Bicycles | 7 |
| 35 | Pedestrians | 20 |
| 36 | Trucks / no-zones | 21 |
| 37 | Motorcycles & mopeds | 14 |
| 38 | Vehicle registration / Tag & Tax | 19 |
| 39 | Vehicle emissions & inspection | 4 |

**Coverage**: 38 / 39 = **97%**.

The single gap is **Insurance Points / SDIP**. The manual itself devotes only three sentences to this topic ("Insurance companies use a different point system to determine insurance rates. If you have any questions concerning insurance points, contact your insurance agent.") and explicitly defers to outside expertise, so the omission is defensible.

Thin-but-not-missing topics worth noting: Following distance (1), Funeral procession (2), Work zones (2), Pavement markings (2), Drowsy driving (3), and Vehicle emissions & inspection (4). All are present but could be expanded.

## Coverage

### Category distribution (376 total)

| Category | Count | % of bank | Flag |
| --- | ---: | ---: | --- |
| license_system | 90 | 23.9% | — |
| safe_driving_rules | 76 | 20.2% | — |
| defensive_driving | 39 | 10.4% | — |
| vehicle_information | 39 | 10.4% | — |
| signs_and_signals | 38 | 10.1% | — |
| penalties_and_points | 34 | 9.0% | — |
| sharing_the_road | 28 | 7.4% | — |
| alcohol_drugs_health | 14 | 3.7% | — |
| driver_responsibility | 10 | 2.7% | thin |
| driver_testing | 8 | 2.1% | thin |

- No missing canonical categories.
- No over-concentration (>40% threshold) — top category is `license_system` at 23.9%, which is appropriate given Chapter 1 is the longest in the handbook.
- `driver_testing` and `driver_responsibility` are thin (<3%); some of their content (e.g. crash-reporting, driver-condition topics) has been classified under `defensive_driving` / `safe_driving_rules` instead, which is reasonable but does leave those two buckets feeling sparse.

### Density

- Manual extracted text: **228,540 chars** (108 PDF pages).
- Question bank: **376 questions** (358 LLM-derived + 18 sign-image).
- Density: **≈1 question per 608 chars**, **≈3.5 questions per PDF page**.

This is a healthy ratio — neither sparse (which would suggest under-coverage) nor dense (which would suggest padding with low-signal questions).

### Sign-question contribution

- 18 of 376 questions (4.8%) are image-tagged sign questions. NC's manual is text-heavy (Chapter 5 covers signs but is brief on regulatory inventory), so a smaller sign share than states like California or Texas is expected.

## Recommended Actions

These are improvement opportunities, not blockers. The bank is already in good shape.

1. **Optional: add 1–2 SDIP-aware questions** that mirror the manual's framing ("According to the NC Driver Handbook, where should you direct questions about insurance points?" → "Your insurance agent."), since the manual itself defers the substance of this topic.
2. **Expand thin but important topics** — consider adding questions on:
   - Following distance / 3- to 4-second rule (currently 1 question)
   - Work zones (currently 2; manual has a dedicated Hazardous Driving subsection)
   - Pavement markings (currently 2; would pair well with signs/signals questions)
   - Drowsy driving (currently 3; manual lists 5+ warning signs)
3. **Rebalance `driver_testing` and `driver_responsibility`** — these categories sit at 2.1% and 2.7%. Some currently-classified `safe_driving_rules` questions about crash duties, insurance proof, and on-road test conduct could be re-tagged into these buckets without rewriting content.
4. **Re-run this verification** after any future regeneration to make sure the high grounding rate is preserved.
