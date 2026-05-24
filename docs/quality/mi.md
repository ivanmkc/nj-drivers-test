# Michigan (MI) — Quiz Quality Report

| Field | Value |
| --- | --- |
| State | Michigan |
| Agency | SOS (Secretary of State) |
| Manual | What Every Driver Must Know (October 2025 ed.) |
| Manual edition | 2025-10 |
| Manual SHA-256 | `d7afd04a7270cf908fa47ba68b56712856b7c313c4751a4f9cd1c575281a7c11` |
| Manual size | 204,792 chars / 92 pages |
| Manual sources | 1 (multi-source manifest, single PDF) |
| Total questions | 350 |
| Sign questions | 34 (9.7%) |
| Non-sign questions | 316 (90.3%) |
| Question density | 1.71 Qs per 1,000 chars of manual text |
| Languages shipped | English, Spanish |
| Structural audit | `tools/audit_questions.py mi` → 0 issues |

## Score

| Axis | Result | Grade |
| --- | --- | --- |
| Precision | ~40 distinct claims spot-checked across 316 non-sign questions; all trace cleanly to the manual; zero fabrications detected. WEDMK "multilingual editions of the manual" content trap not present in the question bank. | **A** |
| Recall | 31/31 critical WEDMK topics covered; all chapter-level sections from the table of contents are represented. | **A** |
| Coverage | All 10 canonical categories present; max share 24.0% (`safe_driving_rules`), well under the 40% over-concentration threshold; density 1.71 Qs/1k chars (mid-range). | **A** |
| **Overall** | All three axes A. The bank is tightly bound to the source manual, with explanations that quote directly from named sections. | **A** |

## Precision

Methodology: every non-sign explanation in `questions_en.yaml` was screened by searching `manual_text.txt` for distinctive 3–6-word phrases drawn from the explanation. Claims that failed the phrase grep were re-checked with broader keyword queries and direct passage reads. A focused content-trap search was also performed for the known WEDMK failure mode ("the manual is available in multiple languages / editions") — no such claim appears in the bank.

| Result | Count | % |
| --- | --- | --- |
| Grounded by direct phrase / passage match | 316/316 | 100% |
| Partial / weak grounding | 0 | 0% |
| Fabricated / contradicted | 0 | 0% |

### Representative spot-checks (all verified against the manual)

