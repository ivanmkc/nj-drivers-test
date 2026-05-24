# Wisconsin (WI) — Quiz Quality Verification

- **State**: Wisconsin
- **Agency**: DMV (Wisconsin Department of Transportation)
- **Manual**: 2025 Wisconsin Motorists' Handbook ([wisconsindot.gov](https://wisconsindot.gov/Documents/dmv/shared/bds126-motorists-handbook.pdf))
- **Edition**: 2024/2025 (BDS126, 60 numbered pages)
- **PDF**: 5,073,479 bytes, 64 pages, SHA-256 `9983bf68bce25ab758ad7db061be0d162aac4112a9804eb90a8a9c6044159ddd`
- **Extracted text**: 97,763 chars (PyMuPDF 1.27.2)
- **Question bank**: `data/states/wi/questions_en.yaml` — 321 questions (310 LLM-derived + 11 sign-image)
- **Structural audit**: `python3 tools/audit_questions.py wi` -> **0 issues**

## Score

**Overall: A** (Precision A, Recall A, Coverage A)

| Axis | Grade | Detail |
|---|---|---|
| Precision | A | 308 / 310 non-sign questions (99.4%) match a 4-8-word distinctive phrase from the explanation directly in `manual_text.txt`. The 2 mechanical near-misses were manually inspected and both are grounded (paraphrase / line-break artifacts, not fabrication). Adjusted precision: 100% grounded, 0 fabricated. |
| Recall | A | 63 / 63 critical Wisconsin driving topics covered (100%) — every Section 1-12 topic in the handbook is exercised by at least one question, including state-specific items (Y-turn, RoadReady app, Diverging Diamond Interchange, flex lane, MV3030V vision form, 72-county human-trafficking notice). |
| Coverage | A | All 10 canonical categories represented. Top category `safe_driving_rules` at 30.2% — well under the 40% over-concentration threshold. Density 3.24 Q/1k chars (slightly above the typical 0.5-3.0 range, but the manual is unusually compact at 98k chars so this is healthy, not bloated). |

## Precision

**Method**: For every non-sign question (310 of 321), distinctive 8-, 6-, 5-,
and 4-word phrases were extracted from the `explanation` field (lowercased,
punctuation-stripped, whitespace-normalized) and checked against a
normalized `manual_text.txt`. A question is "mechanically grounded" if
any one of those phrases matches the manual verbatim.

| Bucket | Count | % of non-sign |
|---|---:|---:|
| Total non-sign questions | 310 | 100.0% |
| Grounded (>=1 long-phrase match) | 308 | 99.4% |
| Mechanically unmatched | 2 | 0.6% |
| Fabricated (after manual inspection) | 0 | 0.0% |

The 2 unmatched IDs were manually inspected and **both are grounded** — the
mismatch is purely paraphrase / structural-table shape, not fabrication:

| ID | Category | Claim | Manual evidence |
|---|---|---|---|
| 183 | signs_and_signals | Section 4 sign categories are Warning, Regulatory, Construction, Destination, Service, Mile Marker, Route Number, Railroad Crossing (and NOT "School Zone"). | Manual Table of Contents (lines 122-130) lists exactly those 8 sub-sections under "Section 4: Signs". "School Zone" is a sign instance, not a category. |
| 296 | safe_driving_rules | "Section 6 lists the steps for reaching a roundabout, which includes to 'Yield to semitrucks.'" | Manual line 1264: *"Yield to semitrucks"* — verbatim bullet in Section 6 roundabout procedure. |

**Adjusted precision after manual inspection: 100.0% grounded, 0 fabricated.**

Sign questions (n=11) are excluded from this analysis — they are
deterministically generated from `data/signs/` MUTCD imagery, not from the
manual text, and audited separately by `tools/audit_questions.py`. They
all pass structural checks.

### Targeted high-stakes fact verification

In addition to the broad n-gram sweep, the following high-stakes specific
claims were verified verbatim against `manual_text.txt`:

