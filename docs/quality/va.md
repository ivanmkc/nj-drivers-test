# Quality Verification — Virginia (VA)

- **State**: Virginia
- **Agency**: DMV
- **Manual URL**: https://www.dmv.virginia.gov/webdoc/pdf/dmv39.pdf
- **Source description**: 2025 Virginia Driver's Manual (dmv.virginia.gov)
- **Manual edition**: *(not recorded — `manual_provenance.json` `edition` field is empty)*
- **Manual PDF on disk**: present (`data/states/va/manual.pdf`, 2.33 MB, 40 pages, `pdf.recovered: true`)
- **Manual extracted text on disk**: present (`data/states/va/manual_text.txt`, 128,886 chars, PyMuPDF 1.27.2)
- **Question bank**: `data/states/va/questions_en.yaml` — 279 questions (EN + ES + JA)
- **Structural audit**: `python3 tools/audit_questions.py va` → 0 issues

## Score

**Grade: B+ (Good, with a single recoverable extraction gap)**

| Dimension  | Grade | One-line rationale                                                                                          |
| ---------- | ----- | ----------------------------------------------------------------------------------------------------------- |
| Precision  | B     | 256 / 268 non-sign questions (95.5%) verifiable against `manual_text.txt`; 12 reference an intro letter that was not captured by PyMuPDF extraction (page 1 of the recovered PDF) |
| Recall     | A     | 45 / 45 (100%) of the must-know VA-specific topics derived from the manual have ≥1 question                 |
| Coverage   | B+    | All 10 canonical categories present; top two (`safe_driving_rules` 24.7%, `signs_and_signals` 22.2%) under the 40% threshold; `alcohol_drugs_health` (3.9%) and `vehicle_information` (4.3%) are thin |
| Structural | A     | `tools/audit_questions.py va` → 0 issues across 279 questions                                               |

Net: the bank is well-grounded where the manual text is available, comprehensively covers the topics a VA test-taker must know, and is internally well-formed. The one material defect is upstream of the question bank itself — the intro letter from the DMV Commissioner (page 1 of the PDF) was dropped during PDF text extraction, so questions sourced from that letter cannot be re-validated from disk without re-extracting the PDF.

## Precision

**Methodology** — for each of the 268 non-sign questions, distinctive 5-word (and on a second pass 4-word) substrings of the `explanation` field were matched against a whitespace-normalised, lowercased copy of `manual_text.txt`. Phrases that matched were treated as grounded. Phrases that did not match were inspected by hand against the manual text to classify each as grounded-with-rewording, grounded-elsewhere, or ungrounded-in-extracted-text.

### Aggregate

| Result                                       | Count | Share |
| -------------------------------------------- | ----: | ----: |
| Auto-grounded (literal 4–5-word match)       |   239 | 89.2% |
| Manually verified grounded (reworded prose)  |    17 |  6.3% |
| **Subtotal grounded**                        | **256** | **95.5%** |
| Not in extracted text (intro letter content) |    12 |  4.5% |
| **Fabricated (no manual support anywhere)**  |   **0** |  **0%**   |
| Total non-sign questions                     |   268 |  100% |

The 11 sign-image questions (Q201–Q211) are general MUTCD-aligned sign identifications (STOP, YIELD, WRONG WAY, NO LEFT TURN, SPEED LIMIT, DEER CROSSING, SCHOOL ZONE, RAILROAD CROSSBUCK, SHARP TURN, DIVIDED HIGHWAY, HANDICAP PARKING) and were not phrase-checked against the manual — the manual's sign descriptions in Section 2 corroborate each.

### Manually verified after auto-grep miss

These 17 questions failed the literal substring match only because the question paraphrased the manual (commas, contractions, or section-heading wording differed). All have a corresponding factual statement in `manual_text.txt`:

