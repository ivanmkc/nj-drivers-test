# Quiz Quality Verification — Arkansas (AR)

| Field | Value |
| --- | --- |
| State | Arkansas (AR) |
| Agency | ASP (Arkansas State Police) |
| Manual source | Arkansas Driver License Study Guide, Volume 1 - Edition 10 (January 2026) |
| Manual URL | https://dps.arkansas.gov/wp-content/uploads/Arkansas-DL-Manual-English.pdf |
| PDF SHA-256 | 8fa9d5d45daf072ca263c04508dfd5a48b3c429cf63366912e94f5a9fa51d8a0 |
| Manual pages / chars | 98 pages / 167,631 chars (extracted with PyMuPDF 1.27.2) |
| Total questions (EN) | 296 (262 text + 34 sign image) |
| Categories | 10 / 10 canonical categories present |
| Languages | EN / ES |
| Verified | 2026-04-29 |

## Score

| Axis | Grade | Detail |
| --- | --- | --- |
| Precision | A | 262 / 262 non-sign questions grounded (100%) |
| Recall | A | 25 / 25 critical Arkansas topics covered (100%) |
| Coverage | A | All 10 categories present; largest is `safe_driving_rules` at 24.3% (under 40% cap); density 1.77 Qs/1k chars (in 0.5–3.0 range); sign ratio 11.5% (near ideal 10%) |
| **Overall** | **A** | GPA 4.00 |

Notes: the mechanical 6-word distinctive-phrase sweep matched 249/262 (95.0%) directly; the 13 misses were all true-positives once inspected manually and re-confirmed with a `gemini-3-flash-preview` semantic judge using the full 167K-char manual as context. The 20-question Gemini audit (13 flagged + 7 randomly sampled controls) returned `grounded` for every single item with corroborating notes pointing to specific manual sections. No `partial`, no `fabricated`.

## Precision

Methodology: for each non-sign question, build 6-word distinctive phrases from the explanation (sliding window with 50% overlap) and grep against the normalised `manual_text.txt`. Phrase match → mechanically grounded; miss → escalated to Vertex AI Gemini judge (`gemini-3-flash-preview`) with the full manual as context for a semantic verdict (`grounded` / `partial` / `fabricated`).

| Bucket | Count | % of text Qs |
| --- | --- | --- |
| Mechanically grounded (≥1 distinctive 6-word phrase in manual) | 249 | 95.0% |
| LLM-judged grounded (after mechanical miss) | 13 | 5.0% |
| **Total grounded** | **262** | **100.0%** |
| Partial (claim partially supported) | 0 | 0.0% |
| Fabricated (claim contradicts or absent from manual) | 0 | 0.0% |
| Sign questions (not graded against manual text — generic MUTCD) | 34 | — |

### Flagged questions

All escalated questions came back `grounded`. No corrective action required.

| ID | Category | Verdict | Mechanical-miss reason (paraphrased meta-question) | Manual anchor |
| --- | --- | --- | --- | --- |
| 16  | driver_testing       | grounded | "AR Driver Testing" app name      | line 2105 ("AR Driver Testing" in Google Play / App Store) |
| 18  | license_system       | grounded | Lists Intermediate among graduated licenses | line 247 (Intermediate License section header) |
| 19  | license_system       | grounded | Class M = Motorcycle             | line 247-280 (Class M (Motorcycle) License) |
| 21  | safe_driving_rules   | grounded | Secondhand smoke under Ch. 1     | line 387 (Protection from Secondhand Smoke) |
| 23  | vehicle_information  | grounded | Faulty Accelerator in Ch. 9      | line 1854 (Faulty Accelerator subhead) |
| 24  | driver_testing       | grounded | Exhaust system in vehicle inspection | Chapter 10 vehicle-inspection list |
| 25  | license_system       | grounded | Class MD = Motor-driven Cycle    | Class MD section under licensing |
| 26  | alcohol_drugs_health | grounded | Epilepsy in Ch. 8 Health         | line 1720 (Epilepsy subhead) |
| 28  | safe_driving_rules   | grounded | Roundabouts under Right of Way   | line 870 (Roundabouts subhead inside Right of Way) |
| 30  | driver_testing       | grounded | 1-2-3 Skills Checklist           | line 2082 / line 5307 (1-2-3 Skills Checklist) |
| 54  | license_system       | grounded | IRS Tax Return as secondary doc  | line 2316 ("IRS Tax Return (W-2 Form is not acceptable)") |
| 126 | signs_and_signals    | grounded | Red curb = fire zone             | line 3579 ("Red curb means fire zone.") |
| 135 | defensive_driving    | grounded | Cognitive distraction definition | line 3746 ("Cognitive — Taking your mind off driving") |

