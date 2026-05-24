# Minnesota (MN) — Quiz Quality Report

| Field | Value |
| --- | --- |
| State | Minnesota |
| Agency | DVS (Driver and Vehicle Services) |
| Manual | Minnesota Driver's Manual (May 2025) |
| Manual edition | 2025-05 |
| Manual SHA-256 | `281569fb6a732fa37d3a9a4c5ac8fa4d50ff71c69190f20e58399ff59fd43b74` |
| Manual size | 225,888 chars / 104 pages |
| Total questions | 383 |
| Sign questions | 34 (9%) |
| Non-sign questions | 349 (91%) |
| Question density | 1.70 Qs per 1,000 chars of manual text |
| Languages shipped | English, Spanish |
| Structural audit | `tools/audit_questions.py mn` -> 0 issues |

## Score

| Axis | Result | Grade |
| --- | --- | --- |
| Precision | 60/60 sampled non-sign questions fully grounded after manual review (100%); zero fabrications or contradictions found | **A** |
| Recall | 39/40 critical MN-test topics covered (97.5%); 1 minor gap (stopping-distance numeric) | **A** |
| Coverage | All 10 canonical categories present; max category share 21.4% (safe_driving_rules); density 1.70 Qs/1k chars - well-balanced | **A** |
| **Overall** | All three axes A. Hand-authored winter questions (382, 383) are tightly grounded in manual lines 3681-3691. | **A** |

## Precision

Methodology: random sample of 60 non-sign questions (seed=42) checked via distinctive-phrase grep against `manual_text.txt`. Phrases not matched were re-inspected manually with broader context queries.

| Result | Count | % |
| --- | --- | --- |
| Grounded by direct phrase match | 45/60 | 75% |
| Grounded after manual paraphrase verification | 15/60 | 25% |
| **Total grounded** | **60/60** | **100%** |
| Partial / weak grounding | 0 | 0% |
| Fabricated / contradicted | 0 | 0% |

All 15 initial misses were false negatives of the phrase-match heuristic (paraphrasing of manual prose). Each was verified manually:

| ID | Claim | Manual evidence |
| --- | --- | --- |
| 16 | Interfering with DVS employee is a crime (Minn. Stat. 609.50 Subd. 5) | "It is a crime to interfere with the work of a DVS employee. Minnesota Statute 609.50, Subdivision 5." |
| 36 | Translator must not be related by blood/marriage to subject | "The translator is not related by blood or marriage to the subject of the document." |
| 58 | Permit at 15: 30 hrs classroom + enrolled BTW | "Complete 30 hours of classroom instruction and be enrolled in behind-the-wheel instruction; or be enrolled in a concurrent..." |
| 64 | Provisional license loss -> 3-month permit at 18 | "Obtain an instruction permit and hold it for three months." (provisional path, l. 874) |
| 72 | Immediate family members exempt from passenger limit | "You may have immediate family members under age 20 as passengers during both time periods." |
| 99 | 10 mph in alleys | "10 mph - in alleys" (default speed limits list) |
| 126 | Uphill with curb -> wheels away from curb | "When the front of a parked vehicle points uphill, and there is a curb, wheels should be turned away from the curb." |
| 173 | Bicyclist may proceed if signal red for unreasonable time | "The traffic signal shows a red light for an unreasonable time." |
| 175 | Mopeds banned from sidewalks/freeways/bike trails | "Motorized bicycles are not allowed on sidewalks, freeways, or lanes and trails designated for pedestrians and bicycles." |
| 195 | Zipper merge reduces backups up to 40% | "Reduces the overall length of traffic backups by up to 40 percent." |
| 230 | SIPDE = Scan, Identify, Predict, Decide, Execute | "Using the Scan, Identify, Predict, Decide and Execute (SIPDE) System" |
| 296 | 12 oz beer = 5 oz wine = 9 oz wine cooler ~ same alcohol | "A 12-ounce beer, a 5-ounce glass of wine, a typical mixed drink and a 9-ounce wine cooler usually contain about the same..." |
| 309 | 1st-offense DWI: 90-day revocation (30 if plead guilty) | "Minimum of 90-day revocation (30 days if you plead guilty to DWI)." |
| 339 | Provisional license is a license classification | Section "Getting your under 18 Class D provisional license" + checklist |
| 347 | GDL = Graduated Driver's Licensing | "Graduated Driver's Licensing (GDL) system" |

