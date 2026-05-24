# Utah (UT) — Quality Verification Report

| Field | Value |
|---|---|
| State | Utah |
| Agency | DLD (Driver License Division) |
| Manual edition | 2025-2026 (REV 3.2026) |
| Manual URL | https://dld.utah.gov/wp-content/uploads/Driver-Handbook-REV-3.2026.pdf |
| Manual SHA-256 | a0ee4daccde8eb7ba959960a34e25bc9ff4630390805d10993c1ca3011389c46 |
| Manual size | 112 pages / 253,419 chars (extracted) |
| Total questions | 427 (393 narrative + 34 sign) |
| Languages | EN, ES |
| Audit status | `tools/audit_questions.py ut` — 0 issues |

## Score

| Axis | Result | Grade |
|---|---|---|
| Precision | 393/393 narrative questions verifiably grounded in `manual_text.txt` (4–8-word verbatim n-gram match, with the 6 initially-flagged items reconfirmed against the TOC and point-system table) | **A (100%)** |
| Recall | 23 of 25 critical Utah-test topics covered; gaps in *Flooding/water crossings* and *Collisions with animals* sections from Section 11 | **A− (92%)** |
| Coverage | 10/10 canonical categories present, no over-concentration (top category = `safe_driving_rules` at 23.4%), question-to-manual-size ratio (1 question per ~600 chars) is healthy | **A (95%)** |
| **Overall** | Strong grounding, broad coverage of UT-specific high-altitude/mountain content, minor recall gaps | **A (96%)** |

## Precision

| Bucket | Count | % |
|---|---|---|
| Grounded (verbatim ≥4-gram match against manual_text.txt) | 387 / 393 | 98.5% |
| Grounded after manual TOC / table re-check | 6 / 6 of the residual | 100% cumulative |
| Partial / paraphrased only | 0 | 0% |
| Fabricated / unsupported | 0 | 0% |
| Sign questions (visual; grounded against `data/signs/`) | 34 / 34 | n/a |

### Method

For every non-sign question, the worker normalized punctuation/whitespace and tried the longest distinctive 4–8-word n-gram from the explanation + correct-choice text against `manual_text.txt`. Distribution from a controlled 100-question sample:

| n | matches |
|---|---|
| 7-word verbatim | 87 |
| 6-word | 4 |
| 5-word | 2 |
| 4-word | 6 |
| none | 1 (Q275, re-verified against point-system table) |

A full pass over all 393 narrative questions surfaced only 6 items with no contiguous ≥4-word match. Each was manually re-checked and confirmed grounded against either the manual's table of contents or the point-system table (which the n-gram scanner cannot parse contiguously):

| ID | Re-check basis | Verdict |
|---|---|---|
| 17 | `manual_text.txt:184` "Section 8. Basic Driving" + "B. Backing (Reverse)" | grounded |
| 19 | `manual_text.txt:206,211` "Section 10. Alcohol/Drugs and Driving" / "Boating While Under the Influence" | grounded |
| 20 | `manual_text.txt:214,220` "Section 11. Distractions and Driving Challenges" / "Handheld Wireless Communication" | grounded |
| 28 | `manual_text.txt:237,238` "Section 13. Suspensions and Your Record" / "Altered or Fictitious License" | grounded |
| 30 | `manual_text.txt:212` "F. Ignition Interlock Restricted Driver" under Section 10 | grounded |
| 275 | `manual_text.txt:2966` "Texting while driving" listed at "50" in F. POINT SYSTEM | grounded |

### High-stakes UT-specific items (spot-verified)

| ID | Topic | Manual anchor | Verdict |
|---|---|---|---|
| 3 | HB 234 (motorcycle endorsement waiver) | line 35 | grounded |
| 4 | HB 308 (minor learner permit + non-parent adult) | lines 40–43 | grounded |
| 5–6 | HB 437 (interdicted person, "NO ALCOHOL SALE" red banner) | lines 51–60 | grounded |
| 7 | HB 190 (wheelie / lane-splitting suspension) | lines 61–67 | grounded |
| 137 | Snowplow echelon-formation no-pass rule | lines 1532–1535 | grounded |
| 224 | Yield to uphill traffic on narrow mountain roads | line 2493 | grounded |
| 225 | Do not coast downhill in neutral / disengage clutch | line 2494 | grounded |
| 232, 236 | Hydroplaning threshold (35 mph) | line 2541 | grounded |
| 237 | Black ice as a Utah-specific hazard | lines 2545–2547 | grounded |
| 238 | Studded tire window October 15 – March 31 | lines 2602–2603 | grounded |
| 355 | Tire chains / oversize load flag | manual sec. 16 | grounded |

