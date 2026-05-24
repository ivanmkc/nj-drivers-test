# Nevada (NV) — Quiz Quality Verification Report

- **State**: Nevada (NV)
- **Source manual**: Nevada Driver's Handbook, March 2024 edition (DMV 700), `dmv.nv.gov/pdfforms/dlbook.pdf`
- **Manual extraction**: PyMuPDF 1.27.2, 86 pages, 210,362 chars, SHA-256 `bd577dcad780db1cb40678ce760e43896d4faadec34df211b5e6b1ed14a85062`
- **Question bank**: `data/states/nv/questions_en.yaml` — 346 questions (328 text + 18 sign-image), EN + ES translations
- **Verification date**: 2026-04-29

## Score

| Axis      | Result                    | Grade |
| --------- | ------------------------- | ----- |
| Precision | 100% grounded (no fabricated content detected) | A     |
| Recall    | 48/50 critical topics covered (96.0%) | A     |
| Coverage  | All 10 canonical categories present; max concentration 23.1% | A     |
| **Overall** | **A** | **A** |

## Precision

Method: For every non-sign question, distinctive 5-word n-grams from each `explanation` were normalized and grep-matched against `manual_text.txt`. Phrases that didn't surface a literal match were re-verified by extracting the four-or-more-letter "distinctive" tokens of the correct answer choice and checking those against the manual; in every case the underlying claim was demonstrably present in the source.

| Bucket       | Count | %     | Notes                                                         |
| ------------ | ----- | ----- | ------------------------------------------------------------- |
| Total        | 346   | 100%  | 328 text + 18 sign-image questions                            |
| Sign images  | 18    |  5.2% | Excluded from text grounding pass (visual MUTCD assets)       |
| Grounded     | 328   | 100%  | All non-sign questions trace back to the manual               |
| Partial      |   0   |  0%   | —                                                             |
| Fabricated   |   0   |  0%   | —                                                             |

15 questions initially failed a strict 5-gram grep due to paraphrasing in the `explanation` field (the question itself was correct). After widening to a keyword check against the answer choice, every one of these resolved to language present in the manual. None required correction:

| ID  | Category               | Reason for flag                            | Resolution                                                  |
| --- | ---------------------- | ------------------------------------------ | ----------------------------------------------------------- |
| 13  | license_system         | Phrasing of ToC reference                  | "Human Trafficking - No Child for Sale" appears verbatim    |
| 92  | driver_responsibility  | Synonymized "misdemeanor offenses"         | Manual: "misdemeanor offenses" present                      |
| 101 | signs_and_signals      | "Brown highway sign" rewording             | Manual: "recreation and scenic area information" present    |
| 102 | signs_and_signals      | Pennant shape commentary                   | Manual lists pennant -> no passing                          |
| 130 | safe_driving_rules     | Basic Rule reword                          | All keywords (traffic/weather/visibility/road) confirmed    |
| 138 | sharing_the_road       | HOV "eligible" paraphrase                  | Manual: HOV rules list motorcycles as eligible              |
| 157 | safe_driving_rules     | Perception/reaction/braking summary        | All three terms appear in the stopping section              |
| 171 | signs_and_signals      | Hand signal description                    | Manual: "Slowing or stop" hand signal defined as described  |
| 212 | defensive_driving      | Brake-failure "never put in park" warning  | Manual contains the warning verbatim                        |
| 214 | defensive_driving      | Accelerator sticks remediation             | Manual: shift to neutral, apply brakes, pull off            |
| 216 | vehicle_information    | Same accelerator warning, different angle  | Same source passage as Q214                                 |
| 243 | sharing_the_road       | "Cyclists should not..." section           | Manual lists headset/earpiece prohibition                   |
| 315 | license_system         | "Get online, not in line" slogan           | Slogan appears in manual                                    |
| 319 | vehicle_information    | Personalized plate orders online           | Listed under DMV online services                            |
| 326 | license_system         | dmv.nv.gov/kiosk URL                       | URL appears verbatim                                        |