Spot-checked precision on representative non-flagged claims (each matched the manual verbatim or near-verbatim):

- Q1: "first offense littering, $100–$1,000 fine" — matches lines 15-19 (8-6-404 (a)(1)(A)(i)).
- Q3: "fail to pay littering fines → 6-month license suspension" — matches lines 51-60 (8-6-404 (e)).
- Q31: "ACT 1289 of 2015 requires $5.00 fee per written exam" — matches lines 2114-2115.
- Q50: "minimum 140-degree field of vision with two functional eyes" — matches Vision Requirements section.
- Q215: "DWI threshold 0.08% BAC" — matches Alcohol and the Law section.
- Q217: "Underage DUI at 0.02%" — matches Alcohol and the Law section.
- Q240: "30 days to file accident report with Office of Driver Services" — matches Traffic Crashes section.
- Q100: "warning signs = yellow diamond with black symbols" — matches Warning Signs section.
- Q150: "signal after passing the intersection if turning just beyond" — matches Signaling section.
- Q200: "avoid dark/tinted lenses at night — reduce visible light" — matches Night Vision section.

No fabrication, no over-claim, no contradicted citation found across the 20-item LLM audit + 10 manual spot-checks.

## Recall

Methodology: enumerated the 25 most important driving topics for an Arkansas written-test taker. The list was cross-validated against a second list produced by `gemini-3-flash-preview` (asked to nominate the 25 must-know topics from the full manual text); both lists yielded 100% coverage when matched against the question bank by keyword sets (case-insensitive search across question + explanation + choices, ≥1 matching question per topic).

| #  | Critical topic | Questions | Sample IDs | Status |
| -- | --- | --- | --- | --- |
| 1  | Arkansas residency / 30-day rule           | 8  | 32, 33      | OK |
| 2  | Instruction permit / supervision           | 8  | 12, 34, 35  | OK |
| 3  | Intermediate License (curfew, passengers)  | 3  | 38, 39      | OK |
| 4  | Class M / MD / motorcycle licensing        | 5+ | 14, 19, 41, 42 | OK |
| 5  | Identification documents (primary/secondary)| 4 | 53, 54, 55  | OK |
| 6  | Seat Belt Law                              | 4  | 57, 61, 127 | OK |
| 7  | Child Passenger Protection Act             | 2  | 58, 59      | OK |
| 8  | Protection from Secondhand Smoke           | 2  | 21, 60      | OK |
| 9  | Arkansas Law on Littering (penalties)      | 4  | 1, 2, 3, 62 | OK |
| 10 | Move Over Law (emergency vehicles)         | 3  | 65, 85, 86  | OK |
| 11 | School Bus Law and Isaac's Law             | 6  | 66, 67, 68, 73 | OK |
| 12 | Traffic stop procedures (LEO)              | 4  | 5, 6, 8, 9  | OK |
| 13 | Work Zone fines (doubled / up to $5,000)   | 13 | 75, 77, 78  | OK |
| 14 | Lighted traffic signals & flashing arrows  | 18 | 91, 92, 93  | OK |
| 15 | Right on Red Rule                          | 3  | 94, 138     | OK |
| 16 | Stop / Yield / Speed limit signs           | 15 | 67, 90, 95  | OK |
| 17 | Railroad crossings (crossbuck / exempt)    | 4  | 102, 103, 105, 106 | OK |
| 18 | Pavement markings (yellow / white lines)   | 4  | 107, 108, 112 | OK |
| 19 | Roundabouts                                | 3  | 28          | OK |
| 20 | Right-of-way at intersections / pedestrians| 13 | 28, 91, 105, 114 | OK |
| 21 | Parking rules (hill, hydrant, distances)   | 8  | 121, 122, 123, 124 | OK |
| 22 | Distracted driving / cell phone law        | 6  | 40, 76, 134 | OK |
| 23 | Headlights, high/low beam, fog/rain use    | 11 | 143, 144, 146, 147 | OK |
| 24 | Following / stopping distance (2-3-4 sec)  | 4  | 167, 168, 197 | OK |
| 25 | Alcohol BAC limits + Underage DUI 0.02     | 5  | 215, 217, 218 | OK |

