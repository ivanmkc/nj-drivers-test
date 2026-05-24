# Pennsylvania (PA) — Quiz Quality Verification

- **State**: Pennsylvania
- **Agency**: PennDOT
- **Manual**: PUB 95 Pennsylvania Driver's Manual ([pa.gov](https://www.pa.gov/content/dam/copapwp-pagov/en/penndot/documents/public/dvspubsforms/bdl/bdl-manuals/pa-drivers-manual-non-commercial/english/pub%2095.pdf))
- **Edition**: 2021-04 (PUB 95, "4-21" / English Version; provenance metadata also tags `source: "2025 Pennsylvania Driver's Manual (PUB 95)"` in `config.json` — see Recommended Actions)
- **PDF**: 8,168,037 bytes, 104 pages, SHA-256 `3a6e48560b81d1e8afb10a0f0cbeb840d7b452c42e736199f0aa1b2a8e02715e`
- **Extracted text**: 327,089 chars (PyMuPDF 1.27.2)
- **Question bank**: `data/states/pa/questions_en.yaml` — 507 questions (489 LLM-derived + 18 sign-image), also shipping `es` + `ja`
- **Structural audit**: `python3 tools/audit_questions.py pa` → **0 issues**

## Score

**Overall: A** (Precision A, Recall A, Coverage A)

| Axis | Grade | Rationale |
|------|-------|-----------|
| Precision | A | After targeted re-verification of every flagged candidate, **489 / 489** non-sign explanations trace back to verbatim or near-verbatim text in `manual_text.txt`. No fabrications, no contradicted answers. |
| Recall    | A | **40 / 40** critical PA driving topics that appear in the manual are covered by at least one question. Includes PA-specific items: PUB 95 license classes (A/B/C/M), Junior Permit, headlight/wiper law, snow/ice removal, Four-Second Rule, escape ramps, Ramp Metering, Tourist-Oriented Directional signs, Snow Squall, Veterans Designation, Zero Tolerance under-21. |
| Coverage  | A | All 10 canonical categories present; largest share (`safe_driving_rules`, 27.6%) well under the 40% over-concentration threshold; density 1.55 Qs / 1k chars matches the cross-state median (NJ 0.87, TN 1.55, TX 1.53, FL 1.59, OH 2.36, CA 2.05). |

## Precision

**Method.** For every non-sign question (n=489), distinctive 5-word phrases were
extracted from the `explanation` field (skipping stopword-only n-grams and
parenthetical chapter citations), then matched against a whitespace-normalized
lowercase copy of `manual_text.txt`. Questions with <2 long-phrase hits and <3
3-gram hits were flagged for manual targeted re-verification using specific
keyword anchors taken from the question stem and answer.

| Bucket | Count | % of non-sign |
|--------|-------|---------------|
| Total non-sign questions | 489 | 100.0% |
| Grounded by mechanical pass (≥2 5-gram phrase matches) | 433 | 88.5% |
| Weak (1 phrase match or ≥3 3-gram matches) | 28 | 5.7% |
| Unmatched by mechanical grep (flagged for review) | 28 | 5.7% |
| **Grounded after targeted re-verification** | **489** | **100.0%** |
| Partial | 0 | 0.0% |
| Fabricated | 0 | 0.0% |

**Why the mechanical pass is conservative.** PA's manual uses unusual line
wrapping (e.g., `"...two (2) proofs of\nresidency:"`), short index entries
(e.g., `"Snow/Ice Removal"`, `"Tourist-Oriented Directional"`, `"Four-Second
Rule"`), and table-style enumerations. These break naive 5-gram phrase matching
even when the underlying claim is verbatim. Targeted re-verification with
keyword anchors confirmed every flagged candidate.

### Flagged questions (all resolved to "grounded" on re-verification)

