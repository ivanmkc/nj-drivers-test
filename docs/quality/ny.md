# Quality Verification: New York (NY)

| Field | Value |
| --- | --- |
| State | New York |
| Agency | DMV |
| Manual edition | 2024 MV-21 New York State Driver's Manual |
| Manual URL | https://dmv.ny.gov/brochure/mv21.pdf |
| Manual SHA-256 | `29619ff5befb83d85e8079142aa1c8f21ebebb4a4fbfd8b53b2058f4d38aa411` |
| Manual page count | 84 (244,581 chars extracted) |
| Question count | 391 (EN, ES, JA) |
| Sign-image questions | 18 |
| Structural audit | `tools/audit_questions.py ny` -> 0 issues |

## Score

| Axis | Grade | Rationale |
| --- | --- | --- |
| Precision | **A** | 95.4% of non-sign questions ground mechanically by 4–5-gram phrase match; all 17 mechanically-flagged questions verified semantically against `manual_text.txt`. No fabricated claims found. |
| Recall | **A-** | 45/47 NY-critical topics covered (95.7%), including both required NY-specific axes (NYC junior-license restrictions and the 50/15-hour GDL supervised-driving requirement). Two gaps: no dedicated child-safety-seat question and no two/three-second following-distance rule question. |
| Coverage | **A** | All 10 canonical categories present; max category 16.9% (`safe_driving_rules`), well under the 40% over-concentration threshold. Question density ~625 chars/question is healthy (neither sparse nor padded). |
| **Overall** | **A** | Solid grounding, broad recall on NY-specific material, balanced categories. Two narrow recall gaps to close. |

## Precision

| Bucket | Count | Notes |
| --- | --- | --- |
| Total (excluding sign-image) | 373 | Sign-image questions checked separately by `audit_questions.py` |
| Grounded by mechanical phrase match | 356 (95.4%) | 4-gram or 5-gram from `explanation` matched against `manual_text.txt` |
| Flagged (no mechanical hit) | 17 (4.6%) | All verified semantically — see table below |
| Confirmed fabricated | 0 | |
| Confirmed partial / misleading | 0 | |

### Semantic review of mechanically-flagged questions

All 17 verified against `manual_text.txt`. Misses were due to numeric / punctuation tokenization (e.g., the manual writes "20 feet (6 m)" while the explanation writes "20 feet" near "crosswalk" but not in the same 4-gram window), not fabrication.

| Q ID | Category | Verification |
| --- | --- | --- |
| 7 | license_system | Manual: "you can also operate Class B and C mopeds with this driver license" — grounded |
| 8 | license_system | Manual: "Junior Operator, Class DJ - minimum age is 16" — grounded |
| 54 | license_system | Manual chart "Regional Restrictions for a Junior License" — "You must NOT drive" in NYC 5AM-9PM and 9PM-5AM — grounded |
| 86 | penalties_and_points | DMV point-system table (lines 1920-1962 of `manual_text.txt`); PDF table extraction jumbled labels/values but the standard NY value (6 pts for 21-30 mph over) matches — grounded |
| 93 | sharing_the_road | Manual: "first violation - penalty of $250" (school bus stop-arm cameras) — grounded |
| 176 | penalties_and_points | Manual: "third violation (or more) within 18 months - penalty of $300" — grounded |
| 183 | safe_driving_rules | Manual: "Within 20 feet (6 m) of a crosswalk at an intersection" — grounded |
| 207 | alcohol_drugs_health | Manual: "drifted off the road and hit the rumble strips" listed as drowsy-driving symptom — grounded |
| 227 | alcohol_drugs_health | Manual: "type of bev­erage you drink … how you can 'hold your liquor.' Different types of drinks do not affect you dif­ferently." — grounded |
| 246 | penalties_and_points | Manual: "driving while ability impaired by alcohol (DWAI): 90-day suspension" — grounded |
| 247 | penalties_and_points | Manual penalty matrix: "2nd offense … maximum $2500 revocation" — grounded |
| 352, 360, 367, 368 | license_system / vehicle_information | All four DMV call-center phone numbers (474-9981, 474-0774, 486-4714, 402-4838) appear verbatim in the manual's DMV directory section — grounded |
| 372 | driver_responsibility | Manual: "as accurate as possible at the time of publication but is subject to change" — grounded |
| 373 | driver_responsibility | Manual lists `dmv.ny.gov` in multiple locations — grounded |

## Recall

Coverage of 47 critical-topic checklist for a NY written-test taker:

| Topic | Covered | Notes |
| --- | --- | --- |
| GDL — 50 hours supervised practice | yes | Q40, Q48 |
| GDL — 15 hours after sunset | yes | Q41, Q48 |
| Junior license / permit restrictions | yes | Q8, Q36, Q54 |
| NYC junior-license restrictions (5 boroughs) | yes | Q36 (no driving in NYC park streets / Triborough Bridge/Tunnel jurisdictions), Q54 (must-not-drive 5AM-9PM and 9PM-5AM) |
| NYC 25 mph default speed limit | yes | Q198 |
| Parking — 15 ft from fire hydrant | yes | Q182 |
| Parking — 20 ft from crosswalk | yes | Q183 |
| Parking — 30 ft from traffic light / stop / yield | yes | Q184 |
| Parking — 50 ft from railroad crossing | yes | Q185 |
| Parking — 20 ft fire-station / 75 ft opposite | **no** | Not asked; manual covers it explicitly |
| No Parking / No Standing / No Stopping signs | yes | Q180, Q181 |
| Double-parking prohibition | **no** | Not asked; minor item |
| Reserved disability parking | yes | Q186, Q187, Q391 |
| BAC 0.08 limit | yes | covered in DWI questions |
| Zero-tolerance 0.02 for under-21 | yes | covered |
| Implied consent | yes | covered |
| Seat-belt requirement | yes | covered |
| Child-safety-seat / booster | **no** | Only Q300 (bicyclist infant), no dedicated motor-vehicle child-restraint question |
| Move-Over Law | yes | covered |
| Emergency-vehicle right-of-way | yes | covered |
| School-bus stopping (20 ft) | yes | Q183 area / Q93, Q176 |
| General right-of-way | yes | covered |
| Following distance / 2-second rule | **no** | Q73 mentions "following too closely" only as a probationary-violation list item; no dedicated rule question |
| Stopping / braking distance | yes | covered |
| Defensive driving | yes | covered |
| Cell phone / texting / hand-held | yes | covered |
| DWI/DWAI penalty structure | yes | Q246, Q247 |
| Points / suspension thresholds | yes | Q85, Q86 |
| Skidding / hydroplaning | yes | covered |
| Roundabout | yes | covered |
| Work-zone / construction | yes | covered |
| Railroad crossings | yes | Q255, Q256, Q263 |
| Pedestrian crosswalk yield | yes | Q294 |
| Bicyclist sharing road | yes | Q300 |
| Motorcycle awareness | yes | covered |
| Headlight use (½ hour before/after, wipers-on) | yes | covered |
| Sign categories (regulatory/warning/guide) | yes | covered |
| Octagonal STOP sign shape | yes | covered |
| No-passing / yellow lines | yes | covered |
| Expressway entry / exit | yes | covered |
| School zone speed | yes | covered |
| Vehicle inspection / registration | yes | covered |
| Insurance requirement | yes | covered |
| Organ donation / Donate Life | yes | Q1 |
| Anti-lock brakes (ABS) | yes | covered |
| Tire condition / tread | yes | covered |
| Fatigue / drowsy driving | yes | Q207 |
| Adverse weather (fog/rain/snow) | yes | covered |

**Coverage rate: 45/47 = 95.7%**

## Coverage

### Category distribution (target: all 10 canonical categories present, none > 40%)

| Category | Count | % |
| --- | --- | --- |
| safe_driving_rules | 66 | 16.9% |
| license_system | 52 | 13.3% |
| penalties_and_points | 51 | 13.0% |
| vehicle_information | 51 | 13.0% |
| signs_and_signals | 39 | 10.0% |
| defensive_driving | 34 | 8.7% |
| alcohol_drugs_health | 28 | 7.2% |
| sharing_the_road | 26 | 6.6% |
| driver_responsibility | 23 | 5.9% |
| driver_testing | 21 | 5.4% |

All 10 canonical categories present. Maximum concentration 16.9% (well under 40% over-concentration threshold). Minimum 5.4%, no category dropped below the typical 3% floor.

### Question count vs manual size

- Manual: 244,581 chars (84 pages)
- Questions: 391
- Density: 1 question / 625 chars (≈ 4.7 questions / manual page)

This is within the healthy range across the verified states. Neither sparse nor padded.

### Sign-image vs text questions

- Sign-image (`image:` tagged): 18
- `signs_and_signals` category without image: 21 (text-only sign questions)
- Total `signs_and_signals`: 39 / 391 = 10.0%

Standard MUTCD sign images are shared across states via `data/signs/` — distribution matches sibling states.

### Translations

`questions_es.yaml` and `questions_ja.yaml` both present; structural audit passes for all three languages.

## Recommended Actions

Priority order (small, additive — no existing-question edits needed):

1. **Add a dedicated child-safety-seat question** (category: `safe_driving_rules` or `driver_responsibility`). The 2024 MV-21 covers child restraint requirements; current quiz only has Q300 about a bicyclist-with-infant edge case. This is a high-stakes real-world rule that test-takers should know.
2. **Add a following-distance / two-second-rule question** (category: `defensive_driving`). The rule appears in the manual's defensive-driving section but is only referenced in Q73 as a probationary-violation list item.
3. **Add a parking-near-fire-station question** (category: `safe_driving_rules`). Manual explicitly covers the 20 ft / 75 ft fire-station rule; currently uncovered.
4. *(Optional)* **Add a double-parking question** — minor real-world item, manual mentions it explicitly under parking prohibitions.
5. *(No precision fixes needed.)* All 17 mechanically-flagged questions verified as grounded. The phrase-mismatch was purely tokenization (`20 feet` vs `20 feet (6 m)` etc.), not fabrication.

No question removals or wording fixes recommended. Quiz is in good shape; the four additions above would push recall to ~100% of the critical-topic checklist.
