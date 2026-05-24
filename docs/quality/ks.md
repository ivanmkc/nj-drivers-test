# Quiz Quality Verification — Kansas (KS)

| Field | Value |
| --- | --- |
| State | Kansas (KS) |
| Agency | DOR (Kansas Department of Revenue, Division of Vehicles) |
| Manual source | 2025 Kansas Driving Handbook — Non-Commercial Driver's Manual (AAMVA 09 Model Test Version, Revised February 2022) |
| Manual URL | https://www.ksrevenue.gov/pdf/dlhb.pdf |
| PDF SHA-256 | 1450c8b59b1c5f6247d20c1d00b3a759314df966a744c5ad20fe2d9c091fb4a5 |
| Manual pages / chars | 112 pages / 291,209 chars (extracted with PyMuPDF 1.27.2) |
| Total questions (EN) | 468 (450 text + 18 sign image) |
| Categories | 10 / 10 canonical categories present |
| Languages | EN / ES / JA |
| Verified | 2026-04-29 |

## Score

| Axis | Grade | Detail |
| --- | --- | --- |
| Precision | A | 450 / 450 non-sign questions grounded (100%) after LLM re-judging with full manual context |
| Recall | A | 25 / 25 critical Kansas topics covered, all with strong coverage (>=3 Qs) |
| Coverage | A | All 10 categories present; largest is `safe_driving_rules` at 32.1% (under 40% cap); density 1.61 Qs/1k chars (in 0.5-3.0 range); sign ratio 3.8% |
| **Overall** | **A** | GPA 4.00 |

Notes: the mechanical 5-word distinctive-phrase sweep matched 397/450 (88.2%) directly; the remaining 53 (29 zero-hit + 24 single-hit) were escalated to a Vertex AI Gemini judge (`gemini-2.5-flash`) using the manual as context. An initial pass with a 200K-char truncation falsely flagged 10 questions as `fabricated`; a re-judge with the FULL 291K-char manual (the donor section and sample questions sit in the final 5K chars) returned `grounded` for every one of them with verbatim manual quotes. Final verdict: **0 partial, 0 fabricated** across the 53 escalated plus 10 random grounded controls.

## Precision

Methodology: for each non-sign question, build 5-word distinctive phrases from `question + explanation` (sliding window, stopword filter) and grep against the normalised `manual_text.txt`. Phrases with >=2 hits = mechanically grounded; <=1 hit = escalated to Vertex AI Gemini (`gemini-2.5-flash`) with the full manual as context for a semantic verdict (`grounded` / `partial` / `fabricated`). A 10-question random control of mechanically-grounded items was also re-judged to validate the bar.

| Bucket | Count | % of text Qs |
| --- | --- | --- |
| Mechanically grounded (>=2 distinctive 5-word phrases in manual) | 397 | 88.2% |
| LLM-judged grounded (after mechanical miss/partial) | 53 | 11.8% |
| **Total grounded** | **450** | **100.0%** |
| Partial (claim partially supported) | 0 | 0.0% |
| Fabricated (claim contradicts or absent from manual) | 0 | 0.0% |
| Sign questions (not graded against manual text — generic MUTCD) | 18 | — |

### Flagged questions (mechanical miss) — all confirmed grounded

The 29 zero-hit questions and 24 single-hit questions were all confirmed `grounded` once the LLM judge had access to the full manual. Mechanical misses were driven by (a) heavy paraphrasing of the Governor's letter / Table of Contents / Age Requirements tables (structural manual content where the question paraphrases rather than quotes), and (b) content at the very end of the manual (organ-donation, sample-questions, very-hot-weather sections) that was beyond the initial 200K-char LLM context window.