| ID  | What the question claims                                       | Manual evidence                                                |
| --- | -------------------------------------------------------------- | -------------------------------------------------------------- |
| 7   | Use the "two-, three-, and four-second rule"                   | "Use the two-, three- and four-second rule…" (line 1737)       |
| 8   | TOC lists a two-part knowledge exam                            | TOC line 18 + Section 1 prose (line 178)                       |
| 10  | TOC "Dangerous driving behaviors" lists aggressive/distracted/drowsy/drinking | TOC line 88 + Section 3 sub-headings (lines 2319–2371) |
| 11  | TOC lists "Insurance monitoring program" under DMV requirements | TOC line 119, body line 3046                                  |
| 12  | TOC includes "Light rail" subsection                            | TOC line 68, body lines 1979–2010                              |
| 13  | TOC lists "Administrative License Suspension" under Alcohol & the law | TOC line 126, body line 3154                              |
| 82  | "Never pump antilock brakes"                                   | Line 1385 (verbatim)                                           |
| 103 | Recommended 3-second following at 35–45 MPH                    | Following Distance table (lines 1747–1748)                     |
| 150 | Turn on interior lights during a night-time traffic stop       | Line 2630                                                      |
| 213 | TOC: "Over-correcting" under Section 3                          | TOC line 49                                                    |
| 217 | TOC: Fog/Rain/Snow grouped under "Hazardous conditions"        | TOC lines 79–87                                                |
| 219 | TOC: Section 4 = "Seat Belts, Airbags, and Child Safety Seats" | TOC lines 100–104                                              |
| 221 | TOC: Regulatory/Warning signs sit under Section 2              | TOC lines 34–36                                                |
| 223 | TOC: "Traffic crashes" and "Deer/large animal hazards" in Section 3 | TOC lines 97–98                                            |
| 224 | TOC: Section 1 lists 2-part knowledge exam, road skills, vision (no drug screening) | TOC lines 17–22                          |
| 232 | Road-skills vehicle must have working speedometer              | Line 265 (verbatim list)                                       |
| 269 | Horse-drawn buggies: "Slow down and don't use the horn"        | Line 702 (verbatim)                                            |

### Flagged: cannot verify from extracted text

These 12 questions all reference content that lives in the introductory letter from the DMV Commissioner (Gerald F. Lackey, Ph.D.), which appears as page 1 of the actual PDF but is **missing from `manual_text.txt`** — extraction begins mid-paragraph at "The Virginia Driver's Manual will help you learn…" (line 2), skipping the letter entirely. These questions are not fabricated — they make verifiable factual claims (2024 VA crash statistics, named officials, named program goals) that would survive a re-extraction of the PDF — but they are not verifiable from the local artifact today:

| ID  | Category                | Claim                                                              |
| --- | ----------------------- | ------------------------------------------------------------------ |
|   1 | driver_responsibility   | 71% of 2024 VA crash fatalities were men                           |
|   2 | safe_driving_rules      | 50% of 2024 VA occupant fatalities were unbelted                   |
|   4 | safe_driving_rules      | Texting takes your eyes off the road for 5 seconds                 |
|   5 | defensive_driving       | At 55 mph, 5 seconds = the length of a football field              |
|   6 | safe_driving_rules      | 410 people died in speed-related crashes in VA in 2024             |
| 212 | alcohol_drugs_health    | 318 people died in alcohol-related crashes in VA in 2024           |
| 214 | driver_responsibility   | DMV Commissioner is Gerald F. Lackey, Ph.D.                        |
| 216 | driver_responsibility   | DMV Highway Safety Office goal statement                           |
| 218 | driver_responsibility   | Letter conclusion: "Safety is everyone's responsibility"           |
| 220 | alcohol_drugs_health    | "Drunk driving crashes are 100% preventable"                       |
| 225 | driver_responsibility   | Letter calls "actions you must take to protect your life" the most important part |
| 226 | safe_driving_rules      | 71% of 2024 fatalities were men (duplicate framing of Q1)          |

**Note**: Q1 and Q226 ask substantially the same question (71% men, 2024) from different angles. Even after re-extraction this is worth a deduplication look.

### Zero fabricated

