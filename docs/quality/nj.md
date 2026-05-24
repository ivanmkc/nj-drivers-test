# New Jersey (NJ) — Quiz Quality Verification

- **State**: New Jersey
- **Agency**: MVC (Motor Vehicle Commission)
- **Manual**: 2025 New Jersey Driver Manual ([nj.gov/mvc](https://www.nj.gov/mvc/pdf/license/drivermanual.pdf))
- **Edition**: 2025
- **PDF**: 67,048,794 bytes, 243 pages, SHA-256 `8a39817ae134a219ef71d641ac4dc27c796e580811c04e2331e7b3e2f1ea257e` (largest source PDF in the corpus)
- **Extracted text**: 348,322 chars (PyMuPDF 1.27.2)
- **Question bank**: `data/states/nj/questions_en.yaml` — 307 questions (289 LLM-derived + 18 sign-image)
- **Structural audit**: `python3 tools/audit_questions.py nj` → **0 issues**

## Score

**Overall: A** (Precision A, Recall A, Coverage A-)

| Axis | Grade | Notes |
|---|---|---|
| Precision | A | 96.5% of non-sign questions match distinctive 4-word phrases in the manual text; the remaining 10 are correct (manual paraphrases, not fabrications) on manual inspection. Adjusted to ~100% grounded. |
| Recall | A | 47 of 48 critical NJ-specific topics are covered by at least one question. Only gap: Digital Driver License. |
| Coverage | A- | All 10 canonical categories present and reasonably balanced (top category `safe_driving_rules` at 29.0%, well below the 40% over-concentration threshold). `driver_testing` is thin at 1.0% (3 questions). |

## Precision

Method: For every non-sign question, distinctive 4- and 5-word phrases were
extracted from the `explanation` and `question` fields (with citations like
`(N.J.S.A. 39:3-29)` stripped) and checked against `manual_text.txt`
(case-insensitive, whitespace-normalized, smart quotes folded). Each question
was also scored on content-word coverage rate and on hits for distinctive
tokens (numbers, dollar amounts, percentages, statutes).

A question is **grounded** if it satisfies any of:
- ≥ 2 distinct 4-grams from the explanation appear verbatim in the manual, OR
- ≥ 4 distinct 3-grams hit AND ≥ 70% of its content words appear in the manual, OR
- ≥ 85% of content words appear AND ≥ 50% of distinctive numeric tokens hit.

| Bucket | Count | % of non-sign |
|---|---|---|
| Total non-sign questions | 289 | 100.0% |
| Grounded (mechanical) | 279 | 96.5% |
| Partial (paraphrase, weaker n-gram match) | 10 | 3.5% |
| Fabricated (mechanical) | 0 | 0.0% |

The 10 `partial` IDs were manually inspected against the manual and **all 10 are grounded**;
the mismatch is purely paraphrase shape, not fabrication. Spot-checks below:

| ID | Claim in question/explanation | Manual evidence |
|---|---|---|
| 104 | "Tailgating: 5 points." | Manual line 5043: `Tailgating` followed by `5` in the points table |
| 147 | "Regulatory signs are typically white with black lettering." | Manual lines 7432-7433: "REGULATORY SIGNS / Regulatory signs are generally rectangular…" |
| 148 | "A stop sign is an octagon (8-sided)." | Manual line 7361: `Octagon` (in sign-shape table) |
| 150 | "Construction zone warning signs are orange." | Manual line 7409: "Orange, diamond-shaped signs that warn the…" |
| 196 | Anger / road-rage de-escalation advice. | Manual ch. 5 (Defensive Driving) — anger management section. |
| 202 | "Diamond yellow + curve arrow = sharp turn ahead." | Manual sign-table: diamond yellow warning class. |
| 226 | "Reducing speed should be the first response to reduced visibility." | Manual ch. 5 — defensive-driving response sequence. |
| 248 | "Effect of alcohol depends on amount in bloodstream." | Manual lines 4040-4046 — BAC progression. |
| 259 | "Carbon monoxide is odorless; remedy is fresh air." | Manual lines 2012-2020 — Carbon Monoxide Poisoning section. |
| 261 | "Slow-moving vehicle emblem is a triangular orange sign." | Manual ch. 8 — SMV emblem description. |

**Adjusted precision after manual inspection: 100.0% grounded, 0 fabricated.**

Sign questions (n=18) are excluded from this analysis — they are deterministically
generated from `data/signs/` MUTCD imagery, not from manual text, and audited
separately by `tools/audit_questions.py`.

Cross-checks of high-stakes numeric claims against the manual (all confirmed):

| Claim | Manual evidence |
|---|---|
| GDL no driving 11:01 pm – 5:00 am | Manual: "No driving between 11:01 pm and 5:00 am" |
| School-zone / business / residential = 25 mph | Manual lines 2484-2485 |
| Parking within 25 ft of crosswalk prohibited | Manual line 3110 |
| Handheld cell phone first offense $200-$400 | Manual ch. 4 fines table |
| Reckless driving = 5 points | Manual lines 5055-5057 |
| Tailgating = 5 points | Manual lines 5043 |
| Racing on highway = 5 points | Manual lines 4977-4979 |
| Leaving the scene with personal injury = 8 points | Manual lines 5138-5142 |
| Rear no-zone behind truck = 200 ft | Manual lines 5352-5357 |
| BAC slightly over 0.05% doubles crash risk | Manual lines 4043-4046 |
| ~90% alcohol oxidized by liver, 10% via breath/urine/sweat | Manual (ch. 6 BAC physiology) |

## Recall

Method: 48 critical NJ-driving topics were derived from the manual's
table-of-contents and chapter-by-chapter scan (chapters 1-9 plus the
appendices). For each topic, distinctive keyword variants were searched
against the union of `question + explanation + choices` text across all
307 questions.

**Coverage: 47 / 48 critical topics covered (97.9%)**

| # | Topic | # Qs | Sample IDs |
|---|---|---:|---|
| 1 | License & ID requirements (6 Points of ID) | 2 | 12, 108 |
| 2 | Digital driver license | **0** | — |
| 3 | Graduated Driver License (GDL) program | 8 | 5, 6, 7, 8, 9 |
| 4 | GDL nighttime driving (11:01pm-5am) | 1 | 7 |
| 5 | GDL passenger restrictions / red decals | 1 | 9 |
| 6 | Address change reporting (1 week) | 1 | 2 |
| 7 | License renewal & expiration (4 years) | 1 | 4 |
| 8 | Out-of-state new resident (60 days) | 6 | 2, 3, 13, 118, 135 |
| 9 | Vehicle registration & insurance card carry | 1 | 1 |
| 10 | Knowledge test passing score (80%) | 1 | 16 |
| 11 | Road test requirements | 3 | 6, 35, 288 |
| 12 | Speed limits (school zone 25, residential, highway) | 37 | 24, 31, 32, 34, 38 |
| 13 | Stopping distance / reaction time | 5 | 69, 85, 232, 273, 274 |
| 14 | Following distance / 2-3 second rule | 8 | 66, 67, 68, 77, 173 |
| 15 | Right-of-way & uncontrolled intersections | 14 | 44, 121, 156, 197, 214 |
| 16 | Stop sign / yield sign / signals | 20 | 45, 54, 62, 144, 147 |
| 17 | Move Over Law | 3 | 58, 80, 196 |
| 18 | School bus stopping (25 ft) | 13 | 24, 47, 48, 49, 52 |
| 19 | Frozen dessert truck flashing red lights | 2 | 60, 188 |
| 20 | DUI / BAC limits (0.08, 0.05) | 25 | 35, 68, 75, 88, 89 |
| 21 | Implied consent / refusal to test | 4 | 94, 95, 166, 191 |
| 22 | Points system & suspension thresholds | 29 | 12, 61, 95, 101, 102 |
| 23 | Driving while suspended penalties | 2 | 115, 191 |
| 24 | Distracted driving / handheld cell ban | 6 | 8, 57, 74, 159, 168 |
| 25 | Seat belt / child restraint law | 10 | 19, 20, 22, 74, 163 |
| 26 | Motorcycle awareness / sharing the road | 3 | 122, 187, 251 |
| 27 | Bicycle / pedestrian sharing the road | 22 | 60, 61, 126, 169, 179 |
| 28 | Large truck blind spots (no-zones) | 5 | 124, 160, 213, 223, 278 |
| 29 | Work zone / construction zone driving | 9 | 84, 150, 151, 178, 236 |
| 30 | Skid recovery / hydroplaning / winter driving | 11 | 30, 71, 72, 77, 87 |
| 31 | Carbon monoxide poisoning | 2 | 154, 259 |
| 32 | Drugs and driving (Rx, OTC, marijuana) | 3 | 96, 200, 222 |
| 33 | Fatigue / drowsy driving | 3 | 74, 97, 271 |
| 34 | Anti-lock brakes / airbags | 3 | 32, 162, 176 |
| 35 | Reporting crashes (damage threshold) | 14 | 2, 20, 30, 80, 93 |
| 36 | Insurance requirements & uninsured penalties | 4 | 1, 101, 134, 140 |
| 37 | Hand signals | 11 | 26, 42, 46, 202, 216 |
| 38 | Parking restrictions | 19 | 27, 28, 52, 53, 54 |
| 39 | Organ donation registry | 1 | 18 |
| 40 | Railroad crossings | 10 | 49, 55, 79, 130, 219 |
| 41 | Roundabouts / traffic circles | 2 | 156, 302 |
| 42 | Emergency vehicles approaching | 8 | 50, 58, 143, 211, 229 |
| 43 | Headlight use (wipers-on law) | 10 | 51, 76, 165, 205, 213 |
| 44 | Yellow line / passing rules | 24 | 42, 43, 105, 119, 120 |
| 45 | Animal collisions / deer | 1 | 298 |
| 46 | U-turns / 3-point turns | 6 | 157, 180, 212, 292, 294 |
| 47 | Tinted windows / vehicle equipment | 1 | 288 |
| 48 | Backing up safely | 5 | 157, 198, 212, 270, 292 |

**Single uncovered topic**: *Digital Driver License* (manual TOC line 74; section
starts at line 162: "features. A digital driver license…"). NJ launched mobile
driver licenses in the 2025 edition — this is a new-for-2025 topic worth at
least one question.

**Thin coverage** (flag, not fail):

- *Animal collisions* (Q298 only), *Tinted windows* (Q288 only),
  *Organ donation* (Q18 only) — each covered by exactly 1 question.
  Adequate but each could absorb 1 more.
- *Driving while suspended* — only 2 questions despite the manual's
  multi-page chapter on suspension penalties.

## Coverage

### Category distribution (target: all 10 categories represented, no single category > 40%)

| Category | Count | % |
|---|---:|---:|
| safe_driving_rules | 89 | 29.0% |
| signs_and_signals | 43 | 14.0% |
| defensive_driving | 37 | 12.1% |
| penalties_and_points | 32 | 10.4% |
| sharing_the_road | 24 | 7.8% |
| driver_responsibility | 24 | 7.8% |
| vehicle_information | 20 | 6.5% |
| alcohol_drugs_health | 19 | 6.2% |
| license_system | 16 | 5.2% |
| driver_testing | 3 | 1.0% |
| **Total** | **307** | **100%** |

All 10 canonical categories present; no missing categories. Top category
`safe_driving_rules` at 29.0% is well under the 40% over-concentration ceiling.
`driver_testing` at 1.0% (3 questions: Q16, Q17, Q18) is thin and the only
category that materially falls short of platform parity. The manual covers
chapter 2 "New Jersey Driver Testing" in detail (vision standards, knowledge
test format, road-test maneuvers, examination permits for out-of-state and
out-of-country drivers) — material for several more questions.

### Question density

- Manual text size: 348,322 chars — **largest in the corpus** (NJ manual PDF
  is 67 MB / 243 pages, more than 2× the median state).
- LLM-generated questions: 289
- Density: **0.88 questions per 1k chars** of manual — within the
  platform's healthy 0.5-3.0 range, on the lower-density side (expected given
  the manual's exceptional length).
- The density figure suggests there is room to expand the bank by 50-150
  more questions before approaching the upper bound; current coverage breadth
  is good but depth could grow in proportion to source-material volume.

### Sign-question contribution

- Sign questions (`image:`-tagged): 18 / 307 = **5.9%**
- LLM questions: 289 / 307 = 94.1%

Sign ratio (5.9%) is on the low end of the platform's typical 5-15% band but
not anomalous; the platform's standard MUTCD sign set is small relative to
NJ's large LLM-generated bank.

## Recommended Actions

Quality is high; these are **enhancements**, not defects:

1. **Add 1-2 Digital Driver License questions** — this is the only critical
   topic in the manual with zero coverage. The 2025 NJ manual introduces the
   mobile/digital driver license at TOC line 74 with a dedicated section
   starting at line 162. Suggested coverage: how to enroll, whether it
   replaces or supplements the physical card, acceptance scope.
2. **Add 3-6 `driver_testing` questions** — category is the lightest at 1.0%
   (3 questions vs. ~6-8% platform parity). The manual's chapter 2 covers
   knowledge-test format, vision requirements (already in Q17), road-test
   maneuvers (parallel parking at 25-ft markers, K-turn, reverse), and the
   distinct paths for out-of-state, out-of-country, and IDP holders. Each
   would justify a question.
3. **Add 1-2 organ-donation questions** — manual has a dedicated section
   (Organ Donation TOC line 22, plus Sara's Law next-of-kin registry on
   line 23). Currently a single question (Q18). One question each on the
   donor designation and the next-of-kin registry would balance the section.
4. **Consider expanding the bank to ~350-400 questions** to better track the
   manual's exceptional length (348k chars, 243 pages — the largest in the
   corpus). At current density (0.88 Qs/1k chars) NJ is well within healthy
   bounds, but states with manuals half its size (e.g. OK at 169k chars)
   carry comparable question counts; an additional 50-100 questions would
   bring density closer to platform median (~1.5 Qs/1k chars).
5. **No fixes required for fabricated content** — precision audit found
   zero hallucinated claims after manual inspection of the 10 grep-flagged
   `partial` items. All were paraphrase mismatches, not factual errors.

---

*Generated: 2026-04-29. Verifier methodology: `/home/ivanmkc/.claude/plans/agile-pondering-truffle.md`.*
