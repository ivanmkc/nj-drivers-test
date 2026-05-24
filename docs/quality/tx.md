# Texas (TX) — Quiz Quality Verification

- **State**: Texas (DPS)
- **Manual edition**: 2025 Texas Driver Handbook (DL-7)
- **Manual URL**: https://www.dps.texas.gov/internetforms/Forms/DL-7.pdf
- **Manual size**: 272,296 chars (91 pages, sha256 `5239ff7c…e21e8a6d`)
- **Question bank**: 417 questions (399 text + 18 sign/image), EN/ES/JA
- **Density**: 15.3 questions per 10k chars of manual (healthy)
- **Audit status**: `tools/audit_questions.py tx` → 0 issues

## Score

| Axis | Grade | Value |
|---|---|---|
| Precision | A | 97.7% grounded (bigram phrase match) + 100% on hand-sampled controls |
| Recall | B+ | 23 / 25 critical topics covered; 2 thin (expressway driving mechanics, in-car emergencies) |
| Coverage | A− | 10 / 10 canonical categories present; no category >21%; one underweight (`driver_testing` 2.4%) |
| **Overall** | **A−** | Strong factual grounding; minor topical gaps |

## Precision

Methodology: for each non-sign question, computed the share of distinctive bigram keywords from the question + answer + explanation that appear verbatim in `manual_text.txt`. Bigrams that match → grounded; ≥10% but <25% → partial; <10% → flagged. A hand-sample of 24 questions (20 random + 4 flagged) was then verified against direct manual excerpts.

| Bucket | Count | % of 399 non-sign |
|---|---|---|
| Grounded (≥25% bigram match) | 390 | 97.7% |
| Partial (10–25% bigram match) | 5 | 1.3% |
| Flagged (<10% bigram match) | 4 | 1.0% |
| **Fabricated (after manual review)** | **0** | **0.0%** |

### Flagged IDs investigated (all confirmed grounded)

| ID | Category | Claim | Manual line |
|---|---|---|---|
| 128 | vehicle_information | Two red reflectors at 15–60 inches | line 1008 ("Two red reflectors … must be placed at a height of 15 to 60 inches") |
| 220 | safe_driving_rules | Illegal to coast on a downgrade in neutral | covered in Ch. 9 (transmission-in-neutral coasting prohibition) |
| 224 | defensive_driving | Field of vision at 60 mph reduced to ~1/5 | lines 2320–2330 ("60 MPH — Field of vision reduced to about 1/5") |
| 293 | sharing_the_road | Pedestrian crossing outside crosswalk must yield | covered in pedestrian-rights subsection |

### Spot-checked hand sample (20 random + 4 flagged Qs, all grounded)

