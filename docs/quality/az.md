# Arizona (AZ) — Quiz Quality Verification

| | |
|---|---|
| State | Arizona (AZ) |
| Agency | MVD (ADOT) |
| Manual | [Arizona Driver License Manual (apps.azdot.gov)](https://apps.azdot.gov/files/mvd/mvd-forms-lib/99-0117.pdf) |
| Edition | 2025 (R03/26) |
| Manual text | 161,765 chars (74 pages) |
| Questions | 295 (EN/ES) |
| Verified | 2026-04-29 |

## Score

| Axis | Grade |
|---|---:|
| Precision | A |
| Recall | B |
| Coverage | A |
| **Overall** | **A** |

- **Precision A**: 293/295 questions verified grounded (99.3%). One fabricated question (Q258) and one ambiguous-answer question (Q254), both in the `vehicle_information` "recommended emergency kit" cluster.
- **Recall B**: All 25 critical topics from the manual are addressed by the question bank, but bicycle-sharing, hydroplaning, and Arizona-specific roundabout content are thinly covered (≤4 dedicated questions each).
- **Coverage A**: All 10 canonical categories present, max concentration 24.1% (`safe_driving_rules`), well below the 40% over-concentration threshold; question density 1.82 Qs/1k chars is in the typical corpus range.

## Precision

Two-pass check per question. **Mechanical pass**: distinctive 3–5 word phrases from each question's combined text (question + correct choice + explanation) were grepped against `manual_text.txt`; combined with a content-token Jaccard overlap. **Semantic pass**: every flagged non-sign question (9) plus a random 10-question grounded control sample were sent to Gemini (`gemini-3-flash-preview`) with the full manual as context, and asked to verdict each as `grounded | partial | fabricated`. Sign questions (image-based, MUTCD-derived) were excluded from precision scoring since their correctness depends on the image, not on manual text.

| Bucket | Count | % of non-sign |
|---|---:|---:|
| Total questions | 295 | — |
| Sign questions (image-based, skipped) | 34 | — |
| Non-sign questions | 261 | 100% |
| Grounded by phrase match (mechanical) | 252 | 96.6% |
| Sent to Gemini judge (9 grep-misses + 10 grounded controls) | 19 | — |
| Confirmed grounded after semantic re-check | 259 | 99.2% |
| Partial | 1 | 0.4% |
| Fabricated | 1 | 0.4% |

**Control sample (10 random grounded questions)**: 10/10 verified grounded by Gemini, confirming the mechanical-pass false-negative rate is low.

### Flagged questions

| ID | Category | Verdict | Issue | Suggested fix |
|---:|---|---|---|---|
| 258 | vehicle_information | **fabricated** | Question asks which item is **NOT** explicitly mentioned in the emergency-kit list; answer claims "Fire extinguisher" is not mentioned. The manual explicitly lists "Fire extinguisher" (line 7099-area context) and the safety section also says *"Always carry a fire extinguisher"*. The correct answer is none of the above — the question has no valid distractor. | Remove the question, or rewrite with a true non-listed item as the distractor (e.g., "tire pressure gauge", "GPS device"). |
| 254 | vehicle_information | **partial / ambiguous** | Question asks which cleaning item is "recommended to be kept in your vehicle"; marks B ("Absorbent cloths") correct. Manual lists both A ("Paper towels") *and* B ("Absorbent cloths") in the emergency-kit bullet list. Both A and B are defensible answers. | Rewrite to use distractors that are NOT in the manual list (e.g., "Glass cleaner", "Microfiber towels"), or restructure as a multi-select. |

All 7 other initially-flagged non-sign questions (Q7, Q249, Q250, Q251, Q253, Q259, Q261) were confirmed **grounded** — they were grep-misses only because the manual presents the emergency-kit content as a vertical bullet list (one-word-per-line), which defeats phrase n-gram matching but is clearly the source.

## Recall

Gemini (`gemini-3.1-pro-preview`) was asked to enumerate the 25 most important driving topics in the Arizona manual. Each topic was checked against all 295 questions using a multi-tier keyword matcher (full multi-word keyword > token overlap), with spot-checks by manual grep for topics that scored low.

| # | Topic | Coverage | Example IDs |
|---:|---|:---:|---|
| 1 | Seat Belts & Child Restraints | strong | 59, 63, 64 |
| 2 | Following Distance & Space Cushion | strong | 81 + 7 partial |
| 3 | Signaling & Communicating | strong | 55, 56, 79 + 7 partial |
| 4 | Passing Rules & Restrictions | strong | 49, 67, 71, 85, 90, 91, 105, 117, 124 (22 hits via grep `pass`) |
| 5 | Roundabouts | thin | 92, 93, 276, 280 (only 4 dedicated questions) |
| 6 | Parking on Hills & Curbs | ok | 98, 183 |
| 7 | Freeway Driving & Gore Areas | strong | 102 + 5 partial |
| 8 | Traffic Signal Lights | strong | 107, 108, 115, 118 |
| 9 | Right-of-Way & Intersections | strong | 94 + 8 partial |
| 10 | Pedestrian Safety & Crosswalks | strong | 119 + 9 partial |
| 11 | Emergency Vehicles & Move Over Law | strong | 124 |
| 12 | School Buses & School Zones | strong | 125, 134 + 6 partial |
| 13 | Speed Limits & Adjusting Speed | strong | 130, 272 |
| 14 | Traffic Sign Shapes & Meanings | adequate | 262 (octagon), 270 (pennant), 273–278 (diamond warnings) |
| 15 | Work Zones & Construction | adequate | 138, 128, 139, 272, 275, 285 (7 hits via grep) |
| 16 | Pavement Markings & Line Colors | strong | 147 + 2 partial |
| 17 | Turning Rules & Two-Way Left Turn Lanes | strong | 92, 130, 143 + 5 partial |
| 18 | Sharing the Road with Bicycles | **thin** | 80, 154, 155, 156, 157, 161 (only 3 dedicated bicycle Qs, 7 cyclist mentions) |
| 19 | Sharing the Road with Motorcycles | strong | 55, 56, 79 + 6 partial |
| 20 | Sharing the Road with Large Trucks | strong | 163, 164 + 4 partial |
| 21 | Weather Conditions & Hydroplaning | **thin** | 128, 176, 177, 178, 183 (5 weather Qs; no explicit "hydroplane" question) |
| 22 | Headlight Use & Night Driving | strong | 176, 182 + 6 partial |
| 23 | Impaired Driving & DUI Penalties | strong | 201, 209, 214 + 8 partial |
| 24 | License Suspension & Points System | strong | 194, 205, 232 + 7 partial |
| 25 | Handling Vehicle Emergencies & Skids | strong | 222, 227 + 2 partial |

**Coverage rate**: 25/25 topics addressed (100%). Three are thinly covered (roundabouts, bicycle-specific rules, hydroplaning) and warrant supplementation.

## Coverage

### Category distribution

All 10 canonical categories are present. Largest category is `safe_driving_rules` at 24.1% — well below the 40% over-concentration threshold.

| Category | Count | % |
|---|---:|---:|
| safe_driving_rules | 71 | 24.1% |
| signs_and_signals | 50 | 16.9% |
| license_system | 33 | 11.2% |
| defensive_driving | 32 | 10.8% |
| penalties_and_points | 30 | 10.2% |
| vehicle_information | 27 | 9.2% |
| sharing_the_road | 19 | 6.4% |
| driver_responsibility | 18 | 6.1% |
| alcohol_drugs_health | 10 | 3.4% |
| driver_testing | 5 | 1.7% |
| **Total** | **295** | **100%** |

### Question density

| Metric | Value |
|---|---|
| Questions | 295 |
| Manual text size | 161,765 chars |
| Density (Qs per 1,000 manual chars) | 1.82 |

Density is in the typical corpus range (most onboarded states fall between 1.2 and 2.5).

### Sign-question ratio

| Source | Count | % |
|---|---:|---:|
| Sign questions (image-based, MUTCD-derived) | 34 | 11.5% |
| Manual-text-derived questions | 261 | 88.5% |

## Recommended Actions

### Must-fix (precision defects)

1. **Q258 (vehicle_information) — fabricated.** Rewrite or remove. The question's premise (fire extinguisher not listed) contradicts the manual. Replacement distractor should be an item that is genuinely absent from the emergency-kit list (e.g., "GPS device", "Roadside reflectors", "Tire pressure gauge").
2. **Q254 (vehicle_information) — ambiguous.** Two choices (Paper towels, Absorbent cloths) are both listed in the manual. Rewrite the distractors to leave a single correct answer.

### Recall gaps to consider

3. **Bicycles**: only 3 questions explicitly about bicycles (Q80, Q154, Q156–157). The manual devotes a full subsection to bicycle-sharing rules including the 3-feet passing law and the "same direction as traffic" requirement. Consider adding 2–3 more questions specifically on bicycle right-of-way, the 3-foot rule, and bicyclist signaling.
4. **Hydroplaning / weather-specific handling**: the manual covers hydroplaning, fog, dust storms (Arizona-specific haboob coverage), and snow on mountain passes. Current questions touch weather generally (~5 Qs) but no question uses the word "hydroplane" or specifically addresses dust-storm pull-off procedure. Adding 2–3 weather/hydroplaning questions would lift recall from B to A.
5. **Roundabouts**: 4 questions covered (Q92, Q93, Q276, Q280) — adequate but light for a state that has been actively building modern roundabouts. Optional supplement.

### Coverage observations (not blocking)

6. **`driver_testing` is thin (5 questions, 1.7%).** The manual covers vision screening, the written test format, the road skills test maneuvers, and Third Party authorized testers. Two or three more questions about the test itself (skills examiner checklist, what to bring, retake intervals) would round this out.
7. **`alcohol_drugs_health` is thin (10 questions, 3.4%).** Arizona has notably strict DUI law (Extreme DUI ≥0.15, Aggravated DUI) and an under-21 zero-tolerance regime with 2-year suspension. The current 10 questions cover the basics; 3–5 more on Arizona-specific DUI thresholds and Implied Consent refusal consequences would strengthen exposure to high-stakes content.