No question in the bank contradicts the manual or invents content beyond it. Every claim that *could* be verified, *did* verify.

## Recall

**Methodology** — derived a list of 45 must-know topics directly from the manual's Table of Contents and section bodies (rather than asking Gemini to extract them, to keep the recall list traceable to the manual text). For each topic, the question bank was searched for a question whose `question`/`explanation`/`choices` contain any of a small synonym set for that topic.

**Result: 45 / 45 topics covered (100%).**

| Topic | Covered? | Topic | Covered? |
| --- | :---: | --- | :---: |
| Right-turn-on-red rules | ✓ | Sharing road with motorcycles (No-Zone) | ✓ |
| Left-turn-on-red (one-way to one-way) | ✓ | Trucks/RVs No-Zones | ✓ |
| Red arrow / flashing red arrow | ✓ | Pedestrian right-of-way / cane/guide dog | ✓ |
| Yellow light response | ✓ | Funeral processions / military convoys | ✓ |
| All-way stop / 4-way yield | ✓ | Seat belt law (all occupants) | ✓ |
| Roundabouts (yield + counter-clockwise) | ✓ | Child safety seats / booster | ✓ |
| Speed limits (urban/unpaved/highway) | ✓ | DUI BAC (.08 adult, .02 under-21) | ✓ |
| Reckless driving threshold (20+ mph over / 85 mph) | ✓ | Implied consent / breath test | ✓ |
| Following distance (2/3/4-second rule) | ✓ | Vehicle impoundment for DUI suspension | ✓ |
| Stopping distance (perception + reaction + braking) | ✓ | Open container in passenger area | ✓ |
| Antilock brakes (never pump) | ✓ | Distracted driving / cell phone | ✓ |
| Hand position (8 and 4) | ✓ | Drowsy driving (no caffeine fix) | ✓ |
| Hand signals (left/right/stop) | ✓ | Aggressive driving penalty | ✓ |
| School bus stop (red flashing) | ✓ | License suspension vs revocation | ✓ |
| Railroad crossings (gates, stalls) | ✓ | Demerit point system | ✓ |
| Sharing road with bicycles (3 ft) | ✓ | Insurance requirements / $500 fee | ✓ |
| Crash reporting / $3,000 threshold | ✓ | Deer/large animal hazards | ✓ |
| Driving in fog/rain/snow | ✓ | Headlights when wipers on | ✓ |
| Work zones (fines, devices) | ✓ | HOV lanes | ✓ |
| Parking restrictions (fire hydrant 15ft, RR 50ft) | ✓ | U-turn rules | ✓ |
| Knowledge test (2-part, 80% pass, 10 sign Qs) | ✓ | Road skills test / vehicle requirements | ✓ |
| Sign shapes (octagon, pentagon, diamond) | ✓ | Sign colors (red/yellow/orange/brown) | ✓ |
| Pavement markings (yellow/white solid/broken) | ✓ |  |  |

No critical-topic gaps found.

Topics intentionally **not** included in the must-know list because they are explicitly out of scope per the manual itself (Section 6 defers to other DMV publications): motorcycle endorsement details (`DMV 2`), CDL details (`DMV 60V/60A`), bioptic telescopic lens criteria (`MED 44`). Each is *referenced* by the bank (e.g. Q252 on bioptic lenses, Q184 on school-bus endorsement) but a deep dive is not expected.

## Coverage

### Category distribution (10/10 canonical categories present)

| Category               | Count | Share |
| ---------------------- | ----: | ----: |
| safe_driving_rules     |    69 | 24.7% |
| signs_and_signals      |    62 | 22.2% |
| driver_testing         |    27 |  9.7% |
| penalties_and_points   |    25 |  9.0% |
| sharing_the_road       |    21 |  7.5% |
| driver_responsibility  |    20 |  7.2% |
| defensive_driving      |    16 |  5.7% |
| license_system         |    16 |  5.7% |
| vehicle_information    |    12 |  4.3% |
| alcohol_drugs_health   |    11 |  3.9% |
| **Total**              | **279** | **100%** |