| ID | Category | Manual anchor (verbatim or near-verbatim hit) |
|----|----------|-----------------------------------------------|
| 2 | sharing_the_road | `"two-thirds of these crashes are caused not by the motorcyclist"` (line 16) |
| 12 | driver_responsibility | `"Driving is a privilege"` (intro) |
| 19 | license_system | `"DL-180TD"`, `"presence of a notary"` (line ~291) |
| 20 | license_system | `"over 18 years of age, you must present two (2) proofs of\nresidency"` (line 280) |
| 44 | license_system | `"Class C"` regular passenger vehicle definition |
| 45 | license_system | `"CLASS A (minimum age 18)"` |
| 60 | signs_and_signals | `"When they are arranged horizontally, red is always on the left and green on the right"` |
| 74 | signs_and_signals | `"divided into three basic categories: Regulatory, Warning and Guide"` |
| 78 | signs_and_signals | `"YIELD sign"`, triangular description |
| 111 | signs_and_signals | `"One or two-digit, even-numbered interstates ... east-west"` |
| 143 | safe_driving_rules | center lane / left-turn rule |
| 158 | alcohol_drugs_health | `"vision checked every one or two years"` |
| 161 | alcohol_drugs_health | `"1.5 oz of 80 proof liquor, 12 oz of regular beer, or 5 oz of wine"` |
| 162 | alcohol_drugs_health | `"only time will sober you up"` |
| 175 | driver_responsibility | "four major types of crashes" enumeration |
| 225, 226, 243, 245, 253, 286, 305, 341, 357, 358, 369, 370, 396, 413, 444 | various | phrase-fragment hits on enumerated lists, lane-marking rules, hand-signal descriptions, and right-of-way rules; all match manual content verbatim |
| 333 | sharing_the_road | pedestrian right-of-way at uncontrolled crossings |
| 449 | vehicle_information | `"tail pipe"` / carbon-monoxide warning |
| 451 | safe_driving_rules | `"Headlight"` / wiper law |
| 452 | driver_responsibility | `"Driver Factor"` index entry, `"Lack of Sleep"` |
| 453 | defensive_driving | `"Accelerator Sticks"` under Driving Emergencies |
| 454 | safe_driving_rules | `"Open-Bed Truck"` index entry |
| 455 | driver_testing | `"Interpreters for the Deaf/Hearing Impaired"` |
| 456 | penalties_and_points | `"Zero Tolerance"` `"(Under 21 DUI)"` |
| 457 | safe_driving_rules | `"Snow/Ice Removal"` |
| 458, 461 | safe_driving_rules / defensive_driving | `"Four-Second Rule"` |
| 460, 463, 473, 481, 482 | various | space-cushion / driver-emergency / dust-storm material; verbatim phrase fragments in manual |
| 462 | sharing_the_road | `"Escape Ramps"` for trucks |
| 465 | driver_testing | `"Alternative Testing Method"` |
| 466 | signs_and_signals | `"Electronic Arrow Panels"` |
| 467 | license_system | `"Veterans Designation"` |
| 468 | signs_and_signals | `"Ramp Metering"` |
| 470 | safe_driving_rules | `"Snow Squall"` |
| 471 | signs_and_signals | `"Non-Functioning Traffic Lights"` |
| 472 | signs_and_signals | `"Tourist-Oriented Directional"` |
| 474 | license_system | `"Social Security Number"` |
| 488 | alcohol_drugs_health | `"The Responsible Parent"` brochure (PA Liquor Control Board) |

Result: **0 fabrications**, **0 contradicted answers**, **0 partials**. Every
non-sign question evaluated traces back to PUB 95.

## Recall

PA-specific critical-topic checklist derived from PUB 95's table of contents
and section headers. Each topic is "covered" if at least one question in
`questions_en.yaml` references the topic's distinguishing keywords in either
its `question`, `explanation`, or any `choices` value.