**Hand-authored winter questions (Q382, Q383)** — explicitly called out for verification by the onboarding agent:

| ID | Topic | Grounding |
| --- | --- | --- |
| 382 | Snowplow following / passing behaviour | Verbatim phrasing matches manual l. 3686-3690: "Never crowd a snowplow. Pass snowplows only when you can see the entire vehicle. Stay well behind... 'whiteout' conditions." |
| 383 | Snow-emergency parking compliance | Verbatim phrasing matches manual l. 3681-3684: "When a significant amount of snow accumulates, city officials may declare a snow emergency... Obey snow emergency parking rules to avoid towing and fines." |

Both hand-authored items are **well-grounded** and use phrasing close enough to the manual to qualify as direct paraphrase rather than synthesis.

### Precision flags

None. Zero items require correction.

## Recall

Methodology: hand-curated list of 40 critical Minnesota-test topics derived from the manual's table of contents plus the user's MN-specific call-outs (snow-emergency parking, snowplow following distance, skid recovery). Each topic was probed against the question-bank corpus via keyword matching.

| # | Topic | Covered? | Representative Q |
| --- | --- | --- | --- |
| 1 | GDL / Graduated Driver Licensing | yes | Q347, Q58, Q72 |
| 2 | REAL ID requirements | yes | Q5 |
| 3 | Driver's License for All / proof of legal presence | yes | Q4 |
| 4 | Seat belt / child restraint laws | yes | Q2, Q128 |
| 5 | Speed limits (urban / rural / alley / freeway) | yes | Q99 (10 mph alleys), Q234 |
| 6 | Right-of-way rules | yes | various |
| 7 | Stopping for school buses | yes | Q142, Q303 |
| 8 | Move Over law / emergency vehicles | yes | Q152, Q153 |
| 9 | **Snow emergency parking** (MN-specific) | **yes** | **Q383 (hand-authored)** |
| 10 | **Sharing road with snowplows** (MN-specific) | **yes** | **Q382 (hand-authored), Q256** |
| 11 | **Skid recovery / loss of traction** (MN-specific) | **yes** | **Q262** |
| 12 | Anti-lock brakes (ABS) | yes | covered in defensive_driving |
| 13 | Hydroplaning | yes | covered in defensive_driving |
| 14 | Following distance / 3-second rule | yes | Q232, Q234, Q176, Q243, Q251 |
| 15 | Stopping distance (total / reaction / braking) | **NO** | gap - see Recommended Actions |
| 16 | Distracted driving / texting / phones | yes | Q139, Q247, Q245 |
| 17 | Alcohol / DWI / BAC | yes | Q296, Q299, Q307, Q308, Q315 |
| 18 | Drugs / cannabis impairment | yes | various |
| 19 | Crash reporting / what to do after crash | yes | Q135, Q145 |
| 20 | Insurance requirements | yes | Q135 |
| 21 | Roundabouts | yes | Q113 |
| 22 | Lane use / changing lanes / passing | yes | Q121, Q195 (zipper merge) |
| 23 | Railroad crossings | yes | Q189, Q202 |
| 24 | Pedestrians / crosswalks | yes | Q3 |
| 25 | Bicycles / sharing the road | yes | Q1, Q3, Q170, Q173 |
| 26 | Motorcycles | yes | Q176, Q177 |
| 27 | Work zones / construction | yes | covered in safe_driving_rules |
| 28 | Vision test | yes | covered in driver_testing |
| 29 | Renewal / address change | yes | Q322 |
| 30 | Penalties / points / suspension / revocation | yes | Q287, Q289, Q291, Q345 |
| 31 | Vanessa's Law (teen DUI) | yes | Q63, Q64 |
| 32 | Funeral procession | yes | Q160 |
| 33 | Roadway emergencies / breakdowns | yes | Q241, Q267, Q283 |
| 34 | Driver fatigue / drowsy driving | yes | Q261 |
| 35 | Sign types (regulatory / warning / guide) | yes | signs_and_signals category (59 Qs) |
| 36 | Stop sign / yield sign | yes | various sign Qs |
| 37 | Traffic signal colors (red/yellow/green/flashing) | yes | various |
| 38 | Parking rules (uphill / downhill / curb) | yes | Q126 |
| 39 | Vehicle equipment (lights, tires, brakes) | yes | Q92, Q267, Q284 |
| 40 | Organ donor | yes | Q330 |