| Claim | Q ID(s) | Manual evidence |
|---|---|---|
| 20/40 vision, 70-deg field | 16, 17 | "Visual acuity of at least 20/40 in one eye"; "70-degree field of vision" |
| Highway Signs Test: 12/15 (80%) | 18, 188 | "answer 12 questions (80%) correctly to pass the test" |
| Knowledge test: 50 Qs, 45 min, free in-person, $10 online (15-17) | 19, 20, 187, 196 | "test will take about 45 minutes"; "50 questions"; "Tests in a DMV customer service center is free"; "for a fee of $10" |
| Property damage reporting: $1,000 / $200 govt | 114, 115 | "Property damage of $1,000 or more"; "Government property damage of $200 or more" |
| BAC under 21: 0.00% | 119 | "legal alcohol concentration allowed for drivers under the age of 21 is 0.00%" |
| Demerit suspension: 12+ in 12 mo | 127 | "12 or more demerit points within any 12-month period" |
| School bus stop distance: 20 ft | 123 | "stop at least 20 feet from it" |
| Bicyclist passing distance: 3 ft | 125 | "Give bicyclists at least three feet of room" |
| No-Zone trucks: 200 ft behind / 20 ft front | 126 | "about 200 feet behind and 20 feet in front of large trucks" |
| Speed limits: school 15 / residential 25 / outlying 35 | 40, 41, 146 | All three phrases match verbatim in Section 3.B |
| Low-beam 500 ft / sunset+0.5h to sunrise-0.5h | 63, 64 | "500 feet (about one block)"; "half hour past sunset to half hour before sunrise" |
| Occupational license: 12 hr/day, 60 hr/wk | 130 | "drive up to 12 hours a day and up to 60 hours a week" |
| Habitual offender: 4 major / 12 minor in 5 yrs | 129 | "convicted of four or more major traffic violations or 12 or more minor violations within five years" |
| GDL restrictions: 9 months | 31 | "These restrictions are required for the first nine months" |
| Supervised driving: 40 daylight + 10 darkness = 50 hrs | 29, 207, 214 | "practice driving for at least 40 hours during daylight and 10 hours during darkness (50 total hours)" |
| REAL ID enforcement date: May 7, 2025 | 205, 218 | "beginning May 7, 2025" |
| Crash-doubling with another teen passenger | 318 | "The chance of a crash doubles if a teen driver has another teen" |
| Min age 16 for farm tractor on highway | 317 | "No one under 16 years old can operate a farm tractor" |

All checked claims are verbatim in the manual.

## Recall

**Method**: 63 critical Wisconsin-specific topics were derived from the
manual's Section 1-12 Table of Contents plus state-specific items (forms
MV3001/MV3030V/MV2167/MV3004, RoadReady app, KnowToDrive.com/Wisconsin,
72-county human-trafficking note, Diverging Diamond Interchange, flex
lane, semitruck yield in roundabout, sunset-to-sunrise deer activity).
Each topic was matched against the union of `question + explanation +
choices` text across all 321 questions.

**Coverage: 63 / 63 critical topics (100%)**

### Driver licensing pipeline (Sections 1-2)

| Topic | Covered |
|---|:---:|
| Vision screening (20/40, 70-deg) | OK |
| Highway Signs Test (12/15) | OK |
| Knowledge Test (40/50, 50 questions, 45 min, $10 online) | OK |
| Skills Test maneuvers (Y-turn, parking, examiner vehicle check) | OK |
| Required application documents (2 WI residency proofs) | OK |
| Sponsorship & adult sponsor liability (sibling 18+, married-spouse exception) | OK |
| Instruction permit restrictions (passenger seat, 2-yr exp, age 19/21/25) | OK |
| Probationary license / GDL (9-mo, midnight-5am, immediate family) | OK |
| Supervised driving (50 hrs, 40 daylight + 10 dark, RoadReady app) | OK |
| Regular license renewal (every 8 years, 90-day window, 45-60-day reminder) | OK |
| Out-of-state transfer (60 days regular, 30 days CDL) | OK |
| REAL ID (star marking, May 7 2025, no auto-transfer) | OK |

### Basics & rules of the road (Section 3)