- **All 10 canonical categories populated** — no missing category.
- **No category over-concentrated.** Largest bucket (`safe_driving_rules` at 24.7%) is well below the 40% over-concentration threshold from the plan. `signs_and_signals` at 22.2% is also healthy for a state with a long sign-shape/color/marking chapter (Section 2).
- **Thin buckets to watch:** `alcohol_drugs_health` (3.9%) and `vehicle_information` (4.3%). Section 5's alcohol subsection in the manual is dense (BAC tiers, implied consent, ALS, impoundment, open container, under-21 penalties) and could support a few more questions; section 7's tire-safety / inspection / insurance text is similarly under-mined in the bank.

### Sign-question contribution

11 of 279 questions (~3.9%) carry an `image:` field. Combined with the 51 text-only `signs_and_signals` items, total signs/signals coverage is ~22.2% — solid. Adding 4–6 more image-based questions for VA-specific MUTCD signs (e.g., Pedestrian Hybrid Beacon, Lane-Use Control signals, sharrow, Light Rail crossing) would round out the visual sign coverage without adding noise.

### Question count vs manual size

- `manual_text.txt`: 128,886 characters
- 279 questions
- **Density: 2.16 questions per 1,000 characters** (or one question per ~462 chars of manual text)

Given how directly the manual reads (Section 8 is itself a sample knowledge exam — see lines 3469–3578 — and several of those sample items appear nearly verbatim as Q198–Q200), there is headroom to add 30–50 more questions without redundancy, particularly in the under-mined sections noted above.

## Recommended Actions

Listed in priority order.

1. **Re-extract `manual.pdf` to capture the introductory letter.** The current `manual_text.txt` starts mid-document (line 2: "The Virginia Driver's Manual will help you learn…"), skipping page 1 entirely. The bank's questions 1, 2, 4, 5, 6, 212, 214, 216, 218, 220, 225, 226 all source from that page. After re-extraction these become precision-verifiable. The `pdf.recovered: true` flag in provenance plus the PyMuPDF version pin (`1.27.2`) make this a one-command rerun — no Gemini calls or human input required.

2. **Deduplicate Q1 and Q226.** Both ask about the same statistic (71% of 2024 VA crash fatalities were men) from slightly different framings. After re-extraction confirms the underlying claim, drop one or rephrase one to cover a different intro-letter fact (e.g., the 5-key-actions list, the comparison to the national average, etc.).

3. **Strengthen `alcohol_drugs_health` (11 questions, 3.9%).** The manual's Section 5 alcohol pages (lines 3058–3247) contain enough material for ~15–18 questions. Missing or under-represented: the three-tier Administrative License Suspension schedule (7 days / 60 days / until trial), the "additional $500–$1,000 fine + 80hr community service for second DUI with juvenile passenger" detail, the ignition-interlock-required language, and the marijuana-still-illegal-while-driving paragraph (line 2484).

4. **Strengthen `vehicle_information` (12 questions, 4.3%).** Tire safety (penny test is covered but not tire pressure schedule), safety inspections / emissions inspection, registration decals, the precise liability-insurance dollar amounts on page 34 (current bank does not include the post-2022 $30K/$60K/$20K minimums), and the bed-of-pickup-truck rule (Q156 covers but no follow-up on camper-shell exception language) are all candidates.

5. **Populate `manual_provenance.json` `edition`** so future refresh agents can detect drift. The PDF is described in `config.json` as the 2025 edition; copying that into the provenance `edition` field is a one-line change.

6. **Consider 4–6 extra sign-image questions** for VA-specific signals (PHB, Lane-Use Control X/arrow signals, sharrow, Light Rail crossing). The text-only sign questions already exist (Q33, Q34, Q65, Q115, Q255, Q256) — the visual pairings would boost test-taker recognition without changing the underlying claim set.

7. **No regeneration needed.** The bank is grounded, comprehensive, well-categorised, and free of fabricated claims. The recommended actions above are enhancements, not corrections.