| ID | Claim | Manual evidence |
| --- | --- | --- |
| 30 | "Driving is a privilege and not a right" — Introduction | "Driving is a privilege and not a right." (l. 211) |
| 31 | 2,284 crashes involved cell-phone use in 2023 | "A total of 2,284 crashes resulted from a driver, pedestrian, or bicyclist using a cell phone." (l. 257-258) |
| 32 | 272 (26.6%) of 1,021 fatal crashes were alcohol-involved | "Of the 1,021 fatal crashes that occurred in Michigan, 272 (26.6%) were alcohol-involved" (l. 253-254) |
| 34 | Organ Donor Registry saves up to 8 lives | "agree to become an organ, eye and tissue donor to save up to 8 lives, and potentially heal up to 125 others." (l. 276-277) |
| 40 | Chauffeur GVWR threshold = 10,000 lb | "operating a motor vehicle with a Gross Vehicle Weight Rating (GVWR) of 10,000 pounds or more" (l. 383-384) |
| 50 | REAL ID required for domestic flights starting May 7, 2025 | "Beginning May 7, 2025, Michigan residents boarding a plane for domestic travel" (l. 461) |
| 53 | Germany / S. Korea / Canada license-conversion exception | "If you are from another U.S. state, Canada, Germany or the Republic of Korea (South Korea), you may convert your driver's license" (l. 520-522) |
| 56 / 63 / 126 | Kelsey's Law prohibits phone use for GDL 1 / GDL 2 teens | "Kelsey's Law prohibits you from using a cell phone while driving." (l. 603-604) and "Kelsey's Law (MCL 257.602c) prohibits teens with a GDL 1 or GDL 2" (l. 1765-1766) |
| 92 | Drag racing = 4-point violation | "Four Points: Drag racing." (l. 1235-1236) |
| 96 | Fleeing/eluding = 6 points | "Six Points: Fleeing or eluding a police officer." (l. 1217, 1226) |
| 105/106 | Equivalent alcohol amounts; only time sobers you | "coffee, a cold shower, exercise or fresh air can sober them up. The only thing that sobers you up is time." (l. 1293-1294) |
| 108 | Drug-conviction reinstatement fee = $125 | "driver's license reinstatement fee is $125." (l. 1349-1350) |
| 109/110 | Marijuana: 2.5 oz legal at 21+; illegal to transport into Canada | "Transport 2.5 ounces or less of marijuana if you are…" (l. 1363) / "Transport marijuana into Canada." (l. 1385) |
| 123 | Hand-held phone first-offense fine = $100 | "Drivers face a fine of $100 for a first offense and $250" (l. 1679) |
| 124 | At 65 mph, vehicle covers 24 ft in 1/4 sec | "a car moving at 65 mph covers 24 feet." (l. 1689) |
| 129 | First chemical drunk-driver test = Detroit PD, 1945 | "In 1945, the first chemical test to identify suspected drunken drivers was administered by the Detroit Police Department." (l. 1656-1658) |
| 132 | Car seat/booster until 8 yr OR 4 ft 9 in | "until they are 8 years old or 4 feet 9 inches tall" (l. 1838-1839) |
| 133 | Rear-facing seat → front airbag must be deactivated | "passenger air bag must be deactivated if a child in a rear-facing child-restraint system" (l. 1912-1913) |
| 135/136 | <6 unattended unless caregiver ≥13 not legally incapacitated | "younger than 6 years old unattended…" / "under the supervision of someone age 13 or older who is not legally incapacitated" (l. 1888-1894) |
| 137/138 | 10-in breastbone clearance; back-seat kids ≤12 | "10 inches of space between the center of their breastbone and the center of the steering wheel" (l. 1920-1921) |
| 139/140/141 | 15 mph mobile-home park; 25 mph subdivisions; 65 mph trucks on 70-mph freeway | Speed-limit list (l. 1941-1959) |
| 145/146 | Local maintenance vehicles allowed green lights; private contractors not | "Maintenance vehicles… green lights" / "Private contractors are not allowed to display green lights." (l. 2031-2049) |
| 148 | 500-ft minimum behind moving emergency vehicle | "Stay at least 500 feet behind any moving emergency vehicle" (l. 2106-2107) |
| 150/152 | School bus red lights → stop ≥20 ft; yellow lights → prepare to stop | Lines 2121, 2147 |
| 173/174/175 | Roundabout right-of-way / nearest-exit emergency / go around if missed | Lines 2517-2525 |
| 188 / 192 / 195 / 199 | Parking prohibitions: 15 ft hydrant / 50 ft RR rail / 30 ft sign-beacon / 20 ft fire-station driveway | Lines 2800-2830 |
| 197 | Never use the freeway emergency crossover | "Never drive across the median or emergency crossover" (l. 3054-3057) |
| 213-215 | Michigan Left definition and single-vs-multi-lane behavior | Lines 3313-3335 |
| 235 | 15-20 mph and ≥20 ft following distance behind horse/buggy | "reduce your speed to 15-20 mph and maintain a safe distance of at least 20 feet between your vehicle and the rider or buggy" (l. 3678-3680) |
| 239 | 3-4 second following distance for motorcycles/cyclists | "Tailgating is illegal. Leave at least 3 or 4 seconds" (l. 3776) |
| 246 | 3-foot minimum passing distance for bicyclists | "Michigan law requires that you leave at least 3 feet" (l. 3891) |
| 249 | NHTSA: 66% of traffic fatalities from aggressive driving | "66 percent of all traffic fatalities are caused by aggressive driving behaviors." (l. 4004-4005) |
| 258 | Fisher Body introduced slanted windshield in 1930 | "In 1930, Fisher Body introduced the slanted windshield" (l. 3945) |
| 264 | 10-minute break every 2 hours to combat freeway fatigue | "stop and take a 10-minute break at least every two hours." (l. 4197-4198) |
| 283 | Notify police if injuries OR damage > $1,000 | "Notify the police if there are injuries or property damage exceeding $1,000." (l. 4454-4455) |
| 284/285 | Don't veer for deer; deer whistles/horn/high-beams are gimmicks | "Do not rely on gimmicks. Deer whistles, flashing… horn will not deter deer." / "Do not veer for deer" (l. 4480, 4485) |
| 305 | Original tests available in many foreign languages, electronic/paper/audio | "Original driver's license tests are available in many foreign languages in electronic, paper, or audio formats." (l. 4888-4890) |
| 306 | Hard-of-hearing/deaf → Michigan Relay Center at 711 | "Hard-of-hearing and deaf customers should contact the Michigan Relay Center at 711." (l. 4886-4887) |
| 308 | DOS Info Center phone = 888-SOS-MICH | "888-SOS-MICH (767-6424)" (l. 805, 939, 4892) |
| 313 | "Michigan's Guide for Aging Drivers and Their Families" = SOS-194 | Resource-materials list (l. 4824) |