**Result**: 0 fabricated questions. 0 actionable precision defects.

## Recall

Method: 50 critical topics were derived from the Nevada Driver's Handbook table of contents (13 chapters) plus statutorily-tested concepts (DUI thresholds, demerit points, Move Over law, etc.). Each topic was probed against question stems + explanations + answer choices with a keyword set tuned per topic.

| #  | Critical topic                                          | Qs   | Status   |
| -- | ------------------------------------------------------- | ---- | -------- |
| 1  | License eligibility (age, residency, 30-day rule)       | 19   | Covered  |
| 2  | Documents required (Real ID, proof of name/age/SSN)     | 10   | Covered  |
| 3  | Driver Authorization Card (DAC)                         | 6    | Covered  |
| 4  | Vision / knowledge / skills tests and waivers           | 12   | Covered  |
| 5  | Graduated licensing for young drivers                   | 10   | Covered  |
| 6  | License classifications (A, B, C, M / CDL)              | 12   | Covered  |
| 7  | Renewals and duplicate licenses                         | 7    | Covered  |
| 8  | Identification cards / Veteran designation              | 10   | Covered  |
| 9  | Human Trafficking - No Child for Sale                   | 2    | Covered  |
| 10 | Fees                                                    | 40   | Covered  |
| 11 | Seat belts and child restraint laws                     | 15   | Covered  |
| 12 | Unattended children / pets in vehicle                   | 2    | Covered  |
| 13 | Signs (regulatory / warning / guide / colors / shapes)  | 6    | Covered (+ 18 sign-image questions) |
| 14 | Traffic signals and flashing lights                     | 12   | Covered  |
| 15 | Highway markings (yellow / white lines)                 | 5    | Covered  |
| 16 | Right-of-way                                            | 23   | Covered  |
| 17 | Speed limits and basic speed rule                       | 27   | Covered  |
| 18 | Freeway driving / ramp meters / HOV lanes               | 21   | Covered  |
| 19 | Anti-lock braking systems (ABS)                         | 8    | Covered  |
| 20 | Stopping distances (perception / reaction / braking)    | 15   | Covered  |
| 21 | Defensive driving tips                                  | 3    | Covered (thin) |
| 22 | Cell phones and texting                                 | 5    | Covered  |
| 23 | Stopped by law enforcement                              | 8    | Covered  |
| 24 | Roundabouts                                             | 7    | Covered  |
| 25 | Signaling, turning, lane changes, passing               | 38   | Covered  |
| 26 | Parking (curbs, hills, parallel)                        | 24   | Covered  |
| 27 | International Symbol of Access / disabled parking       | 4    | Covered  |
| 28 | Advanced Driver Assistance Systems (ADAS) — Ch. 4       | 5    | Covered  |
| 29 | Night driving                                           | 8    | Covered  |
| 30 | Driving in bad weather (rain, fog, snow, ice)           | 11   | Covered  |
| 31 | Skidding and vehicle control                            | 13   | Covered  |
| 32 | Driving emergencies (brake/accel failure, blowout, fire)| 13   | Covered  |
| 33 | Tips for driving in a flash flood                       | **0**| **GAP**  |
| 34 | Highway work zones                                      | 7    | Covered  |
| 35 | Approaching a stopped emergency vehicle (Move Over)     | 7    | Covered  |
| 36 | Commercial vehicles / no-zones                          | 11   | Covered  |
| 37 | Motorcycles                                             | 14   | Covered  |
| 38 | Mopeds                                                  | 5    | Covered  |
| 39 | School buses (stopping requirement)                     | 2    | Covered (thin) |
| 40 | Bicycles / sharing road with cyclists                   | 14   | Covered  |
| 41 | Passengers in the bed of a truck                        | **0**| **GAP**  |
| 42 | Pedestrians (incl. blind / visually impaired)           | 33   | Covered  |
| 43 | Towing and trailer loading                              | 22   | Covered  |
| 44 | Insurance and financial responsibility                  | 12   | Covered  |
| 45 | What to do at a crash (SR-1 form)                       | 17   | Covered  |
| 46 | Demerit point system                                    | 10   | Covered  |
| 47 | DUI penalties and implied consent                       | 37   | Covered  |
| 48 | Young driver DUI / zero tolerance                       | 3    | Covered  |
| 49 | Open container law                                      | 1    | Covered (thin) |
| 50 | License suspensions and revocations                     | 27   | Covered  |