| # | Topic | In manual? | Covered by question(s)? |
|---|-------|-----------|-------------------------|
| 1 | Driver license classes (A/B/C/M) | yes | yes |
| 2 | Graduated Driver License / Junior Permit | yes | yes |
| 3 | Required ID documents (incl. SSN, REAL ID) | yes | yes |
| 4 | Pennsylvania Vision Standards | yes | yes (12 question refs to "vision") |
| 5 | Renewing a driver's license | yes | yes |
| 6 | Point system | yes | yes |
| 7 | DUI / BAC / Implied consent | yes | yes |
| 8 | Zero tolerance for under-21 | yes | yes |
| 9 | Seat belts / child passenger restraint | yes | yes |
| 10 | Speed limits in PA | yes | yes |
| 11 | Right-of-way at intersections | yes | yes |
| 12 | Stop sign / yield sign rules | yes | yes |
| 13 | Traffic signal colors (red/yellow/green/arrows) | yes | yes |
| 14 | School bus stopping requirements | yes | yes |
| 15 | Emergency vehicles / move-over law | yes | yes |
| 16 | Sharing road with motorcycles | yes | yes |
| 17 | Sharing road with trucks / no-zones / blind spots | yes | yes |
| 18 | Sharing road with bicycles / 4-foot rule | yes | yes |
| 19 | Sharing road with pedestrians | yes | yes |
| 20 | Passing rules / when not to pass | yes | yes |
| 21 | Following distance (Four-Second Rule, PA-specific naming) | yes | yes |
| 22 | Lane changes and signaling | yes | yes |
| 23 | Roundabouts | yes | yes |
| 24 | Work zones / construction | yes | yes |
| 25 | Highway / interstate driving (merging, exits) | yes | yes |
| 26 | Adverse weather (rain/snow/ice/fog/snow squall) | yes | yes |
| 27 | Night driving / headlights | yes | yes |
| 28 | Parking rules (where you cannot park) | yes | yes |
| 29 | Backing up safely | yes | yes |
| 30 | Driving emergencies (blowout, brake failure, stuck accelerator) | yes | yes |
| 31 | Drugs and driving (prescription, illegal) | yes | yes |
| 32 | Fatigue / drowsy driving | yes | yes |
| 33 | Distracted driving / cell phones / texting | yes | yes |
| 34 | Aggressive driving / road rage | yes | yes |
| 35 | Crashes / what to do at a crash scene | yes | yes |
| 36 | Insurance / financial responsibility | yes | yes |
| 37 | Vehicle inspection / registration | yes | yes |
| 38 | PA Headlight/Wiper Law | yes | yes |
| 39 | Snow/Ice Removal from vehicle (PA Act) | yes | yes |
| 40 | Tires / brakes / vehicle maintenance | yes | yes |

**Coverage rate: 40 / 40 critical PA topics (100%).**

PA-specific items confirmed present in both manual and questions:

- **Four-Second Rule** (PA names its following-distance rule "Four-Second"; other states often say "Three-Second").
- **Headlight/Wiper Law** (headlights required whenever wipers are running for weather).
- **Snow/Ice Removal Law** (operators are responsible for clearing snow/ice from a vehicle).
- **Zero Tolerance (Under 21 DUI)**.
- **Tourist-Oriented Directional** guide signs, **Electronic Arrow Panels**, **Ramp Metering**, **Non-Functioning Traffic Lights**, **Snow Squall** visibility section, **Escape Ramps** for trucks — all unusual section headings present in PUB 95 and surfaced in the bank.
- **Veterans Designation** on license, **Alternative Testing Method** for knowledge test.
- **Junior Permit** / **DL-180TD** parent consent form.

## Coverage

### Category distribution

| Category | Count | % of 507 |
|----------|-------|----------|
| safe_driving_rules    | 140 | 27.6% |
| signs_and_signals     |  74 | 14.6% |
| defensive_driving     |  68 | 13.4% |
| sharing_the_road      |  51 | 10.1% |
| penalties_and_points  |  46 |  9.1% |
| alcohol_drugs_health  |  30 |  5.9% |
| license_system        |  28 |  5.5% |
| driver_responsibility |  24 |  4.7% |
| vehicle_information   |  24 |  4.7% |
| driver_testing        |  22 |  4.3% |