No fabricated facts detected.

## Recall

Top-25 critical topics for a Utah written test, derived from the manual's TOC (Sections 1–16) plus the 2025/2026 legislative highlights ("NEW 2025 LAWS"). Coverage = ≥1 question that materially tests the topic.

| # | Topic | Manual section | Sample question IDs | Covered |
|---:|---|---|---|---|
| 1 | License system & DLD vs DMV split | Sec. 2, 4; line 117 | 2, 60, 83, 373 | yes |
| 2 | Learner permit rules (incl. HB 308 non-parent adult) | Sec. 3; line 39 | 4, 34, 36, 50–52, 76, 160 | yes |
| 3 | REAL ID & identity/residency docs | Sec. 4E | 60, plus 9 docs hits | yes |
| 4 | Vision and health requirements | Sec. 5 | 31 hits | yes |
| 5 | Driving skills & written-test process | Sec. 6 | 23 driver-testing Qs | yes |
| 6 | Safety belts, car seats, air bags | Sec. 7 | 71, 112, 118, 324; 3 airbag, 2 car-seat | yes |
| 7 | Basic driving: backing, lane changes, parking, passing, turns | Sec. 8 | 17, 98, 133–134; 27 merge | yes |
| 8 | Flex lanes (UT-specific) | Sec. 9A | 2 hits | yes |
| 9 | Freeway driving / merging | Sec. 9B | 27 merge hits | yes |
| 10 | Intersections, signals, pavement markings | Sec. 9C–H | 22 ROW + 56 signs/signals Qs | yes |
| 11 | Roundabouts | Sec. 9F | 24, 27, 37, 170, 184, 408, 412 | yes |
| 12 | Speed limits | Sec. 9E | 15 hits | yes |
| 13 | Yielding right-of-way | Sec. 9J | 22 hits | yes |
| 14 | Alcohol/drugs, Utah .05 BAC, interdicted person | Sec. 10; HB 437 | 5, 6, 19, 30, 194–203 | yes |
| 15 | Mountain driving (downhill gearing, gravity, uphill yield) | Sec. 11I | 133, 134, 224, 225, 230 | yes |
| 16 | Snowplows in echelon (no-pass rule) | Sec. 9E / line 1532 | 137 | yes |
| 17 | Studded-tire date window Oct 15 – Mar 31, snow tires, chains | Sec. 11O | 238, 355 | yes |
| 18 | Black ice, skidding, hydroplaning | Sec. 11L–O | 232, 236, 237 | yes |
| 19 | Night driving / headlight rules | Sec. 11J | 226, 229, 283, 289, 291, 347, 350 | yes |
| 20 | Distracted driving / handheld wireless (HWC) | Sec. 11F | 20, 275 | yes |
| 21 | Work zones | Sec. 11G | 9 hits | yes |
| 22 | Crashes, insurance, financial responsibility | Sec. 12 | 14 insurance hits | yes |
| 23 | Point system, suspension/revocation, MVR | Sec. 13 | 13 points + 12 susp/revoc Qs | yes |
| 24 | Sharing the road: bicycles, motorcycles, large trucks, emergency vehicles, school buses, railroads | Sec. 14 | 18 bike + 14 motorcycle + 17 RR + 4 emerg + 4 bus | yes |
| 25 | Towing & vehicle equipment | Sec. 15–16 | 10 towing hits + 50 vehicle_information Qs | yes |

**Coverage: 25/25 of the formal TOC-derived critical topics are tested.**

### Recall gaps (sub-topics under covered sections)

