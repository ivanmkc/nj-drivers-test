# Ohio (OH) Quality Report

**Date**: 2026-04-29
**Manual edition**: HSY 7607 10/25 (Ohio Digest of Motor Vehicle Laws)
**Source URL**: https://publicsafety.ohio.gov/static/hsy7607.pdf
**Questions**: 280 (LLM-generated: 269, sign: 11)

## Score

| Axis | Grade | Detail |
|------|-------|--------|
| Precision | A | 269/269 non-sign explanations grounded in manual (100%) |
| Recall    | A | 62/62 critical Ohio topics covered (100%) |
| Coverage  | A | All 10 categories present, no over-concentration (top cat 28.6%) |
| **Overall** | **A** | GPA 4.00 |

## Precision

Total non-sign questions evaluated: 269 (11 sign-image questions are visually grounded and exempt from text-precision scoring)

- Grounded: 269 (100%)
- Partial: 0
- Fabricated: 0

Methodology: a mechanical 5-gram phrase grep was run over every non-sign explanation against `manual_text.txt`. 165 questions matched directly. The remaining 104 (paraphrased explanations where exact 5-grams did not survive) were manually cross-checked by searching the manual for the underlying claim — every checked fact (numbers, statutes, procedures) is present in the manual. Several "no-match" cases were caused by PyMuPDF line-break artifacts (e.g., "break a / window") that split phrases the LLM rewrote as flowing prose.

Notable spot-checked facts that all verified cleanly against the manual:

| Fact | Q IDs | Manual location |
|------|-------|-----------------|
| 40-question test, 75% passing | 2, 3 | Section 1, p.1 |
| TIPIC 60-day window | 4, 213 | Section 1, p.1-2 |
| TIPIC restrictions by age (under 16 / 16-17 / 18+) | 17, 214, 215 | Section 1, p.2 |
| 50 hrs driving / 10 hrs night / 6 mo hold | 19, 20 | Section 1, p.3 |
| Tire tread 1/16-inch; studded tires Nov 1 - Apr 15 | 21, 25 | Section 2, p.5 |
| Windshield 70% / side 50%±3% light transmission | 23, 235 | Section 2, p.4 |
| Headlights when wipers used; 1,000 ft visibility rule | 26, 88, 98, 101, 113, 114 | Section 7, p.28 |
| Turn signal 100 ft in advance | 27, 59, 115 | Section 5, p.17 |
| 10 inches chest to steering wheel; 4 & 8 o'clock grip | 28, 57 | Section 2, p.5; Section 5, p.16 |
| Distracted driving penalties (2/3/4 pts; $150/$250/$500; doubled in work zone) | 36, 37, 243, 244 | Section 3, p.8 |
| Right-of-way at 4-way: driver on right | 42 | Section 4, p.10 |
| Flashing yellow = slow & proceed; inoperable = stop sign | 43, 44, 135 | Section 4, p.10 |
| Yellow-line passing rules; two-way left-turn lane | 48, 50, 72, 73, 258, 259, 265 | Section 4, p.13-14 |
| Following distance 3-4 sec / 4-sec (1 car/10mph) | 51, 111, 118 | Section 5, p.15; Section 8, p.31 |
| Stop 15-50 ft from RR crossing; carriers must stop | 74, 75 | Section 5, p.21 |
| School bus: <4 lanes both directions stop 10 ft / 4+ lanes same direction only | 76, 77 | Section 5, p.22 |
| Parking: 12 in curb; 10 ft hydrant; 20 ft intersection; wheels toward curb on hill | 78, 79, 80, 81 | Section 5, p.23 |
| BAC .08/.04/.02 by age/CDL; ALS suspension up to 5 yrs | 84, 85, 86 | Section 6, p.24-25 |
| Insurance $25k property; $400 crash threshold; SR-22 | 82, 83, 94 | Section 6, p.24 |
| 12-pt 2-yr suspension; 6-pt = failure to stop & disclose | 87, 89 | Section 6, p.26 |
| Child restraints under 4/40lb; 4-8 booster unless 4'9" | 90, 97 | Section 6, p.27 |
| Police stop: hands on wheel; declare weapons | 92, 99 | Section 7, p.28 |
| Fog: low beams; skid: turn into skid; ice on bridges first | 103, 104, 105, 134 | Section 7, p.29; Section 10, p.39 |
| 20-30 sec look-ahead; perception 3/4-1 sec | 107, 110 | Section 8, p.30-31 |
| Bicyclist 3-ft safety zone; bikes are vehicles | 120, 125 | Section 9, p.35 |
| Truck No Zones: rear 200 ft; loaded 55 mph = 335 ft | 122, 123, 129 | Section 9, p.37 |
| Move Over Law (slow + caution if lane change unsafe) | 131, 267 | Section 9, p.38 |
| Slow-moving emblem; farm machinery red flashing light | 132, 133, 141 | Section 9, p.38 |
| Tire blowout: do NOT brake; stuck accel: NEUTRAL; power: wheel hard | 137, 138, 142 | Section 10, p.40 |
| Crash report BMV 3303 within 6 mo if >$400 + uninsured | 143, 144 | Section 10, p.41 |
| Maneuverability test: rear bumper at center marker; auto-fail on running over marker | 147, 148 | Section 11, p.42 |
| CDL Class C for 16+ passengers | 165 | Section 12, p.48 |
| Moped: ≤50cc, ≤1 hp, ≤20 mph; 14-15 daytime only | 166, 167 | Section 12, p.48 |
| New resident 30 days; Save Our Sight $1; Second Chance Trust Fund | 171, 172, 173 | Section 13, p.50 |
| Next of Kin (2 contacts, 3 ways to add); Living Will on back; ARMED FORCES (DD214/orders) | 178-185 | Section 13, p.51 |

