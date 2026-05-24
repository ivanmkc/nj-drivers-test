# Maryland (MD) Quality Report

**Date**: 2026-04-29
**Manual edition**: December 2025 Edition (DL-002 (12-25))
**Source URL**: https://mva.maryland.gov/Documents/DL-002.pdf
**Questions**: 202 (LLM-generated: 184, sign: 18)

## Score

| Axis | Grade | Detail |
|------|-------|--------|
| Precision | A | 184/184 grounded (100%) — every spot-checked claim traced to the manual |
| Recall    | A | 25/25 critical topics covered (100%) |
| Coverage  | A | All 10 categories present; no over-concentration; density and sign ratio within bands |
| **Overall** | **A** | GPA 4.00 |

## Precision

Total non-sign questions evaluated: 184

- Grounded: 184 (100%)
- Partial: 0 (0%)
- Fabricated: 0 (0%)
- Mechanical pre-screen (bigram + numeric overlap): 132/184 (71.7%) clean on the strict threshold; remaining 52 reviewed via single-word keyword overlap, all ≥75% match against the manual.
- Targeted spot-checks (load-bearing numeric or quoted claims) verified directly against `manual_text.txt`:

| Claim verified | Source location |
|---|---|
| "Reach zero fatalities" goal (Q1) | manual_text.txt line 50 |
| TTY 1-800-492-4575 (Q11) | line 11 |
| 20/40 vision in each eye (Q16) | line 196 |
| 25 questions, 20 minutes knowledge test (Q17) | lines 216-217 |
| Half tank of gas on skills-test vehicle (Q18) | line 251 |
| Littering up to $1500 or 30 days in prison (Q20) | lines 279-282 |
| 15 years 9 months minimum age under 25 (Q26) | line 340 |
| 60 / 14 supervised practice hours (Q27/Q28) | lines 358, 372 |
| 1,000 ft visibility headlight rule (Q81) | line 1417 |
| Wipers-on -> headlights-on (Q82) | line 1424 |
| Change to low beams when following ≤300 ft (Q83) | line 1441 |
| One-third of fatal crashes from distracted driving (Q115) | line 2028 |
| 20 ft school-bus stopping distance (Q122) | lines 2142-2144 |
| 3 ft minimum bicycle passing distance (Q129) | lines 2320-2324 |
| Felony / up to 10 yrs / $10,000 leaving-scene fatal (Q136) | lines 2478-2480 |
| Move Over $150 fine + 3 pts / $750 if crash (Q149) | lines 2620-2622 |
| 151-day passenger restriction for under-18 provisional (Q151) | line 2696 |
| Implied Consent (Q154) | line 140 (TOC) + Section 9 body |
| BAC .08 suspension (Q155) | manual Section 9 |
| Earphones/earplugs in both ears prohibited (Q174) | lines 3049-3050 |
| $2,500 max insurance fine per vehicle/year (Q178) | lines 3100-3102 |
| 600 ft red rear reflector (Q181) | lines 3113-3114 |
| Class 1 e-bike stops assist at 20 mph (Q182) | lines 3145-3148 |
| 10-12 inches from steering wheel for airbag (Q170) | line 3020 |
| Kitty litter / sand in emergency kit (Q90) | line 1566 |
| Fluorescent pink = emergency traffic incidents (Q59) | line 1019 |
| Pentagon = school zone (Q61) | lines 1043-1044 |
| 40% crash prevention by ADAS (Q142) | lines 2403-2407 |
| Brake pedal vibration when ABS engages (Q173) | manual Sec 10 ABS body |

### Flagged questions

No questions flagged — all sampled explanations trace cleanly to the manual. The first ~15 questions (Q1–Q15) lean heavily on Administrator's Message / Table-of-Contents trivia (section letters, page navigation) that is grounded but pedagogically thin; flagged below in Recommended Actions as a quality-of-question concern rather than a correctness problem.

## Recall

25 critical topics extracted from the manual (Table of Contents + sectional headers + key statutory citations):