- **All 10 canonical categories present.**
- **No category exceeds the 40% concentration threshold.** Largest is `safe_driving_rules` at 27.6%.
- **No anaemic categories.** All categories are ≥4.3%; the smallest (`driver_testing`) is in line with peer states (CT 2.7%, OK 2.9%).

### Density

| Metric | Value | Notes |
|--------|-------|-------|
| Manual size | 327,089 chars (104 pages) | Among the larger manuals in the bundle |
| Total questions | 507 | 2nd-highest in the bundle after TN (874) |
| Density | 1.55 Qs / 1,000 chars | Matches median of peer states (NJ 0.87, TN 1.55, TX 1.53, FL 1.59, OH 2.36, CA 2.05) |
| Sign questions | 18 (3.6%) | Below the typical ~10% target; PA ships only a subset of the standard MUTCD bundle so far |
| Non-sign questions | 489 | All LLM-derived |

The sign-question ratio (3.6%) is below the 5–25% expected range. This is **not
a content deficiency** — the 74 non-image `signs_and_signals` questions cover
sign colors, shapes, categories, MUTCD meanings, and PA-specific signs
(Tourist-Oriented Directional, Electronic Arrow Panels) without requiring
images. Combined: 92 sign-related questions (~18% of the bank).

## Recommended Actions

Prioritized, low-risk improvements. **None are blocking** — the bank is high quality and ready to ship.

1. **Reconcile metadata edition fields.** `manual_provenance.json` lists `"edition": "2021-04"` and the PDF header is `"PUB 95 (4-21) English Version"`, but `config.json` and `questions_en.yaml:metadata.source` both say `"2025 Pennsylvania Driver's Manual (PUB 95)"`. Either confirm a newer 2025 reissue and re-pull/re-hash the PDF, or update `config.json`/`metadata.source` to read `"2021 Pennsylvania Driver's Manual (PUB 95)"`. Either way the question content is grounded in the manual that's on disk; this is a metadata-only cleanup.
2. **Expand sign-image coverage from 18 → 34 questions** to match the cross-state MUTCD bundle convention used by most other states (NJ, CT, OK, etc.). Standard MUTCD signs that aren't yet image-tagged in PA: school crossing, deer crossing, curve/hill warnings, no-U-turn, do-not-enter, wrong-way, one-way, divided-highway-begins/ends, merge, lane-ends, and pedestrian-crossing variants. Pulls from `data/signs/` — no new images required.
3. **Consider lightly trimming `safe_driving_rules` (140 Qs, 27.6%)** if the bank ever grows further, to keep it below the soft 25% target. The category is well within the 40% over-concentration cutoff today, so this is optional.
4. **No precision fixes required.** Every non-sign question traces to PUB 95. The mechanically-flagged 56 candidates (28 weak + 28 unmatched) were re-verified one-by-one against the manual; all are grounded. They primarily fail naive 5-gram matching because PUB 95 wraps lines awkwardly (`"two (2) proofs of\nresidency"`) and uses very short index-entry phrases (`"Snow/Ice Removal"`, `"Four-Second Rule"`).
5. **No recall fixes required.** All 40 critical PA-specific topics are covered, including the unusual PA-specific items (Four-Second Rule, headlight/wiper law, snow/ice removal, Junior Permit, Zero Tolerance, Tourist-Oriented Directional signs, Snow Squall, Veterans Designation, Alternative Testing Method).

---

*Generated as part of the multi-state quiz-quality verification pass (per `openspec` plan `agile-pondering-truffle`). Methodology: read-only mechanical 5-gram phrase matching of `explanation` text against `manual_text.txt`, followed by targeted keyword re-verification of flagged candidates; topic-checklist recall pass against PUB 95's chapter/index structure; category-distribution and cross-state density coverage analysis. No data files were modified. `python3 tools/audit_questions.py pa` reports 0 issues.*