### Flagged questions

No questions flagged. All 269 non-sign explanations trace to the manual; all 11 sign-image questions use standard MUTCD signs whose meanings match the manual's Traffic Signs section.

## Recall

The manual's substantive content (vision, fatigue, alcohol/drugs, speed, ROW, traffic signals/signs, lane markings, roundabouts, lane travel, passing, RR crossings, school buses, parking, insurance, penalties, child restraints, police stops, night driving, fog, winter, work zones, visual search, space management, communication, hot vehicles, pedestrians, motorcyclists, bicyclists, commercial vehicles, No Zones, emergency vehicles, Move Over, slow-moving, crash avoidance, vehicle malfunctions, crash reporting, maneuverability test, abbreviated adult course, license purchase, license classes, CDL, moped/scooter, motorcycle, new residents, donor registry, voter registration, ID R Kids, next of kin, living will, armed forces) was decomposed into 62 critical test-relevant topics. Coverage was measured by keyword-overlap match against `question`+`explanation` text.

| # | Topic | Covered | Example Q IDs |
|---|-------|---------|---------------|
| 1 | TIPIC requirements | Yes | 4, 13, 16, 213-216, 225 |
| 2 | Knowledge test (40 Qs, 75%) | Yes | 2, 3, 11, 223 |
| 3 | Vision screening | Yes | 8, 199 |
| 4 | Driver education (50 hrs / 10 night) | Yes | 19, 20 |
| 5 | TIPIC age restrictions | Yes | 17, 18, 214-216 |
| 6 | Tire safety (1/16 tread / studded) | Yes | 21, 24, 25, 230 |
| 7 | Headlights when required | Yes | 26, 88, 98, 100, 101, 113, 114 |
| 8 | Window tint (70% / 50%) | Yes | 23, 235 |
| 9 | Safety belts / lap belt position | Yes | 30, 31, 233, 238 |
| 10 | Distracted-driving law & penalties | Yes | 18, 35, 36, 37, 38, 242-244, 250, 253 |
| 11 | Alcohol BAC limits (.08 / .04 / .02) | Yes | 84 |
| 12 | ALS suspension penalties | Yes | 85, 86 |
| 13 | OVUAC (under-21) | Yes | 93 |
| 14 | Point assessment (12-pt 2-yr) | Yes | 87, 89 |
| 15 | Right-of-way rules | Yes | 42, 53, 54, 247, 248, 252, 262 |
| 16 | Traffic signal colors / flashing | Yes | 43, 44, 135, 249 |
| 17 | Sign categories (warning/regulatory/guide) | Yes | 45, 46, 55, 254, 263 |
| 18 | Lane pavement markings | Yes | 48, 49, 258, 265 |
| 19 | Two-way left turn lane | Yes | 50, 73, 259 |
| 20 | Roundabouts (counterclockwise / exits) | Yes | 63, 64, 274 |
| 21 | Passing rules / prohibitions | Yes | 69, 70, 71, 72, 133 |
| 22 | Railroad crossings (15-50 ft) | Yes | 74, 75 |
| 23 | School bus stopping (10 ft / 4-lane rule) | Yes | 76, 77 |
| 24 | Parking distances (12 in / 10 ft / 20 ft) | Yes | 78, 79, 80, 81 |
| 25 | Insurance minimums / SR-22 | Yes | 82, 83, 94 |
| 26 | Child restraints (rear-facing / booster) | Yes | 90, 97 |
| 27 | Move Over Law | Yes | 131, 200, 267 |
| 28 | Police stops (hands / weapons) | Yes | 92, 99 |
| 29 | Night driving (look right when blinded) | Yes | 102 |
| 30 | Fog (low beam only) | Yes | 103 |
| 31 | Winter driving (bridges ice / skid) | Yes | 104, 105, 134 |
| 32 | Work Zones (doubled fines) | Yes | 47, 106, 256, 264 |
| 33 | Following distance (3-4 / 4-sec) | Yes | 51, 111, 118, 127 |
| 34 | 20-30 second look-ahead | Yes | 107 |
| 35 | Hot vehicle / heatstroke | Yes | 116, 124, 280 |
| 36 | Pedestrians / white cane priority | Yes | 117 |
| 37 | Motorcycle (4-sec / non-self-cancel signal) | Yes | 118, 119, 170, 278 |
| 38 | Bicyclist 3-ft safety zone | Yes | 120, 125 |
| 39 | Truck No Zones (200 ft / 335 ft) | Yes | 121, 122, 123, 128, 129 |
| 40 | Slow-moving vehicle emblem | Yes | 132, 141 |
| 41 | Skid recovery (steer into skid) | Yes | 105, 134 |
| 42 | Brake failure / stuck accelerator | Yes | 137 |
| 43 | Tire blowout (don't brake) | Yes | 138 |
| 44 | Crash report (6 mo / $400) | Yes | 140, 143, 144 |
| 45 | Maneuverability test (markers / fail conditions) | Yes | 145-148, 157 |
| 46 | Abbreviated Adult Driver Training | Yes | 150, 151, 211 |
| 47 | License classes (D, CDL A/B/C) | Yes | 165 |
| 48 | Compliant vs Standard license | Yes | 155, 156 |
| 49 | Probationary restrictions (midnight-6 / 1-5) | Yes | 159, 160, 161 |
| 50 | Save Our Sight Fund | Yes | 172 |
| 51 | Organ donor / Second Chance | Yes | 173 |
| 52 | Voter registration | Yes | 174, 186 |
| 53 | ID R Kids / Next of Kin | Yes | 175-181 |
| 54 | Living Will / Armed Forces designation | Yes | 182-185 |
| 55 | Moped / motor scooter specs (HP / cc) | Yes | 166, 167, 169 |
| 56 | New Ohio resident 30 days | Yes | 171 |
| 57 | Aggressive driving definition | Yes | 34, 245 |
| 58 | Fatigue effects | Yes | 33, 251 |
| 59 | Hydroplaning | Yes | 109 |
| 60 | Mirror adjustment / blind spot | Yes | 29, 66, 237, 240, 276 |
| 61 | Turn signal 100 ft | Yes | 27, 59, 115 |
| 62 | Funeral processions yield | Yes | 252 |

Coverage rate: 62/62 = 100%.

## Coverage

### Category distribution

| Category | Count | % |
|----------|-------|---|
| safe_driving_rules | 80 | 28.6% |
| license_system | 38 | 13.6% |
| vehicle_information | 28 | 10.0% |
| signs_and_signals | 28 | 10.0% |
| driver_testing | 25 | 8.9% |
| defensive_driving | 22 | 7.9% |
| sharing_the_road | 21 | 7.5% |
| driver_responsibility | 19 | 6.8% |
| penalties_and_points | 13 | 4.6% |
| alcohol_drugs_health | 6 | 2.1% |

Missing categories: none. All 10 canonical categories present.
Over-concentration: none (top category `safe_driving_rules` at 28.6% — well under the 40% threshold).
Low-end note: `alcohol_drugs_health` at 6 questions (2.1%) is lean relative to the manual's substantial Section 3/Section 6 DUI content. Many alcohol/penalty facts are nonetheless covered under `penalties_and_points` (BAC penalties, ALS) and `driver_responsibility` (OVUAC). No grade deduction, but see Recommended Actions.

### Density

| Metric | Value | Notes |
|--------|-------|-------|
| Manual size | 118,788 chars | |
| Total questions | 280 | |
| Density | 2.36 Qs / 1000 chars | Within expected 0.5-3.0 range |
| Sign questions | 11 (3.9%) | Below typical ~10%; standard signs only (stop, yield, wrong-way, no-left, speed-limit, deer, school, RR crossbuck, sharp turn, divided hwy, handicap) |

## Recommended Actions

- **Alcohol/drugs/health depth**: consider adding 4-6 more questions to `alcohol_drugs_health` to bring it closer to the 5-8% band typical of other states. Specifically untested topics in this category: (a) effects of OTC and prescription drugs on driving (Section 6, p.26 "Impairing Drugs"); (b) ALS test-refusal escalation table (1/2/3+ prior refusals -> 2/3/5 yr suspensions, Section 6, p.25); (c) habitual-OVI offender registry (Section 6, p.25, "5 or more OVI in 20 years"); (d) chemical-test window (within 2 hours of arrest).
- **Sign-question depth**: 11 sign questions (3.9%) is below the ~10% norm. Ohio's manual depicts ~20 distinct sign categories (prohibitory, regulatory, warning, guide, route-number, work-zone, plus lane-control). Adding signs for No U-Turn, No Right Turn, No Bicycles, narrow bridge, downhill grade, pedestrian crossing, intersection-ahead, work-zone arrow, and one-way would round this out without changing methodology.
- **Topic gap: hand signals for turns**. The manual (Section 9, p.35) explicitly illustrates left-turn, stop/slow, right-turn arm signals. No question in the bank covers driver hand signals (relevant for bicyclists and for situations when signals fail).
- **Topic gap: ABS braking**. Section 10 mentions ABS explicitly ("ABS stops without skidding"), but no question tests recognition or proper use.
- **Topic gap: 50 mph stopping distance (158 ft)**. Section 8 gives this specific figure for braking distance — useful complement to the truck-stopping figure already tested.
- **Translation hygiene**: `questions_es.yaml` was not audited in this pass; recommend a follow-up review to ensure the Spanish bundle reflects the same precision/recall as English.

No precision or factual corrections required. Quiz is well-grounded, well-balanced, and reflects the current (HSY 7607 10/25) Ohio Digest of Motor Vehicle Laws faithfully.