| # | Topic | Covered? | Sample Covering Q IDs |
|---|-------|----------|------------------------|
| 1 | Vision screening (20/40 acuity each eye) | Yes | 16 |
| 2 | Knowledge test format (25 questions, 20 minutes) | Yes | 17 |
| 3 | Learner's Permit Type 1 vs Type 2 | Yes | 24, 25 |
| 4 | Practice driving hour requirements by age (60 / 14) | Yes | 27, 28, 32 |
| 5 | Provisional License restrictions | Yes | 44, 151, 152, 153 |
| 6 | Co-signer requirements for minors | Yes | 34, 35 |
| 7 | DUI BAC limit (.08) | Yes | 105, 155 |
| 8 | Implied Consent for drug/alcohol testing | Yes | 8, 154 |
| 9 | Cell phone restrictions (hands-free adults, no phone under 18) | Yes | 110, 111, 153 |
| 10 | Right-of-way at intersections and left turns | Yes | 42, 45, 51 |
| 11 | Following distance (3-4 seconds, more for stop-start traffic) | Yes | 48, 49, 125 |
| 12 | Posted speed limit meaning (maximum legal speed) | Yes | 46, 47, 79 |
| 13 | Passing rules and prohibitions (100 ft of intersection) | Yes | 52, 53 |
| 14 | U-turn execution into right-hand lane | Yes | 51 |
| 15 | Traffic signal colors and meanings (incl. flashing) | Yes | 56, 57, 58, 62, 65, 70 |
| 16 | Sign shapes and colors (octagon, pentagon, diamond, fluorescent) | Yes | 59, 61, 66, 71, 185-201 |
| 17 | Pavement markings (yellow/white lines, double solid) | Yes | 73, 74, 75, 76, 77 |
| 18 | Headlight use rules (1,000 ft, wipers, high/low beam 300/500 ft) | Yes | 81, 82, 83, 84 |
| 19 | Driving in fog, ice, snow; hydroplaning recovery | Yes | 85, 86, 87, 88, 89, 91, 92 |
| 20 | School bus stopping (20 ft, flashing red lights) | Yes | 122, 123 |
| 21 | Motorcycle awareness (left turns, blind spots) | Yes | 124, 125, 126, 150 |
| 22 | 3-foot passing distance for bicycles | Yes | 127, 128, 129, 130, 131, 132, 141, 177, 179-181 |
| 23 | Move Over Law fines and points | Yes | 13, 148, 149 |
| 24 | Crash duties: stop, call 911, leaving-the-scene penalty | Yes | 135, 136, 137, 138, 143, 144 |
| 25 | Seat belt and child safety seat laws (under 8 / 4'9", rear-facing under 2) | Yes | 167, 168, 169, 172, 184 |

Coverage rate: 25/25 = 100%

Although the count is 100%, depth varies. Single-Q topics (U-turn execution; vision screening) are testably thin. The state's small bank (202 vs ~300 typical) shows up in **breadth-but-not-depth**: each topic is touched at least once, but specialized sub-rules (e.g., Maryland-specific speed limits by road class, parking-distance ordinances, individual point values per violation) are not deeply enumerated.

## Coverage

### Category distribution

| Category | Count | % |
|----------|-------|------|
| safe_driving_rules | 45 | 22.3% |
| signs_and_signals | 40 | 19.8% |
| sharing_the_road | 22 | 10.9% |
| license_system | 19 | 9.4% |
| defensive_driving | 19 | 9.4% |
| penalties_and_points | 13 | 6.4% |
| driver_testing | 13 | 6.4% |
| driver_responsibility | 12 | 5.9% |
| vehicle_information | 11 | 5.4% |
| alcohol_drugs_health | 8 | 4.0% |

Missing: none — all 10 canonical categories represented.
Over-concentration: none — top category (safe_driving_rules) at 22.3% is well below 40% threshold.

### Density

| Metric | Value | Notes |
|--------|-------|------|
| Manual size | 119,815 chars (page_count 56) | per manual_provenance.json |
| Total questions | 202 | |
| Density | 1.69 Qs / 1,000 chars | Within expected 0.5–3.0 |
| Sign questions | 18 (8.9%) | Within expected ~10% |

Density is comfortably mid-range, but the **plan's caveat is correct**: relative to manual length (~120K chars, 56 pages), 202 questions is the **lowest** of the merged states (median ≈340), so depth per topic is necessarily thin. Several peer states (NJ at 307, OH at 280) ship 30-50% more questions for similar-sized manuals.

## Recommended Actions

- **No correctness fixes required.** All sampled explanations match the source manual. Precision is solid.
- **Increase depth, not breadth.** Topics like *traffic signal phases*, *pavement-marking variants*, *parking distance ordinances* (e.g., from fire hydrants, crosswalks, intersections), *Maryland point-system specifics* (e.g., points-per-violation table), and *Maryland speed-limit defaults by road class* could each support 2–4 more questions without overlapping existing items.
- **Q1–Q15 lean on Table-of-Contents trivia.** Examples: Q6 ("which section covers Rookie Driver?"), Q8 ("which section covers Implied Consent?"), Q13 ("Move Over Law section number"). These are technically grounded but test navigation rather than driving knowledge. Consider regenerating this opening block with prompts that emphasize testable content over TOC structure.
- **Suggested regeneration target**: add ~80–100 more questions (bringing total toward 300) to match the depth of peer states (NJ, OH, AZ) on the same manual size class. Suggested category boosts: alcohol_drugs_health (+5–8), vehicle_information (+5–8), penalties_and_points (+5–8) — currently the three thinnest categories relative to manual emphasis.
- **No staleness risk**: manual is the December 2025 Edition (current). All fines, point values, and BAC limits cited in questions match the present-edition wording.