| IDs | Category | Mechanical-miss reason | Manual anchor |
| --- | --- | --- | --- |
| 1 | safe_driving_rules | Paraphrase of Governor's letter on texting | manual lines 37-40 |
| 2 | vehicle_information | "141,000 miles of roads" stat from intro | line 27 |
| 3, 5 | license_system | Website ksrevenue.gov / "Non-Commercial Driver's Manual" title page | line 8, 42-43 |
| 6, 7, 8, 9, 10, 11, 12, 15 | mixed | Table-of-Contents structural questions | lines 56-164 |
| 16, 17 | license_system | VETERAN indicator docs (DD-214 / NGB-22) | lines 181-183 |
| 18-29, 34, 37 | license_system | Age Requirements table (commercial / non-commercial / farm permit / instruction permits) | lines 195-280 |
| 39, 40, 42, 44 | safe_driving_rules / license_system | Restricted License conditions (16-year-old curfew, passenger, wireless) | lines 280-330 |
| 65 | signs_and_signals | "Pennant-shaped" no-passing-zone warning sign | warning-signs section |
| 66 | defensive_driving | Four-second following rule for adverse conditions | space-management section |
| 74, 76, 198, 199, 200, 202 | safe_driving_rules | Parking restriction distances (15 ft hydrant, 30 ft signal, 12" curb, red curb = fire zone) | parking section |
| 87 | safe_driving_rules | Aggressive-driving relaxation guidance | aggressive-driving section |
| 89 | alcohol_drugs_health | "Vision impacted at .02 BAC for all drivers" | alcohol section |
| 140 | signs_and_signals | "Red light on the left" on horizontal signals | traffic-signals section |
| 208 | signs_and_signals | Regulatory sign colors (white with black/red/green) | traffic-signs section |
| 271, 275 | driver_responsibility / defensive_driving | "Driving is a privilege" + "limit risk = change direction/speed/lanes" | text quotes verified |
| 278 | defensive_driving | "Three options: brake, steer, accelerate" | avoiding-collisions section |
| 344 | safe_driving_rules | "Pass safety zone at no faster than 10 mph" | rules-of-the-road section |
| 351 | sharing_the_road | "Yield to pedestrians always, even jaywalking" | pedestrians section |
| 370 | driver_testing | "Must score 80% to pass" | knowledge-test section |
| 375 | safe_driving_rules | Stop-line stop sample question (verbatim manual sample Q10) | line 4690 |
| 417 | defensive_driving | "10-15 min breaks every 2-3 hours" on major highways | trip-planning section |
| 426 | vehicle_information | "Inspect tires every 2 hrs / 100 mi in hot weather" | hot-weather section |
| 438, 442, 444, 447, 448 | driver_responsibility | Organ-donation slogans ("SHARE YOUR LIFE / DECISION", "LIVE IT. GIVE IT. LIFE.", "Living donation is possible") | lines 5427-5462 |

All 10 random control questions (Q40, Q86, Q93, Q107, Q151, Q162, Q177, Q325, Q428, plus the partial-bucket sample) were also LLM-judged and returned `grounded`.

Spot-checked manual anchors for high-value claims:

- Q1 (texting prohibited) -> "Kansas Legislature updated our driving laws to prohibit this activity" (line 39).
- Q22 (Class C Restricted min age 15) -> Age Requirements table.
- Q39 ("one non-sibling minor passenger") -> Restricted License conditions.
- Q44 (Unrestricted License age 17) -> Age Requirements table.
- Q65 (No Passing Zone = pennant) -> warning-signs subsection.
- Q66 (four-second following rule, adverse conditions) -> space-management subsection.
- Q198 (15 ft of fire hydrant) -> No-Parking Zones list.
- Q278 (brake/steer/accelerate) -> Avoiding Collisions section.
- Q370 (80% knowledge-test passing score) -> Knowledge Test section.
- Q438/442/444/447/448 (organ-donation slogans) -> manual lines 5427-5462.

No fabrication, no over-claim, no contradicted citation found.

## Recall

Methodology: asked Vertex AI Gemini (`gemini-2.5-pro`) to enumerate the 25 most important driving topics a Kansas written-test taker MUST know from the full manual text. Each topic was then matched against the question bank by keyword sets (case-insensitive substring search across `question + explanation + choices`). Topics with >=1 matching question = covered; >=3 = strongly covered.

| #  | Critical topic | Questions | Sample IDs | Status |
| -- | --- | --- | --- | --- |
| 1  | Alcohol and Drug Impairment Laws (DUI)          |  47 | 6, 11, 51, 54, 73        | STRONG |
| 2  | Right-of-Way Rules at Intersections             |  67 | 8, 64, 67, 69, 72        | STRONG |
| 3  | Stopping for School Buses                       |  12 | 1, 12, 67, 68, 145       | STRONG |
| 4  | Responding to Emergency Vehicles                |  12 | 67, 71, 183, 329, 330    | STRONG |
| 5  | Understanding Traffic Signals                   |  21 | 6, 40, 67, 73, 137       | STRONG |
| 6  | Recognizing Traffic Signs                       | 109 | 6, 11, 35, 45, 47        | STRONG |
| 7  | Interpreting Pavement Markings                  |  11 | 9, 162, 168, 169, 170    | STRONG |
| 8  | Speed Limits and the Basic Speed Law            |  47 | 57, 58, 59, 64, 70       | STRONG |
| 9  | Rules for Passing Other Vehicles                |  25 | 63, 65, 151, 162, 168    | STRONG |
| 10 | Sharing the Road with Large Trucks              |  22 | 112, 176, 188, 190, 213  | STRONG |
| 11 | Seatbelt and Child Restraint Laws               |  24 | 6, 7, 11, 39, 59         | STRONG |
| 12 | Maintaining a Safe Following Distance           |  11 | 66, 239, 240, 244, 245   | STRONG |
| 13 | Distracted Driving and Cell Phone Use           |   7 | 1, 13, 34, 40, 78        | STRONG |
| 14 | Prohibited Parking Locations                    |  49 | 73, 74, 75, 76, 83       | STRONG |
| 15 | Graduated Driver's License (GDL) Restrictions   |  12 | 26, 33, 34, 35, 36       | STRONG |
| 16 | Sharing the Road with Pedestrians               |  39 | 73, 133, 134, 135, 136   | STRONG |
| 17 | Safe Driving Practices at Night                 |  33 | 25, 35, 45, 63, 70       | STRONG |
| 18 | Driving in Adverse Weather Conditions           | 119 | 1, 3, 7, 9, 10           | STRONG |
| 19 | Handling Vehicle Emergencies and Skids          |  34 | 40, 67, 71, 121, 148     | STRONG |
| 20 | Proper Turning and Turnabout Maneuvers          | 125 | 6, 11, 41, 61, 62        | STRONG |
| 21 | Sharing the Road with Motorcycles               |  11 | 5, 190, 241, 323, 324    | STRONG |
| 22 | Railroad Crossing Safety Procedures             |  37 | 59, 60, 64, 73, 75       | STRONG |
| 23 | Driving Safely in Work Zones                    |  13 | 152, 155, 157, 167, 208  | STRONG |
| 24 | Responding to Aggressive Driving                |   5 | 8, 78, 87, 244, 325      | STRONG |
| 25 | Reasons for Losing Driving Privileges           |  13 | 10, 50, 51, 52, 53       | STRONG |

**Recall: 25/25 = 100% (all strong, >=3 Qs).**

KS is by question density the heaviest state in the corpus (468 Qs on a 291K-char manual = 1.61 Qs per 1K chars), so essentially every important topic carries deep redundancy. Even the lightest-covered topic (Responding to Aggressive Driving, 5 Qs) is comfortably above the strong-coverage threshold. The 109 question count for "Recognizing Traffic Signs" reflects intentional broad treatment — most sign-shape, sign-color, and individual-warning-sign questions count toward this topic.

Thinly-covered topics worth noting (still strong, but lighter than the 468-Q bank would suggest):

- Distracted Driving / Cell Phone Use (7 Qs). The manual gives a full Driver Distractions subsection (lines ~750-820) and a Texting subsection on line 37; question count could justifiably be doubled given the state's recent statutory focus.
- Sharing the Road with Motorcycles (11 Qs). The manual's Motorcycles/Scooters/Mopeds subsection at lines ~3700-3900 supports more.
- Responding to Aggressive Driving (5 Qs). The manual has a dedicated Aggressive Driving subsection in Section 3 that supports another 2-3 questions on de-escalation behaviors.

## Coverage

### Category distribution

| Category | Questions | % of total | Notes |
| --- | --- | --- | --- |
| safe_driving_rules    | 150 | 32.1% | Largest bucket but under the 40% cap; reflects Section 6 (Rules of the Road) + Section 7 (Safe Driving Tips) being roughly 30% of the manual |
| defensive_driving     |  62 | 13.2% | Section 7 (Safe Driving Tips) + Section 8 (Avoiding Collisions) |
| signs_and_signals     |  51 | 10.9% | Includes 18 sign-image questions |
| vehicle_information   |  48 | 10.3% | Pre-trip inspection, basic vehicle control skills (Section 11) |
| sharing_the_road      |  43 |  9.2% | Section 9 (pedestrians, bicyclists, motorcycles, trucks, transit) |
| driver_responsibility |  31 |  6.6% | Includes the organ-donation block in Section 12 |
| license_system        |  29 |  6.2% | Sections 1-2 |
| driver_testing        |  29 |  6.2% | Section 11 (knowledge / pre-trip / road test) |
| penalties_and_points  |  14 |  3.0% | Loss-of-driving-privileges + BAC consequences |
| alcohol_drugs_health  |  11 |  2.4% | Thin — Section 3 alcohol content is concise in this manual; supplementary alcohol-impairment questions are filed under `safe_driving_rules` / `defensive_driving` |

All 10 canonical categories present. No category exceeds the 40% over-concentration flag. `safe_driving_rules` at 32% is the largest by a clear margin but stays within the safe range and proportionally tracks the manual's emphasis (the Rules of the Road + Safe Driving Tips sections together are ~30% of the source document).

### Question count vs manual size

| Metric | Value | Notes |
| --- | --- | --- |
| Manual text length | 291,209 chars (112 pages) | |
| Total questions | 468 | Highest in the 34-state corpus |
| Density | 1.61 Qs / 1000 chars | Expected 0.5-3.0 — in range, near the top |
| Manual chars per question | 622 | High density per the plan's note; many topics intentionally redundant |
| Sign questions | 18 (3.8%) | Lower than typical (~10%); reflects KS manual reuses signs via AAMVA Model Test |

The high density (the densest state in the corpus per the orchestrator's note) creates expected topic overlap — most critical topics are exercised from multiple angles. This is healthy for an offline practice app where users want repeated exposure on each high-stakes rule.

### Sign questions

18 sign questions (Q451-Q468) reference shared MUTCD-style images stored under `data/signs/`. Universal U.S. signs — content correct per MUTCD; not graded against `manual_text.txt`. The 3.8% sign-question share is lower than the corpus median (~10%); the KS manual itself includes only a modest in-line warning/regulatory sign survey, so the bank under-uses sign images relative to peer states.

### Structural audit

`python3 tools/audit_questions.py ks` -> **0 issues** (all 468 questions structurally valid, no within-state duplicates, all categories canonical).

## Recommended Actions

No blocking issues. The KS question bank is factually accurate, well-grounded in the source manual, and well-balanced across categories. Nice-to-have improvements only:

1. **Optionally rebalance the heavy `safe_driving_rules` bucket (32%)** by reclassifying questions that are really category-specific. Examples: parking questions (Q73-Q83, Q198-Q202) could move to a dedicated subgroup or `penalties_and_points`; speed-limit questions (Q57-Q70) could move to `defensive_driving`. Not a defect — KS is still under the 40% cap — but tightening will help the per-category drill UX.
2. **Expand the sign-image bank** beyond Q451-Q468 (currently only 3.8% of questions vs ~10% corpus median). The KS manual covers regulatory, warning, guide, and incident signs; adding sign-recognition images for school-zone, no-passing-zone (pennant), railroad advance-warning, and roundabout signs would close this gap.
3. **Lighten the manual-structural questions** at the front of the bank (Q6-Q15 are essentially Table-of-Contents trivia: "what section is X in?"). These are technically grounded but low test-prep value; consider replacing them with content questions on the same sections.
4. **Strengthen aggressive-driving / road-rage coverage** beyond the current 5 questions (Q8, Q78, Q87, Q244, Q325). The manual's Aggressive Driving subsection in Section 3 supports 2-3 more questions on specific de-escalation behaviors (do not make eye contact, do not respond, get to a safe place, etc.).
5. **Strengthen distracted-driving coverage** (currently 7 Qs). KS legislature singled this out as a priority in the Governor's letter (line 37-40) and the Driver Distractions subsection in Section 3 supports another 4-5 specific behavioral / penalty questions.

All five above are quality enhancements, not corrections — the existing 468-question bank requires no remediation.