**Recall: 48/50 = 96.0%**

Notes on "thin" coverage (1-3 questions but topic touched):
- Topic 21 (Defensive driving tips, 3 Qs) — Ch. 3 has a full subsection but is mostly reachable through related categories (following distance, hazards) which inflated other buckets.
- Topic 39 (School buses, 2 Qs) — Statutorily critical "you must stop both directions on undivided road"-style nuance worth a second question.
- Topic 49 (Open container, 1 Q) — A second question on the "passenger area" vs. "living quarters" distinction would improve test realism.

## Coverage

### Category distribution (canonical 10)

| Category               | Count | %     | Flag                |
| ---------------------- | ----- | ----- | ------------------- |
| safe_driving_rules     | 80    | 23.1% | OK                  |
| license_system         | 58    | 16.8% | OK                  |
| vehicle_information    | 42    | 12.1% | OK                  |
| signs_and_signals      | 36    | 10.4% | OK                  |
| penalties_and_points   | 31    |  9.0% | OK                  |
| defensive_driving      | 28    |  8.1% | OK                  |
| sharing_the_road       | 25    |  7.2% | OK                  |
| driver_responsibility  | 23    |  6.6% | OK                  |
| driver_testing         | 14    |  4.0% | Low                 |
| alcohol_drugs_health   |  9    |  2.6% | Low (see note)      |

- All 10 canonical categories are present. No missing categories.
- Maximum concentration is 23.1% (`safe_driving_rules`), well below the 40% over-concentration threshold.
- `alcohol_drugs_health` looks underweight at 2.6%, but actual DUI/alcohol coverage is ~37 questions spread between this category and `penalties_and_points`, which matches the manual's organization (DUI laws sit in Ch. 10 alongside penalties).

### Volume vs. manual size

- Manual text size: **210,362 chars** (86 pages)
- Question count: **346** (328 text + 18 sign-image)
- Density: **~1 question per 608 chars** of manual text — within the typical band (most onboarded states sit between 400 and 900 chars/question).
- Sign question share: **5.2%** of total — in line with peer states.

### Translations

- EN: required, present (346 questions).
- ES: present (`questions_es.yaml`, 208 KB).
- JA: not generated (optional per project rules).

## Recommended Actions

Priority is low — the bank is well-grounded and broadly covers the manual. The following would lift the score from "A" to a tight "A+":

1. **Add ~2 questions on "Tips for Driving in a Flash Flood"** (Ch. 5, p. 59). This is a Nevada-specific safety topic (sub-headed in the manual) with zero current coverage. Suggested angles: (a) "turn around, don't drown" — never drive through standing water; (b) what depth of moving water can carry a vehicle away.
2. **Add 1-2 questions on "Passengers in the Bed of a Truck"** (Ch. 6, p. 66). The manual dedicates a full section; current bank ignores it. Suggested angle: the age restriction and any exemptions (e.g., farm work, parades).
3. **Add 1 question on school-bus stopping requirements** specifically clarifying "both directions on undivided road / divided highway exception" — currently only loosely covered by Q108/Q238.
4. **Add 1 question on open-container nuance** (passenger area vs. living quarters of motor home / commercial bus / limo / taxi). Q302 covers the exemption but the inverse claim would round out the topic.
5. **Optional**: Move 1-2 DUI-fee or DUI-administrative questions from `penalties_and_points` into `alcohol_drugs_health` to balance the category split closer to the manual's organization.

No precision defects to correct. No structural issues. No category rebalancing required.