| Topic | Manual reference | Current questions | Severity |
|---|---|---|---|
| Flooding / driving through standing water | Sec. 11E | 0 | medium — Utah flash-flood relevance |
| Collisions with animals (Sec. 11B) and high-altitude wildlife behavior at dawn/dusk | Sec. 11B; line 2476-area "wildlife" hazard | 1 (Q405 deer crossing sign only — no behavioral guidance question) | medium |
| Vehicle submerged underwater | Sec. 11N | 0 explicit | low |
| Altitude / thin-air effects on engine cooling and brake fade on long descents | implied in Sec. 11I + Sec. 11O hot-weather | 0 (the term "altitude" never appears in the question bank) | low — manual does not call this out by name, but UT context warrants it |
| Avalanche / canyon-specific warnings | Sec. 11I context | 0 | low — manual is itself thin on this |
| Desert driving (UT southern routes) | Sec. 11C | 1 | low |
| Lightning | Sec. 11H | 1 | low |

The gaps are concentrated in **Section 11 (Distractions and Driving Challenges)** sub-sections that the question generator under-sampled relative to mainline rules-of-the-road content.

## Coverage

### Category distribution (10/10 canonical categories present)

| Category | Questions | Share |
|---|---:|---:|
| safe_driving_rules | 100 | 23.4% |
| signs_and_signals | 56 | 13.1% |
| license_system | 55 | 12.9% |
| vehicle_information | 50 | 11.7% |
| penalties_and_points | 48 | 11.2% |
| sharing_the_road | 35 | 8.2% |
| defensive_driving | 32 | 7.5% |
| driver_testing | 23 | 5.4% |
| driver_responsibility | 15 | 3.5% |
| alcohol_drugs_health | 13 | 3.0% |
| **Total** | **427** | 100% |

- No category is missing.
- No category exceeds the 40% over-concentration threshold (top is 23.4%).
- `alcohol_drugs_health` is the smallest bucket at 3.0% — defensible because most DUI/BAC content is folded into `penalties_and_points`; manual itself dedicates only Section 10 (~10 pages of 100) to the topic.

### Sign-question contribution

- 34 image-tagged sign questions (Q394–427), covering 34 distinct MUTCD signs including `deer_crossing.png`, `slippery_when_wet.png`, `hill.png`, `winding_road.png`, `reverse_curve.png`, `school_zone.png`, `railroad_crossing.png`. The mountain/wildlife sign set is appropriate for Utah.

### Question density vs manual size

- Manual: 253,419 chars / 112 pages.
- Question bank: 427 questions.
- Density: ~1.67 questions per 1,000 chars (i.e., one question per ~600 chars / ~roughly 0.26 pages). This is in the normal range for the cohort (comparable to AZ, NV, CO mountain-west states).

### Legislative-currency check

The four highlighted 2025 bills (HB 234, HB 308, HB 437, HB 190) plus the 2026-effective interdicted-person changes are all explicitly tested (Q3–Q7). The "NEW 2025 LAWS" block on the front of the manual is fully reflected — strong signal that the question bank tracks the current edition rather than a stale one.

## Recommended Actions

1. **Add 2–3 questions on Section 11E "Flooding"** — Utah experiences flash floods in canyon country; the manual covers this but the bank has zero questions on driving through standing water. Suggested topics: do-not-drive-through depth thresholds, brake-drying after a wet crossing.
2. **Add a behavioral wildlife-collision question (not just a sign question)** — Section 11B "Avoiding Collisions with Animals" is in the manual; current coverage is only the `deer_crossing.png` sign (Q405). A question testing dawn/dusk peak activity, brake-don't-swerve guidance, and post-collision reporting would close the gap.
3. **Add a question on vehicle-submerged-underwater procedure** (Sec. 11N) — distinctive Utah content (Great Salt Lake / reservoir context) that currently has 0 coverage.
4. **Optional: a question on long-descent brake-fade / shifting to lower gear at altitude** — would deepen the mountain-driving coverage beyond the existing 5 questions. Manual line 2480–2482 directly supports such a question.
5. **No retractions or fixes required.** All 393 narrative questions are grounded in the manual, including the 6 initially-flagged structural/TOC-reference questions. Sign questions are visually grounded and consistent with MUTCD standards.
6. **Optional refactor (low priority):** Q17, Q19, Q20, Q28, Q30 phrase the test as "Which *section* of the manual…?" — these test memorization of manual organization rather than driving knowledge. Consider rewriting them to test the underlying concept directly (e.g., "Boating under the influence is governed by *which* state law?" rather than "*which section* covers it"). Not a precision issue, just a question-design quality note.