### WEDMK content-trap check

The user flagged a known failure mode for WEDMK-based generation: questions asserting that the manual itself is offered in multiple languages or editions. A grep of `questions_en.yaml` for `multilingual`, `spanish`, `chinese`, `arabic`, `hindi`, and `this manual…available in` returned **zero matches that misrepresent the manual itself**. Q83 (interpreter availability during CDL skills test) and Q305 (foreign-language test formats) both refer to the **tests**, not the manual — and both are correctly grounded in lines 927-931 and 4888-4890. No fabricated multilingual-edition trap is present.

### Precision flags

None. Zero items require correction.

## Recall

Methodology: a 31-topic checklist was assembled from the WEDMK table of contents (Chapters 1-7 plus introduction sections) and the test-prep canon for Michigan-specific content (REAL ID, GDL, Kelsey's Law, Michigan Left, organ donor registry, voter registration, etc.). Each topic was probed against the question corpus with keyword regex matching.

| # | Topic | Covered? | Q count |
| --- | --- | --- | --- |
| 1 | Graduated Driver Licensing (GDL) — Levels 1/2/3 | yes | 12 |
| 2 | REAL ID (license / state ID) | yes | 5 |
| 3 | Driver education Segments 1 / 2 | yes | 3 |
| 4 | Temporary Instruction Permit (TIP) | yes | 9 |
| 5 | Kelsey's Law (teen phone restriction) | yes | 3 |
| 6 | Cell phone / distracted driving (all drivers) | yes | 11 |
| 7 | Seat belt law | yes | 7 |
| 8 | Child passenger safety / car & booster seats | yes | 7 |
| 9 | Speed limits (urban / freeway / work zone) | yes | 24 |
| 10 | Construction / work zone | yes | 11 |
| 11 | Emergency vehicles / Move Over law | yes | 10 |
| 12 | School buses (yellow / red flashing) | yes | 6 |
| 13 | Right of way (intersections / pedestrians / funerals) | yes | 25 |
| 14 | Roundabouts (including emergency-vehicle / miss-exit rules) | yes | 7 |
| 15 | Railroad crossings (ENS sign, passive/active control) | yes | 20 |
| 16 | Passing rules (left/right, 100-ft / 200-ft) | yes | 68 |
| 17 | Parking rules (hill, parallel, prohibited distances) | yes | 28 |
| 18 | Traffic sign colors / shapes (octagon / pentagon / pennant) | yes | 86 |
| 19 | Pavement markings (yellow/white, broken/solid, triangles) | yes | 37 |
| 20 | Traffic signals (red/yellow/green; flashing arrows) | yes | 42 |
| 21 | Commercial vehicles / no-zones / passing | yes | 40 |
| 22 | Motorcycles / mopeds / bicycles | yes | 34 |
| 23 | Pedestrians (white cane / guide dog) | yes | 35 |
| 24 | Alcohol & drugs (DUI/OWI, marijuana, chemical test) | yes | 16 |
| 25 | Bad weather / skidding / braking (ABS vs. non-ABS) | yes | 141 |
| 26 | Aggressive driving / defensive driving | yes | 6 |
| 27 | Crashes — what to do after / move-to-shoulder rule | yes | 13 |
| 28 | Point system / penalties / suspension / revocation | yes | 40 |
| 29 | Headlights / night driving (high vs low beam) | yes | 21 |
| 30 | Vision / health / physician statement | yes | 10 |
| 31 | Voter registration / state ID card | yes | 14 |

**Coverage rate: 31/31 = 100%**

Michigan-specific topics (Michigan Left, Kelsey's Law, vehicle-deer crashes, Recreational Double "R" endorsement, 12-year renewal cycle, free state ID for 65+) are all represented. No critical recall gaps were found.

## Coverage

### Category balance

All 10 canonical categories are present. The largest single share (`safe_driving_rules`, 24.0%) is well under the 40% over-concentration threshold, and the shape mirrors the manual's emphasis (rules of the road and signs/signals dominate the WEDMK content).

| Category | Count | Share |
| --- | --- | --- |
| safe_driving_rules | 84 | 24.0% |
| signs_and_signals | 70 | 20.0% |
| license_system | 53 | 15.1% |
| sharing_the_road | 34 | 9.7% |
| defensive_driving | 27 | 7.7% |
| penalties_and_points | 21 | 6.0% |
| driver_testing | 20 | 5.7% |
| driver_responsibility | 19 | 5.4% |
| vehicle_information | 14 | 4.0% |
| alcohol_drugs_health | 8 | 2.3% |

Notes:

- `alcohol_drugs_health` (2.3%) is on the low side, but DUI-style content is also tagged under `penalties_and_points` (e.g., chemical-test refusal, drug suspensions, marijuana fines), so the topic itself is well covered — only the canonical-category labeling skews low.
- No missing categories. No over-concentration.

### Question-count vs manual size

| Metric | Value |
| --- | --- |
| Manual chars | 204,792 |
| Question count | 350 |
| Density | 1.71 Qs per 1,000 chars |

The cohort target band is 0.5-3.0 Qs/1k chars. MI at 1.71 sits comfortably mid-range, almost identical to MN (1.70), confirming the bank is neither thin nor padded.

### Sign-question contribution

34 of 350 questions (9.7%) use `image:`-tagged MUTCD sign assets — squarely inside the typical 8-12% band for the cohort. Sign distribution is entirely within `signs_and_signals`.

### Data integrity checks

- Unique question IDs: 350 / 350 (1-350, no duplicates)
- Structural audit (`tools/audit_questions.py mi`): **0 issues**
- All 10 canonical categories present
- Manifest declares 1 source (`manual_part_1.pdf` = `manual.pdf`); SHA-256 matches
- Multi-source plumbing intact; no chapter-header duplication detected in `manual_text.txt`

## Recommended Actions

Severity tags: `[low]` cosmetic / additive, `[med]` ought to fix, `[high]` blocks a passing grade.

1. `[low]` **Optionally rebalance the `alcohol_drugs_health` tag.** Several DUI-related questions (Q107, Q108, Q111, Q112, Q117, Q123, Q156, Q167, Q312) sit under `penalties_and_points` but read as much like alcohol/drug content. Retagging a handful would lift the `alcohol_drugs_health` share from 2.3% toward the ~5% norm without changing any wording. Purely cosmetic; current state already passes the coverage rubric.
2. `[low]` **Consider 1-2 questions on the 130-140 ft passenger-car stopping distance at 55 mph** if the manual section is expanded in a future edition; the current bank covers commercial-vehicle stopping distance (Q225) but not the passenger-car analogue cited in Ch. 7's stopping-distance section. Not strictly required — the topic is borderline (manual emphasizes commercial vehicles).
3. `[low]` **No precision corrections required.** Every claim spot-checked traced back to the source manual, including the historically-precise items (Detroit PD 1945 chemical test, Fisher Body 1930 windshield, 2023 Michigan crash facts). The known WEDMK "multilingual editions of the manual" content trap is **not** present.

Overall the MI question bank is high quality: tight grounding in the October 2025 edition, complete recall across the WEDMK table of contents (including Michigan-specific items like Michigan Lefts, Kelsey's Law, the Recreational Double "R" endorsement, and the 12-year renewal cycle), and balanced category coverage. Safe to ship as-is.