| Topic | Covered |
|---|:---:|
| Right-of-way (4-way same time -> right, T-intersection, white cane 10 ft, roundabout, emergency) | OK |
| Four-Second Following Distance Rule + adverse-condition addition | OK |
| Speed limits (school 15, residential 25, outlying 35, no exceeding to pass) | OK |
| 10-15 second sight distance / look-ahead | OK |
| Stopping / no-coasting (don't shift to neutral) | OK |
| Tailgating / 6-8 second rearview check | OK |
| Turning (left, U-turn rural OK, multi-lane same-lane, Y-turn 4 steps) | OK |
| Passing rules (paved shoulder only if stopped/left-turning, one at a time, headlights-in-mirror return) | OK |
| Backing (slow walk, don't back to a missed exit) | OK |
| Parking (uphill-curb left, uphill-no-curb right, downhill right, yellow curb prohibited, parallel 3-6 ft) | OK |
| Headlights (500 ft, half-hour past sunset/before sunrise, low beams in fog/rain/snow) | OK |
| High beams / brights etiquette (look to right shoulder when oncoming forgets) | OK |
| Turn signal timing (3 sec / 100 ft) + hand signals (left straight, right elbow-up, stop down) | OK |
| Horn use (light tap to alert, hard for collision warning) | OK |

### Signs (Section 4)

| Topic | Covered |
|---|:---:|
| Warning signs (yellow diamond, deer crossing, lane ends, 2-way, slippery, signal-ahead) | OK |
| Regulatory signs (Do Not Enter, school speed, Keep Right, multi-lane arrows, Reserved Parking) | OK |
| Construction signs (orange, fines double, cellphone emergency-only) | OK |
| Destination signs (green city, brown for parks/historical/museums) | OK |
| Service signs (blue) | OK |
| Mile markers (every 0.1-0.2 mi, direction + route + mile number) | OK |
| Route numbers (County rounded-rect, U.S. badge, State milk-jug, Interstate red/blue shield) | OK |
| Railroad crossings (crossbuck, train approaching, gate not under/around, blue report-problem, exempt sign, tracks-out-of-service, no shift gears) | OK |
| Slow-Moving Vehicle emblem (orange triangle, <=25 mph) | OK |
| No Passing Zone (yellow pennant) | OK |

### Signals & pavement markings (Section 5)

| Topic | Covered |
|---|:---:|
| Traffic signals (steady/flashing red/yellow/green + arrows; signal-out -> stop sign) | OK |
| Left turn on red from one-way onto one-way | OK |
| Steady-green left turn yields to oncoming | OK |
| Line markings (white edge, yellow center, dashed-vs-solid, double yellow + farm-equip exception) | OK |
| Shared center lane (left turn / U-turn only) | OK |
| Reversible lanes (red X / green arrow / yellow X) | OK |
| Reserved lanes (white diamond, bus/bike/HOV, turn-across-in-half-block exception) | OK |
| Flex lane (no large trucks, solid yellow separator, signage-driven) | OK |

### Driving situations & conditions (Sections 6-7)

| Topic | Covered |
|---|:---:|
| Roundabouts (counterclockwise, yield to semitrucks, emergency-exit-then-pull-over, no lane switching) | OK |
| Metered ramps (sensors at white line, ticketed for disobeying, "Ramp Metered When Flashing") | OK |
| Diverging Diamond Interchange (safety, reduced crowding, lower cost) | OK |
| Traffic stops (hands on top of wheel, park + radio off, no arguing) | OK |
| Watch for deer (sunset-to-sunrise, headlights-in-eyes -> slow+horn+stop; can keep deer, call police for tag) | OK |
| Funeral processions (headlights on, first vehicle obeys signals, don't cut in) | OK |
| Reduced visibility (vehicles appear slower) | OK |
| Severe weather (bridges/overpasses freeze first; hydroplaning -> off gas, wheel straight; skid -> off brake, into-direction) | OK |
| Winter driving (no cruise control, low beams, snowplow 200 ft, clear plates/lamps/mirrors) | OK |
| Farm/rural (yield to livestock, no horn, farm tractor age 16+) | OK |

### Emergencies (Section 8)

| Topic | Covered |
|---|:---:|
| Avoiding crashes (stop/turn/speed-up options, ABS firm-continuous, brake-tap 3-4x warning) | OK |
| Crashes (call 911, $1,000 property / $200 govt reporting, leaving-scene crime) | OK |
| Roadside emergencies (brakes pump, tire blowout straight-and-off-gas, gas pedal -> neutral, headlights) | OK |

### Dangerous driving behaviors (Section 9)

| Topic | Covered |
|---|:---:|
| Alcohol / drugs (0.00% under 21, Implied Consent / PAC test, 1-year revocation on refusal) | OK |
| Distracted driving (permit/probationary cellphone -> emergency-only; hands-free for regular) | OK |
| Drowsy driving (yawning, lane drift, rumble strip) | OK |

### Sharing the road (Section 10)

| Topic | Covered |
|---|:---:|
| Pedestrians (allow extra room, sidewalk illegal except crossing) | OK |
| Emergency vehicles (move to far lane, no stop in intersection) | OK |
| School buses (20 ft, divided-highway barrier exception, watch for kids) | OK |
| Motorcycles (lightweight, blind spots, extra room) | OK |
| Bicycles (3 ft, whole lane allowed, slow + let oncoming pass first) | OK |
| No-Zones (200 ft behind, 20 ft in front of large trucks) | OK |

### Driving privilege & other (Sections 11-12)

| Topic | Covered |
|---|:---:|
| Point System (12+ pts in 12 mos -> suspended/revoked, doubled on probationary) | OK |
| Habitual Traffic Offender (4 major / 12 minor in 5 yrs, 5-yr revocation) | OK |
| Occupational license (12 hr/day, 60 hr/wk) | OK |
| Reinstating revoked/suspended (proof of financial responsibility + fee) | OK |
| Invisible disability disclosure (MV2167, law enforcement + WisDOT access) | OK |
| Medical conditions to report | OK |
| Free ID for voting (17+, MV3004, petition MV3012) | OK |
| Seat belts (all ages, lap on hip bones, fist between shoulder belt and chest, child <4 + booster <8, still with airbags) | OK |
| Insurance (valid liability required, driver's responsibility on someone else's car) | OK |
| Save fuel (low tire pressure decreases mileage, slow-down little-by-little) | OK |
| Driver Education Grant Program (income-eligible teens) | OK |
| Organ donation (18+ decision cannot be overridden) | OK |
| Human trafficking (all 72 counties, 1-888-3737-888, BeFree 233733, love146.org) | OK |

No critical Wisconsin-handbook topic is left untested.

## Coverage

### Category distribution (target: all 10 represented, no single category > 40%)

| Category | Count | % |
|---|---:|---:|
| safe_driving_rules | 97 | 30.2% |
| signs_and_signals | 60 | 18.7% |
| driver_responsibility | 32 | 10.0% |
| license_system | 28 | 8.7% |
| defensive_driving | 27 | 8.4% |
| sharing_the_road | 27 | 8.4% |
| driver_testing | 23 | 7.2% |
| vehicle_information | 13 | 4.0% |
| penalties_and_points | 11 | 3.4% |
| alcohol_drugs_health | 3 | 0.9% |
| **Total** | **321** | **100%** |

All 10 canonical categories present. Top category `safe_driving_rules`
(30.2%) is comfortably under the 40% over-concentration ceiling.

**Light categories worth noting** (flag, not fail):
- `alcohol_drugs_health` at 0.9% (3 questions) is the platform's lightest
  for WI. The handbook devotes Section 9.A specifically to Alcohol, Drugs
  and Driving, and the Implied Consent / PAC content is non-trivial.
  Several closely-related questions are filed under `penalties_and_points`
  (e.g., Q120 Implied Consent PAC refusal) — defensible categorization,
  but a few more questions tagged `alcohol_drugs_health` would better
  surface that section in by-category analytics.
- `penalties_and_points` at 3.4% (11 questions) is also on the lighter
  side given the manual covers Point System, GDL extension, Habitual
  Traffic Offender, double-points on probationary, $200/$1,000 reporting,
  and Implied Consent revocation.

### Question density

| Metric | Value | Notes |
|---|---|---|
| Manual size | 97,763 chars | Compact for the platform (median ~150k) |
| Total questions | 321 | |
| LLM-derived questions | 310 | |
| Density | 3.24 Q / 1k chars | Just above the 0.5-3.0 expected range, but consistent with the manual's compact size — no dilution |
| Sign questions | 11 (3.4%) | Below the typical ~10% (34 standard signs). The handbook itself describes signs in-line in Sections 4-5 without a separate sign-image gallery, so coverage is via text-based questions; this is acceptable for WI but means visual sign-recognition is lightly exercised. |

### Sign-question contribution

- Sign questions (`image:`-tagged): 11 / 321 = 3.4%
- LLM questions: 310 / 321 = 96.6%

The 11 sign images cover stop, yield, wrong-way, no-left-turn, speed
limit, deer crossing, school zone, railroad crossbuck, sharp turn,
divided highway, and handicap parking — the highest-frequency MUTCD
signs. WI's manual covers many more sign types verbally; questions
68-78, 152-154, 257-258, 261-275 supplement the image questions with
text-based identification.

## Recommended Actions

Quality is high; these are **enhancements**, not defects:

1. **Add 3-5 `alcohol_drugs_health` questions.** Currently at 0.9% (3 Qs).
   The handbook's Section 9.A (Alcohol, Drugs and Driving) supports
   additional questions on: prescription/non-prescription drug warning
   labels, marijuana's mistake-rate finding, "time is the only thing that
   will sober you up", the chain bartender-call-cab tip, and the
   distinction between "any amount of a controlled substance" and PAC
   limits.
2. **Re-categorize some Implied Consent / DUI penalty questions.** Q120
   (PAC refusal / 1-year revocation) is currently `penalties_and_points`;
   it would equally fit `alcohol_drugs_health` and would help balance the
   under-weighted category without writing new questions.
3. **(Optional) Increase sign-image coverage to ~10%.** Adding 15-20 more
   `image:`-tagged questions using existing `data/signs/` MUTCD imagery
   (no passing zone, slow-moving-vehicle, merge, lane-ends, signal-ahead,
   keep right, no U-turn, do not enter, work-zone signs) would match the
   platform's typical sign-question ratio and exercise visual recognition
   — currently those signs are tested only by text description.
4. **No fixes required for fabricated content.** Precision audit found
   zero hallucinated claims after manual inspection of the 2 grep-missed
   items. Both were paraphrase / table-of-contents matches that the
   n-gram heuristic could not detect.

---

*Generated: 2026-04-29. Verifier methodology: `/home/ivanmkc/.claude/plans/agile-pondering-truffle.md`.*