**Coverage rate: 39/40 = 97.5%**

The single gap is **stopping distance with concrete numbers**. The manual states (l. 2587, 3343-3345) "An average passenger car traveling at 55 mph can stop within 130 to 140 feet" and devotes a dedicated section to stopping-distance factors — but no quiz question targets these specifics. This is a minor omission since following-distance (3-second rule) and skid recovery are both covered.

## Coverage

### Category balance

All 10 canonical categories are present. None exceeds 30%; only one (`safe_driving_rules`) exceeds 20%, which is expected for the umbrella category.

| Category | Count | Share |
| --- | --- | --- |
| safe_driving_rules | 82 | 21.4% |
| license_system | 63 | 16.4% |
| signs_and_signals | 59 | 15.4% |
| sharing_the_road | 36 | 9.4% |
| penalties_and_points | 35 | 9.1% |
| defensive_driving | 27 | 7.0% |
| vehicle_information | 25 | 6.5% |
| driver_testing | 23 | 6.0% |
| alcohol_drugs_health | 18 | 4.7% |
| driver_responsibility | 15 | 3.9% |

No missing categories. No over-concentration. The shape mirrors the manual's emphasis (driving rules and licensing make up the bulk of the source).

### Question-count vs manual size

| Metric | Value |
| --- | --- |
| Manual chars | 225,888 |
| Question count | 383 |
| Density | 1.70 Qs per 1,000 chars |

The 34-state cohort target is ~1.5 Qs/1k chars. MN is slightly above average, consistent with the longer 104-page manual that includes detailed MN-specific winter / snow / new-law content. Not an outlier.

### Sign-question contribution

34 of 383 questions (8.9%) use `image:` MUTCD sign assets — within the typical 8-12% band for the cohort. Sign distribution is exclusively in `signs_and_signals`.

### Data integrity checks

- Unique question IDs: 383 / 383 (no duplicates)
- Structural audit (`tools/audit_questions.py mn`): **0 issues**
- All 10 canonical categories present
- Hand-authored Qs 382-383 conform to the same schema as generated questions

## Recommended Actions

Severity tags: `[low]` cosmetic / additive, `[med]` ought to fix, `[high]` blocks a passing grade.

1. `[low]` **Add 1-2 stopping-distance questions.** Manual l. 2587 and l. 3343-3345 explicitly cover stopping distance numerics ("130 to 140 feet at 55 mph") and the three components (perception / reaction / braking). Suggested item: *"According to the manual, approximately how far can an average passenger car traveling at 55 mph take to stop?"* -> 130-140 feet. Closes the single recall gap.
2. `[low]` **Optionally add an ABS technique question.** Manual l. 3766-3770 specifies "do not pump ABS brakes; press firmly and hold." The topic is covered conceptually but no question targets the technique distinction (pump vs. press-and-hold), which is a common test-prep item.

No precision corrections required. The MN question bank is high quality overall: strong grounding, broad recall, balanced category coverage, and the MN-specific winter content (snow emergency parking, snowplow handling, skid recovery) is well covered thanks to the onboarding agent's hand-authored additions.