Verified e.g. Q5 ("314,000 miles" → manual line 52), Q53 (85-year licensing rule → line 335), Q92 ($125 ALR reinstatement → line 842), Q112 ($10/year or $20/2-year occupational license fee → line 965), Q118 (200-ft horn audibility → line 1015), Q120 (25 mph slow-moving-vehicle emblem trigger), Q126 (60-day buyer's temp tag → line 1092), Q134/135 ($25,000 property / $30,000 single-injury liability → lines 1140–1142), Q195 (100-ft turn signal → line 2060), Q280 (intoxication manslaughter = second-degree felony → line 3231), Q347 (highway hypnosis definition → line 3796).

No factual contradictions found.

## Recall

Methodology: identified 25 critical topics for a Texas written test from the manual's table of contents (chapters 1–14 + appendices). For each, searched the question bank for relevant keywords/phrases.

| # | Topic | Qs | Status |
|---|---|---|---|
| 1 | License system / classes (A/B/C/M) | 76 | strong |
| 2 | Graduated / provisional / learner license | 28 | strong |
| 3 | Driver testing process | 10 | thin but adequate |
| 4 | **Financial responsibility & liability insurance** | 18 | strong (covers $30k/$60k/$25k, SR-22, acceptable evidence forms) |
| 5 | Speed limits (urban, highway, school, alley) | 44 | strong |
| 6 | **Expressway / freeway driving mechanics** (entering, lane choice, exiting) | 1 | **gap** — only Q185 (ramp meter); manual Ch. 9 section "Highway Driving" untapped |
| 7 | Right-of-way rules | 33 | strong |
| 8 | Following / stopping distance (2-sec rule) | 8 | adequate |
| 9 | DWI / BAC / open container / implied consent | 36 | strong |
| 10 | Turn signaling (100-ft rule) | 43 | strong |
| 11 | Parking rules & restrictions | 30 | strong |
| 12 | Sharing road: motorcycles, bicycles, pedestrians | 60 | strong |
| 13 | School zones, school buses, school crossings | 15 | adequate (manual is itself silent on a numeric school-zone mph) |
| 14 | Work / construction zones | 5 | thin |
| 15 | Railroad crossings + ENS | 44 | strong |
| 16 | Crash / accident reporting (CR-2/CR-3) | 39 | strong |
| 17 | Seat belts / child restraints | 4 | thin (manual coverage is also brief) |
| 18 | Headlights / high-low beams | 13 | adequate |
| 19 | Cell phone / texting restrictions | 12 | adequate |
| 20 | Sign shapes / colors | 7 | adequate (plus 18 sign-image Qs in `signs_and_signals`) |
| 21 | Pavement markings (yellow/white lines) | 6 | adequate |
| 22 | Wet / slippery / hydroplaning | 5 | thin |
| 23 | Night driving | 12 | adequate |
| 24 | **In-car driving emergencies** (skid recovery, blowout, brake failure) | 1 | **gap** — only Q82 on quick-stop exam; manual lines 2479–2509 (steering out of a skid, blowout, brake failure) almost entirely uncovered |
| 25 | License suspension / revocation / ALR | 22 | strong |

**Coverage rate**: 23 / 25 topics have ≥3 questions = **92%**. Two clear gaps:
- Expressway driving mechanics (enter / lane discipline / exit)
- Emergency vehicle handling (skid, blowout, brake failure)

## Coverage

### Category distribution (10 of 10 canonical categories present)

| Category | Count | % |
|---|---|---|
| safe_driving_rules | 87 | 20.9% |
| license_system | 76 | 18.2% |
| signs_and_signals | 49 | 11.8% |
| penalties_and_points | 44 | 10.6% |
| vehicle_information | 36 | 8.6% |
| sharing_the_road | 35 | 8.4% |
| driver_responsibility | 29 | 7.0% |
| defensive_driving | 27 | 6.5% |
| alcohol_drugs_health | 24 | 5.8% |
| driver_testing | 10 | 2.4% |

- **No over-concentration**: max category share is 20.9% (well under the 40% threshold).
- **Underweight**: `driver_testing` at 2.4% — defensible because the manual's "exam" content is procedural; still, a couple more on the driving-skills test rubric (parallel parking, quick stop, 3-point turn) would round it out.
- **Sign-image contribution**: 18 / 49 of `signs_and_signals` questions (37%) ship with `image:` tags — good MUTCD visual coverage.

### Question-count vs. manual-size

- 417 questions / 272,296 chars ≈ **15.3 Qs per 10k chars** — comfortably within the project's healthy band (10–20).
- No bloat or thinning; ratio aligns with peer states (NJ 307/~180k, IL 413/~310k).

## Recommended Actions

1. **Add 4–6 questions on Texas expressway / freeway driving** (manual Ch. 9 lines 2417–2440 — "Highway Driving" section). Suggested topics:
   - Right-of-way: vehicles already on the highway have it (entering driver yields)
   - Lane discipline: right lane for minimum-speed traffic, middle/left for passing
   - 2-second following rule (4 in bad weather) when on freeway
   - Exit-lane selection in advance
2. **Add 3–4 questions on driving emergencies** (manual Ch. 9 lines 2479–2509):
   - Steering out of a skid — turn wheel *in the direction* of the skid
   - Flat tire / blowout — do not slam brakes; ease off accelerator, steer straight
   - Brake failure — pump cautiously to avoid locking + skid
3. **(Optional, low-priority)** Boost `driver_testing` from 10 to ~15 questions with content from the road-test rubric: parallel parking spec, quick-stop spec, mirror/blind-spot check, signaling during exam.
4. **(Optional)** Add 2–3 questions on hydroplaning / wet-road handling — manual covers this in safe-driving but only 5 questions touch it.

**No precision fixes needed.** No fabricated content, incorrect numbers, or contradictions with the manual were found. Texas quiz quality is solid; the recommendations above are additive, not corrective.
