# Louisiana (LA) — Quiz Quality Report

- **State:** Louisiana
- **Agency:** Office of Motor Vehicles (OMV)
- **Manual edition:** 2017 Louisiana Class D & E Driver's Guide
- **Manual size:** 370,913 chars / 145 PDF pages
- **Questions:** 588 (English); also translated to Spanish
- **Structural audit (`tools/audit_questions.py la`):** 0 issues
- **Report generated:** 2026-04-29

## Score

**Overall: A**

| Axis      | Score | Grade |
|-----------|-------|-------|
| Precision | 100% grounded (mechanical + targeted phrase verification) | A |
| Recall    | 25/25 critical test-relevant topics covered (100%) | A |
| Coverage  | All 10 canonical categories represented; top category 28.2% (below 40% overconcentration threshold) | A |

Caveat: manual is the 2017 edition, so any specific dollar amount, fee, or DUI penalty may be out of date relative to current Louisiana statute. The questions reflect the manual faithfully, but the manual itself is ~9 years stale as of 2026. See [Recommended Actions](#recommended-actions).

## Precision

Methodology: For each of the 554 non-sign questions, distinctive 5-gram phrases from the `explanation` field were matched against `manual_text.txt` (normalized whitespace, case-insensitive). Phrases not matched were then re-checked via targeted keyword/sub-phrase searches on the distinctive facts (entities, dollar amounts, named programs, chapter section headers).

| Bucket | Count | % |
|--------|-------|---|
| Grounded by 5-gram match  | 538 | 97.1% |
| Grounded by targeted keyword re-check | 16 | 2.9% |
| Partial / paraphrased but accurate | 0 | 0% |
| Fabricated | 0 | 0% |
| **Total non-sign questions** | **554** | **100%** |
| Sign-image questions (visual, not text-grounded) | 34 | — |

### Initially-flagged questions that re-checked clean

The 16 questions that failed strict 5-gram matching all rely on heavy paraphrasing of section headers, table-of-contents entries, or short topical phrases. Each was verified to be substantively grounded:

| ID  | Topic | Grounding evidence in manual |
|-----|-------|------------------------------|
| 3   | Commissioner's safety belt message | "Safety belts save lives", "buckle up" both present |
| 7   | Ch. 6 automobile insurance fraud | "AUTOMOBILE INSURANCE FRAUD" present |
| 12  | Ch. 5 aggressive driving/road rage | "AGGRESSIVE DRIVING/ROAD RAGE" present |
| 13  | Revocation of license in Ch. 1 | "REVOCATION OF YOUR LICENSE" present |
| 40  | Primary vs secondary documents | "primary document", "certificate of birth" present |
| 46  | 50 hours behind-the-wheel for intermediate | "fifty (50) hours" present verbatim |
| 125 | "Pass With Care" sign meaning | "Pass With Care" present |
| 162 | Infant rear-facing seat | "rear facing", "federally approved" present |
| 232 | Don't drive when emotional | "worried, nervous" present |
| 234 | 6–8 hour driving limit | "six or eight hours" present |
| 286 | Red curb = fire zone | "fire zone", curb color rules present |
| 349 | Hands visible at traffic stop | "Keep your hands visible" present |
| 375 | Hand signal for right turn | "hand signal", "left arm" present |
| 452 | Four collision factors | "equipment failure", "roadway design", "driver behavior" all present |
| 479 | Wheel-loss warning signs | "thumping noise", "loss of a wheel", "pulling to one side" present |
| 484 | Carbon monoxide symptoms | "carbon monoxide", "yawning", "dizziness" all present |

### Dollar-amount / fine / fee questions

Per the special concern about 2017 manual staleness, every question that cites a specific dollar amount, fee, or penalty was individually traced to the manual:

| ID  | Claim | Manual confirmation | Staleness risk |
|-----|-------|---------------------|----------------|
| 26  | ID card 60+: $0.00, lifetime | "$0.00" and "Lifetime" in fee table | LOW (waiver unlikely to have reversed) |
| 28  | Class D license usage for hire | Verbatim quote in manual | LOW (statutory definition) |
| 29  | $12.00 handling fee, 60+ ID exempt | "$12.00 handling" present | **MEDIUM — fee likely changed since 2017** |
| 70  | Withdrawing from school can lose privilege | "withdrawing from school" present | LOW |
| 74  | Severe littering: $5,000 / 1 yr / 30 days / 100 hrs | All elements present verbatim | **MEDIUM — penalties may have been amended** |
| 83  | Motor Voter Act 1993 | "national voter registration act", "motor voter" present | LOW (federal law) |
| 96  | 2010 crash cost $1,855.00 per LA driver | "$1855" and "2010" present verbatim | **LOW factually, but very dated context (2010 stat in a 2017 manual quoted in 2026)** |
| 397 | Fuel theft: fine, loss of license, jail | "theft of motor vehicle fuel" passage present | LOW |
| 507 | Implied-consent refusal = 365-day suspension (1st) | "365 days", "first offense", "implied consent" all present | **MEDIUM — review against current LA RS 32:667** |
| 511 | Hit-and-run definition | "hit and run" definition present | LOW |
| 515 | Drug DUI same penalty as alcohol DUI | "same penalty", "over-the-counter", "prescribed" present | LOW (policy unchanged) |
| 552 | Private minimum-use pickup ≤6000 lbs: $10/yr, 4-yr plate | "private minimum-use", "6000 lbs", "4-year period" present | **MEDIUM — registration fees often adjusted** |

All 12 are faithful to the 2017 manual. The four flagged MEDIUM-risk items are not precision defects (the question accurately reports what the manual says) but candidates for a follow-up cross-check against current Louisiana statute when the manual is refreshed.

## Recall

Methodology: 25 critical topics that any LA driver's-test taker must know were enumerated from standard driver-manual scope, then each topic was searched against the union of every question's `question` + `choices` + `explanation` text. A topic is "covered" if at least one question matches its keyword set.

| # | Critical topic | Questions | Status |
|---|----------------|----------:|--------|
| 1 | Graduated Driver Licensing (learner/intermediate) | 8 | covered |
| 2 | License classes (Class D, Class E) | 6 | covered |
| 3 | License fees and renewal | 56 | covered |
| 4 | Required documents (primary/secondary) | 5 | covered |
| 5 | Vision requirements / eye test | 19 | covered |
| 6 | Speed limits (urban, rural, school zone) | 52 | covered |
| 7 | Right-of-way at intersections | 53 | covered |
| 8 | Stop signs / signals | 15 | covered |
| 9 | Traffic signal colors / arrows | 17 | covered |
| 10 | Pavement markings (yellow, white) | 6 | covered |
| 11 | Following distance / 2-3 second rule | 20 | covered |
| 12 | Passing rules and no-passing zones | 29 | covered |
| 13 | Lane changes and signaling | 11 | covered |
| 14 | Parking rules (parallel, hill, no-parking) | 40 | covered |
| 15 | Sharing road with motorcycles/bicycles/trucks | 27 | covered |
| 16 | Pedestrian right-of-way / crosswalks | 27 | covered |
| 17 | School bus stopping rules | 10 | covered |
| 18 | Emergency vehicles / Move Over law | 8 | covered |
| 19 | Railroad crossings | 30 | covered |
| 20 | DUI / BAC limits / implied consent | 43 | covered |
| 21 | Seat belts and child restraints | 28 | covered |
| 22 | Distracted driving / texting / cell phones | 8 | covered |
| 23 | Accident reporting / hit-and-run | 56 | covered |
| 24 | Insurance requirements (compulsory) | 9 | covered |
| 25 | Suspension, revocation, points | 13 | covered |

**Recall: 25/25 (100%).** No critical-topic gaps. The bank is comparatively thin on `distracted driving / cell phones` (only 8 questions); Louisiana has had a hands-free law update since the 2017 manual and that area could grow when the manual is refreshed.

## Coverage

### Category distribution (10 canonical categories)

| Category | Count | % | Notes |
|----------|------:|---:|-------|
| safe_driving_rules    | 166 | 28.2% | largest — below 40% overconcentration threshold |
| defensive_driving     | 93  | 15.8% | |
| vehicle_information   | 69  | 11.7% | |
| signs_and_signals     | 66  | 11.2% | includes 34 image-tagged sign questions |
| license_system        | 53  | 9.0%  | |
| sharing_the_road      | 50  | 8.5%  | |
| driver_responsibility | 43  | 7.3%  | |
| penalties_and_points  | 23  | 3.9%  | thin — could absorb more questions |
| alcohol_drugs_health  | 17  | 2.9%  | thin given DUI testing weight; see Recommended Actions |
| driver_testing        | 8   | 1.4%  | very thin (smallest category) |

All 10 canonical categories are represented. No category exceeds 40%. Two categories (`alcohol_drugs_health`, `driver_testing`) are notably under-represented.

### Manual-to-question density

- Manual text: 370,913 chars
- Questions: 588
- **Ratio: ~631 chars/question** — well within healthy range observed across other states (typical 500–1,500). LA is on the denser side (lots of questions per page), but the audit + grounding work shows no fabrication, so density appears genuine.

### Sign-question contribution

- Total: 34 image-tagged sign questions out of 588 (5.8%)
- Generated text questions: 554 (94.2%)
- Sign questions exist within `signs_and_signals` and are grounded in shared MUTCD sign images (`data/signs/`), not the manual text.

## Recommended Actions

### Human-review (2017 manual staleness — flagged per task brief)

These questions are textually faithful to the 2017 manual but cite specific dollar amounts or fixed penalties that may have changed under current Louisiana law. A human reviewer should cross-check each against the current LA statutes / OMV fee schedule before assuming they are still correct in 2026:

- **Q26** — ID Card (60+) "$0.00 for a Lifetime term" (verify fee waiver is still in place)
- **Q29** — "$12.00 handling fee" (OMV handling fees frequently adjusted)
- **Q74** — Severe littering penalty: $5,000 fine / 1 yr suspension / 30 days jail / 100 hrs community service (verify against current LA RS 30:2531/32:387)
- **Q96** — "2010 motor vehicle crashes cost $1,855.00 per licensed driver" — accurate per 2017 manual but presents 16-year-old statistics as current; consider replacing with up-to-date NHTSA / LA DOTD figures when manual refreshes
- **Q507** — Implied-consent first-refusal suspension "365 days" (verify against current LA RS 32:667)
- **Q552** — Private minimum-use pickup ≤6000 lbs registration: "$10.00 per year" / "4-year period" plate (registration fees frequently amended)

### Content-balance improvements (low priority, fine-tuning)

- `driver_testing` is only 8 questions (1.4%). Consider adding 8–12 more (e.g., test format, retesting after failure, required documents at test, skills-test scoring).
- `alcohol_drugs_health` is only 17 questions (2.9%) — light for a topic that is heavily weighted on the actual exam. Adding questions about alcohol absorption, drug categories, and health conditions affecting driving would harden this category.
- `distracted driving / cell phones` cluster is thin (8 questions). When the manual is refreshed to a post-2020 edition, expand this cluster to reflect modern hands-free law.

### Maintenance

- **Refresh the manual.** The 2017 edition is the root cause of all staleness risk above. Re-running the onboarding pipeline against the current OMV PDF (when published) will regenerate every question with up-to-date facts. Track this via the `refresh-manual-catalog` OpenSpec change.
- No precision defects identified. No category misclassifications observed. No fabricated content. No duplicates flagged by `tools/audit_questions.py`.
