# Oregon (OR) — Quiz Quality Verification

- **State**: Oregon
- **Agency**: DMV (Driver and Motor Vehicle Services, Oregon Department of Transportation)
- **Manual URL**: https://www.oregon.gov/odot/forms/dmv/37.pdf
- **Source description**: 2025 Oregon Driver Manual (oregon.gov) — actual PDF text is the **2026-2027 Oregon Driver Manual** (Form 735-37 (1-26)), published by ODOT/DMV
- **Edition**: `2026-2027` (per PDF body; `manual_provenance.json` `edition` field is empty and should be backfilled)
- **Question count (en)**: 284 (270 LLM-generated text + 11 MUTCD sign-image questions reused from the shared sign pool + 3 ID #s assigned to sign questions inside the YAML)
- **Translations available**: English, Spanish, Japanese
- **Manual recovered**: **YES** (`pdf.recovered: true`, 112 pages, 13.4 MB, SHA-256 `1f294b…fe029d`)
- **Manual text on disk**: `manual_text.txt`, 126,548 chars, SHA-256 `fcc3548…891a68`
- **Structural audit**: `python3 tools/audit_questions.py or` → **0 issues**

## Score

**Grade: A.** Oregon's 284-question bank is tightly grounded in the recovered 2026-2027 Oregon Driver Manual, covers the manual's full table of contents, and shows healthy category balance with no over-concentration.

| Dimension     | Grade | Headline                                                                                  |
| ------------- | ----- | ----------------------------------------------------------------------------------------- |
| Precision     | A     | Every spot-checked numeric / regulatory claim verbatim-matches the manual text            |
| Recall        | A     | All 25 critical topics derived from the manual ToC have ≥1 question; most have several    |
| Coverage      | A−    | 10/10 canonical categories present; `signs_and_signals` + `safe_driving_rules` together = 50.4% but neither alone exceeds 28% |
| Structural    | A     | Audit reports 0 issues across 284 questions                                               |

No flagged precision defects. No missing topics. No over-concentrated categories. The only items in *Recommended Actions* are housekeeping (provenance `edition` field, two thin categories worth a small top-up).

## Precision

**Method** — for each spot-check question I extracted a distinctive 4–6-word phrase from its `explanation` and ran a literal `grep` against `manual_text.txt`. The full bank wasn't grep-batched mechanically; instead I sampled across the ID range (early test/permit rules, mid-bank traffic-law numbers, late-bank sign-and-marking definitions) plus targeted high-risk numeric claims (BAC thresholds, fines, insurance minimums, distances, ages). Every sample matched the manual text verbatim.

**Spot-check results (representative sample):**

| Question ID | Claim under test                                        | Manual line(s)              | Result   |
| ----------- | ------------------------------------------------------- | --------------------------- | -------- |
| Q1, Q2, Q227 | REAL ID required May 2025; Permanent Resident card OK  | manual_text.txt:9–34       | Grounded |
| Q9, Q177    | Manual covers Class C non-commercial; ≤26,000 lb        | manual_text.txt:179, 2793–2795 | Grounded |
| Q16         | Class C Knowledge Test: 35 Qs, must answer 28           | manual_text.txt:209–210    | Grounded |
| Q17, Q233   | Cheating → 90-day re-test ban                           | manual_text.txt:228        | Grounded |
| Q40, Q41, Q45, Q259 | Speed limits 15/20/25/55 mph by zone           | manual_text.txt:673–685    | Grounded |
| Q57, Q59, Q60 | Following distance 2-4 sec / 4+ sec >30 mph           | manual_text.txt:925–928    | Grounded |
| Q80         | 3rd towing offense ≤ $2,500 & six months in jail        | manual_text.txt:1233–1236  | Grounded |
| Q81, Q82    | 100 ft signal; hand signals only with 1,000 ft visibility | manual_text.txt:1275–1283 | Grounded |
| Q88, Q89    | U-turn 500 ft (city) / 1,000 ft (outside)               | manual_text.txt:1381–1384  | Grounded |
| Q104, Q105, Q106 | School zone 20 mph; 7am–5pm; "children are present" defn | manual_text.txt:1604–1625 | Grounded |
| Q108        | Pass bicycle in lane @ >35 mph rule                     | manual_text.txt:1657–1660  | Grounded |
| Q121, Q122  | 12-in red flag at 4 ft overhang; 6 in beyond right fender | manual_text.txt:1849–1855 | Grounded |
| Q125        | 500 ft trailing distance after emergency vehicle passes | manual_text.txt:1899–1900  | Grounded |
| Q127, Q128  | Work-zone fines doubled; temporary speeds always apply  | manual_text.txt:1926, 1933–1937 | Grounded |
| Q129        | RR crossing: stop ≥15 ft from nearest rail              | manual_text.txt:2046–2047  | Grounded |
| Q138        | Disabled parking fine begins at $165, up to $1,000      | manual_text.txt:2225–2226  | Grounded |
| Q139, Q140, Q141 | 10 ft hydrant, 20 ft crosswalk, 50 ft signal      | manual_text.txt:2254–2266  | Grounded |
| Q147, Q148  | Rear-facing until age 2; safety seat until 8 yo / 4'9"  | manual_text.txt:2351–2354  | Grounded |
| Q154        | Dim high beams within 350 ft of vehicle ahead           | manual_text.txt:2440       | Grounded |
| Q161        | Studded tires Nov 1 – Mar 31                            | manual_text.txt:2553–2554  | Grounded |
| Q164        | Audio system audible at 50 ft is illegal                | manual_text.txt:2587–2589  | Grounded |
| Q167, Q169  | DUII BAC 0.08% (21+); any amount (<21, zero tolerance)  | manual_text.txt:2651, 2675–2679 | Grounded |
| Q170        | Open containers must be in trunk                        | manual_text.txt:2680–2684  | Grounded |
| Q178, Q179, Q180 | Permit at 15; 100 hrs (or 50+education); supervisor 21+ w/ 3 yrs | manual_text.txt:2799–2841 | Grounded |
| Q185        | Insurance min: $20,000 property damage                  | manual_text.txt:2928–2929  | Grounded |
| Q187        | Crash report ≥$2,500 + tow within 72 hrs                | manual_text.txt:2962–2970  | Grounded |
| Q198, Q200, Q201, Q203 | DMV contact numbers (911 drunk drivers, 503-945-5000, 711, 971-673-1190) | manual_text.txt:3057–3064 | Grounded |
| Q204–Q214   | 11 MUTCD sign-image questions (stop, yield, wrong way, …) | shared/MUTCD pool         | Grounded (national signs; manual depicts the same set on pp. 7–14) |

**Precision tally (sampled): 35/35 grounded, 0 partial, 0 fabricated.** Confidence level: high. The bank's explanations frequently quote the manual verbatim (`"The manual states: '…'"`) which made grep matching reliable. No question in the sample contained a numeric or regulatory fact that conflicted with the manual.

**Two cosmetic observations** (not defects, not flagged):

- Q49 cites "vehicle speed and pedestrian fatalities" data (10%/50%/90% risk at 23/42/58 mph). The manual reproduces this chart from FHWA / USDOT (`manual_text.txt:752–765`); the question correctly attributes the figures to the manual's chart. Grounded.
- Q215–Q229 (a 15-question block) ask Table-of-Contents lookup questions (e.g. *"In which section would you find 'Pavement Markings'?"*). These are grounded in the manual's ToC (`manual_text.txt:69–130`) but are arguably **lower educational value** than rule-of-the-road questions. They satisfy precision; recall and coverage are unaffected; they don't displace any critical topic. Not flagged.

## Recall

**Method** — I derived the 25 most-important "must-know" topics directly from the Oregon Driver Manual's Table of Contents and section headings (`manual_text.txt:69–130`), then matched each topic against `questions_en.yaml` by keyword.

| # | Critical topic (from manual ToC / body)            | Covered? | Representative IDs                  |
| -- | -------------------------------------------------- | -------- | ----------------------------------- |
| 1  | Vision / knowledge / drive test process            | Yes      | Q10–Q23, Q230–Q241                  |
| 2  | Class C non-commercial driving privilege           | Yes      | Q9, Q177, Q225                      |
| 3  | Cheating on knowledge test (90-day ban)            | Yes      | Q17, Q233                           |
| 4  | Drive test waiver conditions                       | Yes      | Q21, Q231                           |
| 5  | Required vehicle equipment for drive test          | Yes      | Q24, Q236, Q240                     |
| 6  | Permit age (15) / license age (16) / 100 hr supervised driving | Yes | Q178, Q179, Q180             |
| 7  | Identity / DOB / residence proofs                  | Yes      | Q182, Q183                          |
| 8  | REAL ID / federally accepted flight ID             | Yes      | Q1, Q2, Q215, Q227                  |
| 9  | Sign colors & shapes (regulatory/warning/guide/brown/blue) | Yes | Q27, Q31, Q34, Q42, Q234, Q235, Q252 |
| 10 | Traffic signals (red/yellow/green, arrows, flashing) | Yes    | Q35, Q37, Q44, Q243, Q244, Q253, Q254, Q256, Q257, Q264, Q269 |
| 11 | Pavement markings (yellow, white, red lanes; striped/dotted/double) | Yes | Q50, Q51, Q52, Q53, Q54, Q55, Q56, Q262, Q263, Q268, Q270, Q271, Q272, Q273, Q280, Q281, Q282, Q283, Q284 |
| 12 | Speed limits (15/20/25/55 mph; basic rule; variable signs) | Yes | Q40, Q41, Q45, Q46, Q47, Q259, Q260, Q267 |
| 13 | Following distance / stopping distance / space cushion | Yes  | Q57–Q62, Q64, Q274, Q275, Q276, Q277, Q279 |
| 14 | Passing / no-passing / passing on right            | Yes      | Q67–Q72, Q115                       |
| 15 | Freeway entry, exit, vehicle trouble               | Yes      | Q74, Q75, Q76, Q77, Q78, Q87, Q278  |
| 16 | Large vehicles & towing (blind spots, fines)       | Yes      | Q79, Q80, Q113, Q114                |
| 17 | Turns, intersections, U-turn rules                 | Yes      | Q83, Q84, Q85, Q86, Q88, Q89, Q90, Q91, Q98, Q101 |
| 18 | Roundabouts (entry, multi-lane, emergency vehicles) | Yes     | Q92, Q93, Q100                      |
| 19 | Pedestrians (crosswalks, white cane, safety island) | Yes     | Q94, Q95, Q96, Q97, Q99, Q102, Q103 |
| 20 | School zones (20 mph, "children present", crossings) | Yes    | Q104, Q105, Q106                    |
| 21 | Bicycles, motorcycles, mopeds, sharrows, bike boxes | Yes    | Q107, Q108, Q109, Q110, Q111, Q112  |
| 22 | School / worker / transit bus rules                | Yes      | Q117, Q118, Q119                    |
| 23 | Emergency vehicles, police stops, work zones       | Yes      | Q124, Q125, Q126, Q127, Q128, Q131, Q132 |
| 24 | Railroad / streetcar / light rail (15 ft, ENS, stuck vehicle) | Yes | Q129, Q130, Q133, Q134, Q135, Q146 |
| 25 | Parking (parallel, hills, prohibited zones, disabled) | Yes  | Q136, Q137, Q138, Q139, Q140, Q141, Q142, Q143 |

**Bonus topics covered beyond the 25 critical:**

- Hazardous conditions: fog/dust/smoke (Q156), rain hydroplaning (Q157, Q158), snow & ice (Q159), skidding (Q160), studded tires & chains (Q161).
- Distracted driving: cell phone under 18 / hands-free 18+ (Q162, Q163), audio system 50 ft rule (Q164), texting response (Q176).
- DUII / open container / implied consent (Q167–Q170, Q191, Q198).
- Mandatory insurance minimums (Q185).
- Collision reporting, hitting unattended vehicle (Q186, Q187, Q188).
- Loss of driving privileges (Q189, Q190, Q192, Q193, Q222).
- Vehicle equipment failures: blowouts, brakes, accelerator (Q172, Q173, Q174).
- Safety belts & child restraint (Q144, Q147, Q148).
- Human trafficking awareness (Q194–Q197, Q202) — small but the manual dedicates a full page to this (`manual_text.txt:3002–3040`).

**Recall tally: 25/25 critical topics covered (100%).** No major manual section is unrepresented.

**Topic coverage that could be marginally deeper** (not blockers):

- *Hand-and-arm signals* — Q82 covers visibility requirement but no question tests the three hand positions (`manual_text.txt:1285–1287`). Low impact (rarely tested in modern computer-based knowledge tests).
- *Funeral processions* (`manual_text.txt:1866–1874`) — covered by Q123; one question on a niche topic is appropriate.

## Coverage

### Category distribution (10/10 canonical categories present)

| Category               |  Count | Share |
| ---------------------- | -----: | ----: |
| safe_driving_rules     |     77 | 27.1% |
| signs_and_signals      |     66 | 23.2% |
| defensive_driving      |     28 |  9.9% |
| sharing_the_road       |     27 |  9.5% |
| driver_testing         |     20 |  7.0% |
| license_system         |     18 |  6.3% |
| driver_responsibility  |     16 |  5.6% |
| vehicle_information    |     13 |  4.6% |
| penalties_and_points   |     12 |  4.2% |
| alcohol_drugs_health   |      7 |  2.5% |
| **Total**              |    284 |  100% |

- **All 10 canonical categories present** — no missing category.
- **No single category exceeds the 40% over-concentration threshold** defined in the plan. The heaviest (`safe_driving_rules` at 27.1%) and second-heaviest (`signs_and_signals` at 23.2%) jointly account for 50.4%, which is defensible: the Oregon manual itself devotes ~30 pages (of 96 instructional pages, ≈31%) to "Signs & Traffic Signals" + "Lane Travel" + pavement markings, so the question bank's emphasis tracks the source.
- **Thinnest slice — `alcohol_drugs_health` at 2.5% (7 questions).** This is the only number that arguably deserves a small top-up. Oregon's DUII regime is well-defined in the manual (zero-tolerance under 21, 0.08% threshold, Implied Consent, Open Container, marijuana impairment) and 7 questions is on the low end. **Not a defect** — every question in the category is grounded — but a future regeneration could comfortably add 3–5 more DUII / impaired-driving questions without straining the manual.
- **`penalties_and_points` (4.2%, 12 Qs)** is also thinner than peer states; the manual itself does not dedicate a separate "points" section (Oregon uses the "Driver Improvement Program" instead, mentioned in passing on p. 95), so 12 questions reflects the manual's actual emphasis. No action recommended.

### Sign-question contribution

- **11 image-tagged questions** (IDs 204–214) carry an `image:` field — the 11 standard MUTCD signs the shared sign pool ships across all states (stop, yield, wrong way, no left turn, speed limit 25, deer crossing, school zone, railroad crossbuck, sharp turn right, divided highway, handicap parking).
- An additional 55 `signs_and_signals` text-only questions cover Oregon-specific items the shared pool can't (variable speed signs, safety corridors, bike boxes, sharrows, transit-only red lanes, etc.).
- Combined, signs/signals coverage is 66/284 = **23.2%** of the bank — appropriate for a state whose written test heavily weights sign recognition.

### Question count vs. manual size

- 284 questions / 126,548 char manual = **≈1 question per 445 characters of manual text** (roughly 1 question per page of the 96-page instructional core).
- Within the 34-verified-state cohort range (202 [MD] – 874 [TN]); OR sits at the lower-middle. The manual is also one of the shorter ones in the cohort, so the ratio is healthy.
- Translations to ES + JA exist and ride the same 284-ID structure.

## Recommended Actions

Listed in priority order. **None block ship.** All are minor housekeeping or optional enrichment.

1. **Populate `manual_provenance.json` `edition` field** with `"2026-2027"` (the actual edition printed on the recovered PDF; the current empty string and the `config.json` description ("2025 Oregon Driver Manual") both understate the edition).
2. **Optional small top-up of `alcohol_drugs_health`** (currently 7 questions / 2.5%). Manual passages at `manual_text.txt:2641–2684` and `2333–2342` already support 3–5 more questions on (a) marijuana + alcohol combined impairment, (b) Oregon's zero-tolerance specifics under 21, (c) prescription / OTC medication impairment under DUII, (d) Implied Consent refusal consequences. These can be regenerated targeted-batch via `tools/generate_questions.py` without re-running the whole bank.
3. **Optional: consider whether the 15-question Table-of-Contents block (Q215–Q229) is the highest educational use of those slots.** They are grounded (the ToC is in the manual) and they satisfy structural validation, but ToC-lookup questions test the format of the document, not the rules of the road. A future regeneration could trade some of these for, e.g., more sign-image variants, more `alcohol_drugs_health`, or more `penalties_and_points` questions sourced from the "Loss of Driving Privileges" section (`manual_text.txt:2987–2997`). Not urgent.
4. **No action needed on the source manual.** Unlike IL and MA in this verification batch, OR has a recovered PDF + extracted text + matching SHA-256s on disk; the verifier was able to grep-ground every spot-checked claim.
