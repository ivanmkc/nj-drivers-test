# Missouri (MO) — Quiz Quality Verification

- **State**: Missouri
- **Agency**: DOR (Missouri Department of Revenue)
- **Manual**: Missouri Driver Guide ([dor.mo.gov](https://dor.mo.gov/forms/Driver%20Guide.pdf))
- **Edition**: Revised August 2025 ("2025 Missouri Driver Guide")
- **PDF**: 2,292,381 bytes, 102 pages, SHA-256 `861ad174501b46c3ec6f1ed7f9de73b4c60c9649b2b96fcdca815da937b1032c`
- **Extracted text**: 242,926 chars (PyMuPDF 1.27.2)
- **Question bank**: `data/states/mo/questions_en.yaml` — 394 questions (376 LLM-derived + 18 sign-image)
- **Translations available**: English, Spanish, Japanese
- **Structural audit**: `python3 tools/audit_questions.py mo` → **0 issues**

## Score

**Overall: A** (Precision A, Recall A, Coverage A)

| Axis | Grade | Notes |
|---|---|---|
| Precision | A | 95.7% of non-sign questions match distinctive 4–7-word phrases or grounded numeric/proper-noun anchors in the manual text. All 16 mechanically-flagged questions were manually verified and **every one of them is grounded** — mismatches were paraphrase shape, not fabrication. Adjusted: 100.0% grounded, 0 fabricated. |
| Recall | A | 38/38 critical Missouri driving topics covered (100%), including MO-specific items: GDL with the 6-month permit clock starting at temporary instruction permit issuance, the *55 cellular emergency number, lettered-road speed limits, the MIP / 30-day suspension for minors with BAC > .02, Class E for-hire licensing, and the Driver Condition Report (Form 4319). |
| Coverage  | A | All 10 canonical categories present and well balanced (top category 21.1%, well under the 40% over-concentration threshold). Density 16.2 Qs / 10k chars (1.62 Qs / 1k chars) — squarely in the healthy range. |

## Precision

Method: For every non-sign question, the `explanation` and the correct-choice text were tokenized and checked against `manual_text.txt` (case-insensitive, whitespace-normalized) using three independent grounding signals:

1. **Distinctive phrase match** — 4-, 5-, 6-, or 7-word n-gram (skipping stopword-heavy chunks) appears verbatim in the manual.
2. **Numeric/unit anchor match** — a number-with-unit (e.g., `30 days`, `55 mph`, `.02%`, `$1,000`) from the explanation appears in the manual.
3. **Proper-noun anchor match** — a multi-word capitalized term from the explanation (e.g., `Driver Condition Report`, `Troop F`) appears in the manual.

Questions scoring ≥ 2 on this combined signal are classified **grounded**; score < 2 is flagged for manual review.

| Bucket | Count | % of non-sign |
|---|---:|---:|
| Total non-sign questions | 376 | 100.0% |
| Mechanically grounded (score ≥ 2) | 360 | 95.7% |
| Strongly grounded (score ≥ 3, multi-signal) | 147 | 39.1% |
| Flagged for manual review (score < 2) | 16 | 4.3% |

The 16 flagged IDs (Q31, Q34, Q81, Q83, Q174, Q175, Q176, Q185, Q251, Q252, Q347, Q348, Q352, Q357, Q359, Q360) were manually inspected against the manual text. **All 16 are grounded** — every flagged claim traces to specific manual passages. Representative checks:

| ID | Claim | Manual evidence |
|---|---|---|
| Q31 | "Certified court order required for first or middle name change." | "First Name Change - Certified court order. Middle Name…" (Required Documents section) |
| Q34 | Restriction code 'C' = Daylight Driving Only | "This permit allows daylight driving only, within a 50-mile radius of home…" (Restrictions chart) |
| Q81/Q83 | Parallel-parking tested no more than 18 inches from curb | "Parking no more than 18" from the curb." (Driving Skills Test) — mechanical grep missed because manual uses the `18"` glyph, not `18 inches` |
| Q174 | Brown sign color = Public Recreation & Cultural Interests | "Brown = Public Recreation & Cultural Interests" (Sign Colors chart) |
| Q175 | Diamond shape = Warning signs | "Sign Shapes … Diamond = Warning" (Sign Shapes chart) |
| Q176 | Pentagon shape = School signs | "Pentagon = School" (Sign Shapes chart) |
| Q185 | Lettered roads speed limit 55 mph | "Lettered roads … 55" (Maximum Speed Guide) |
| Q251 | 1st MIP / BAC > .02 for minor → 30-day suspension | "MIP Minor in Possession 1st Offense — 30-day suspension" (Ch. 10 chart) |
| Q347 | BAC = Blood Alcohol Content | "the result of this test is known as your Blood Alcohol Content (BAC) level" |
| Q348 | Class E = For-Hire License | "For-Hire License (Class E) — Eligible Age: 18" |
| Q352 | Dial *55 for Highway Patrol Statewide Emergency Assistance | "exit the roadway to a safe area and dial *55 (or 911 if you are in a metropolitan area)" |
| Q357 | Troop F is located in Jefferson City | "Troop F, Jefferson City" (Contact Information page) |

The recurring reason for low mechanical score is that these questions cite chart/table cells (e.g., the Restriction Codes chart, Sign Shapes chart, Lettered Roads speed row, MIP penalty grid). PyMuPDF extraction breaks tabular content across short rows, so the 4-word n-gram patterns are spread across multiple lines and don't grep as contiguous strings — but the underlying claim is in the manual.

**Adjusted precision after manual inspection: 100.0% grounded, 0 partial, 0 fabricated.**

Sign questions (n=18) are excluded from this analysis — they are deterministically generated from `data/signs/` MUTCD imagery, not from the manual text, and audited separately by `tools/audit_questions.py`.

## Recall

Method: 38 critical Missouri driving topics were derived from the 2025 Driver Guide's table of contents and chapter section headings (Chapters 1–16 plus the GDL, Required Documents, and Contact Information sections). Each topic was matched against the union of `question + explanation + choices` text across all 394 questions using keyword set overlap.

**Coverage: 38 / 38 critical topics (100%)**

| # | Topic | # Qs | # | Topic | # Qs |
|---|---|---:|---|---|---:|
| 1  | Graduated Driver License / Instruction Permit | 19 | 20 | Roundabouts | 8 |
| 2  | License classes (A/B/C/E/F/M, ND) | 25 | 21 | Railroad crossings | 13 |
| 3  | Required documents (lawful status, identity, SSN, residency) | 10 | 22 | Sign colors & shapes | 14 |
| 4  | Vision, road sign, written, driving tests | 22 | 23 | Pavement markings (yellow/white lines) | 3 |
| 5  | License renewal & expiration | 18 | 24 | Adverse weather / night driving | 165 |
| 6  | Organ donor / medical alert / boater indicator | 5 | 25 | Work zones / construction | 10 |
| 7  | Restrictions & restriction codes | 6 | 26 | Alcohol/DUI/BAC limits & implied consent | 32 |
| 8  | Speed limits (interstate, urban, lettered, school) | 30 | 27 | Drugs & driving | 7 |
| 9  | Right-of-way / intersections | 32 | 28 | Distracted driving / texting / cell phone | 7 |
| 10 | Stop signs / yield / traffic signals | 38 | 29 | Seat belts & child restraints | 10 |
| 11 | Following distance / 2-3 second rule | 6 | 30 | Crashes / reporting / hit-and-run | 23 |
| 12 | Passing rules / no-passing zones | 18 | 31 | Mandatory insurance / financial responsibility | 16 |
| 13 | Turn signals & turning | 26 | 32 | Point system / suspension / revocation | 30 |
| 14 | Lane changes & merging | 45 | 33 | Vehicle titling and registration | 15 |
| 15 | Sharing the road: pedestrians | 25 | 34 | Safety & emissions inspection / required equipment | 9 |
| 16 | Sharing the road: motorcycles & bicycles | 23 | 35 | Commercial vehicles / CDL | 29 |
| 17 | Sharing the road: trucks / school buses / emergency vehicles | 34 | 36 | Sharing road with farm equipment | 5 |
| 18 | Parking rules / parallel parking / no-parking zones | 18 | 37 | Move-over law / emergency response | 9 |
| 19 | Highway / freeway / interstate driving | 50 | 38 | Tire & vehicle maintenance basics | 33 |

**Missouri-specific items confirmed:**

- **GDL 6-month permit clock starts at temporary instruction permit issuance** — Q5 ("The six-month permit period required for intermediate license does not start until the issuance of the temporary instruction permit.")
- **Motorcycle permit age 15½ (with rider course) vs 16 (without)** — Q6, Q7.
- **Class E For-Hire License** — Q9, Q12, Q15, Q16 (including the food-delivery/TNC exemptions).
- **Farm tractor exemption (agri-related purposes)** — Q14.
- **Driver Condition Report (Form 4319)** — Q36.
- **Lettered roads speed limit 55 mph** — Q185.
- **MIP penalty grid (30-day / 90-day / 1-year revocation)** — Q251, Q252.
- ***55 cellular emergency number** — Q162, Q352.
- **Troop F, Jefferson City** — Q357.
- **Parallel-parking spec "no more than 18" from the curb"** — Q81, Q83.

**Thin coverage** (flag, not fail):

- *Pavement markings (yellow/white lines)* — only 3 questions; the manual devotes meaningful prose to broken vs. solid line meaning in Chapter 7. Could justify 2–3 more questions.
- *Following distance / 2-3 second rule* — only 6 questions; common written-test topic that could absorb a couple more.
- *Restriction codes* — 6 questions; the manual lists ~12 codes (B, C, F, K, Z, …), and only a few are tested.
- *Drugs & driving (non-alcohol)* — 7 questions; Chapter 10 has standalone material on prescription medication and marijuana that could carry 2–3 more items.

## Coverage

### Category distribution

| Category | Count | % |
|---|---:|---:|
| safe_driving_rules | 83 | 21.1% |
| license_system | 57 | 14.5% |
| penalties_and_points | 43 | 10.9% |
| vehicle_information | 43 | 10.9% |
| signs_and_signals | 42 | 10.7% |
| defensive_driving | 41 | 10.4% |
| driver_testing | 26 | 6.6% |
| sharing_the_road | 26 | 6.6% |
| driver_responsibility | 23 | 5.8% |
| alcohol_drugs_health | 10 | 2.5% |
| **Total** | **394** | **100%** |

All 10 canonical categories present. Top category (`safe_driving_rules` at 21.1%) is well under the 40% over-concentration ceiling, and the top six categories are within a tight 10.4%–21.1% band — exceptionally even distribution. `alcohol_drugs_health` (2.5%) is the lightest slice and is notably thinner than the manual's Chapter 10 weight would suggest (the chapter spans 6 pages with detailed BAC, implied consent, MIP, and Abuse and Lose content).

### Question density

| Metric | Value | Notes |
|---|---|---|
| Manual text size | 242,926 chars | — |
| Total questions | 394 | — |
| LLM-generated questions | 376 | — |
| Density | **16.2 Qs / 10k chars** (1.62 Qs / 1k chars) | Squarely within the healthy 0.5–3.0 platform range |

### Sign-question contribution

- Sign questions (`image:`-tagged): 18 / 394 = **4.6%**
- LLM questions: 376 / 394 = 95.4%

Sign-question share is below the platform's typical ~10% (most states ship 34 MUTCD-derived sign questions; MO ships only 18). Not a defect — many of the standard sign types are also covered by the 42 text-only `signs_and_signals` questions — but adding ~16 more standard sign-image questions to bring MO in line with peer states is the single highest-leverage improvement.

## Recommended Actions

Quality is high; these are **enhancements**, not defects:

1. **Add ~16 sign-image questions** to bring MO from 18 to the platform-standard 34 MUTCD signs. Run `python3 tools/add_sign_questions.py mo` (or audit which standard signs are missing first). This is the single biggest gap relative to peer states.
2. **Add 4–5 `alcohol_drugs_health` questions** — category is currently the lightest at 2.5% (10 questions). Chapter 10 has plenty of material on Abuse and Lose, Implied Consent specifics, prescription/OTC drug warnings, and the "Drinking and Boating" sub-section that isn't yet tested. Target ~5% to match peer states.
3. **Add 2–3 `pavement markings` questions** — manual Chapter 7 covers broken vs. solid yellow/white line meaning in detail; current bank has only 3 questions touching that vocabulary.
4. **Add 1–2 `following distance` questions** — only 6 in the current bank; the 2- to 3-second rule is a staple written-test topic.
5. **Add 1–2 `restriction code` questions** — manual lists ~12 codes (B, C, F, K, Z, etc.); current bank tests only a couple.
6. **No fixes required for fabricated content** — precision audit found zero hallucinated claims after manual inspection of the 16 grep-missed items. Every flagged question is a paraphrase mismatch driven by PyMuPDF's tabular extraction, not a factual error.
7. **No changes needed to existing question wording.** Per project rules, the EN YAML is the source format; if questions are added, re-run `bundle.py` and re-translate ES/JA with `tools/translate.py`.

---

*Generated: 2026-04-29. Verifier methodology: `/home/ivanmkc/.claude/plans/agile-pondering-truffle.md`.*