**Recall: 25/25 = 100%.**

Thinly-covered topics worth strengthening (still pass, but only 1–3 Qs):

- Child Passenger Protection Act (2 questions; only Q58 and Q59 cover the actual seat-stage thresholds). The manual section at lines 379-386 enumerates infant-seat, forward-facing, booster, and 60-lb / 6-year cutoffs — room for 2–3 more.
- Drugs (prescription, OTC, marijuana) only 3 questions (Q219, Q220, Q221). The Other Types of Drugs and Driving section at line 1790 supports more.
- Roundabouts (3 questions, of which two are sign-image based at Q277/281). The Roundabouts / How to Navigate Roundabouts subsections at lines 870-887 could justify one more dedicated navigation question.
- Hydroplaning has only Q156 + Q157 — the manual gives detail on speed thresholds and recovery behaviour that could carry a third question.

## Coverage

### Category distribution

| Category | Questions | % of total | Notes |
| --- | --- | --- | --- |
| safe_driving_rules    | 72 | 24.3% | Largest bucket but well under the 40% cap |
| signs_and_signals     | 48 | 16.2% | Includes 34 sign-image questions |
| sharing_the_road      | 33 | 11.1% | Trucks, bicycles, motorcycles, pedestrians |
| defensive_driving     | 29 |  9.8% | |
| license_system        | 22 |  7.4% | |
| driver_testing        | 21 |  7.1% | |
| vehicle_information   | 21 |  7.1% | |
| driver_responsibility | 20 |  6.8% | |
| penalties_and_points  | 19 |  6.4% | Littering, seat belt, work zone, DWI |
| alcohol_drugs_health  | 11 |  3.7% | Thin but proportional — Ch. 8 alcohol content is ~3 manual pages |

All 10 canonical categories present. No category exceeds the 40% over-concentration flag. The light weighting of `alcohol_drugs_health` (3.7%) reflects the actual proportional weight of Chapter 8 in the source manual; additional alcohol-related material (DWI penalties, refusal consequences) is correctly filed under `penalties_and_points`.

### Question count vs manual size

| Metric | Value | Notes |
| --- | --- | --- |
| Manual text length | 167,631 chars (98 pages) | |
| Total questions | 296 | |
| Density | 1.77 Qs / 1000 chars | Expected 0.5–3.0 — in range |
| Manual chars per question | 566 | |
| Sign questions | 34 (11.5%) | Expected ~10% — on target |

### Sign questions

34 sign questions (Q263–Q296) reference shared MUTCD-style images stored under `data/signs/` (e.g., `stop.png`, `yield.png`, `do_not_enter.png`, `railroad_crossbuck.png`, `school_zone.png`, `roundabout.png`). Universal U.S. signs — content correct per MUTCD; not graded against `manual_text.txt`.

### Structural audit

`python3 tools/audit_questions.py ar` → **0 issues** (all questions structurally valid, no within-state duplicates, all categories canonical).

## Recommended Actions

No blocking issues. The AR question bank is factually accurate, well-grounded in the source manual, and well-balanced. Nice-to-have improvements only:

1. **Expand Child Passenger Protection Act coverage** (currently 2 Qs). The manual at lines 379-386 specifies tiered restraint requirements by age/weight (infant-seat, forward-facing, booster, 60-lb / 6-year cutoffs); a question on each tier transition would strengthen recall.
2. **Add a hydroplaning recovery question** beyond Q156 / Q157 — manual covers the "do not brake / ease off accelerator / steer straight" sequence in actionable detail.
3. **Add 1–2 drug-impairment questions** (currently only Q219/Q220/Q221) — the Other Types of Drugs and Driving section at line 1790 supports questions on prescription-drug labelling, mixing alcohol + medication, and the specific marijuana effects enumerated.
4. **Add a roundabout-navigation question** distinct from the sign-image Q277 / Q281 — the manual's "How to Navigate Roundabouts" sub-section at line 887 enumerates the yield-then-merge sequence that is testable.
5. **Optional**: a question on the Underage Driving Under the Influence administrative penalties (driver license suspension durations, alcohol-education program) — the Alcohol and the Law section enumerates these and only Q217/Q218 currently touch them.

All five above are quality enhancements, not corrections — the existing 296-question bank requires no remediation.
