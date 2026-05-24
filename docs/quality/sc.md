# South Carolina (SC) — Quiz Quality Verification

- **State**: South Carolina
- **Agency**: DMV (SCDMV)
- **Manual**: South Carolina Driver's Manual ([dmv.sc.gov](https://dmv.sc.gov/sites/scdmv/files/2025-12/Drivers%20Manual%20-%20Forms%20and%20Manuals.pdf))
- **Edition**: 2025-12 (revised 06/2024 per text; published Dec 2025)
- **PDF**: 5,120,742 bytes, 140 pages, SHA-256 `4a2b2dfde8c905f495aea2120cbf6b31d9ee7764625e39c01e0eaac3780198cc`
- **Extracted text**: 159,739 chars (PyMuPDF 1.27.2)
- **Question bank**: `data/states/sc/questions_en.yaml` — 281 questions (247 LLM-derived + 34 sign-image)
- **Structural audit**: `python3 tools/audit_questions.py sc` → **0 issues**

## Score

**Overall: A** (Precision A, Recall A, Coverage A)

| Axis | Grade | Notes |
|---|---|---|
| Precision | A | 100% of non-sign questions grounded after manual inspection — 241/247 (97.6%) auto-matched a distinctive 5-gram, and all 6 grep-missed items were verified by direct inspection to be faithful paraphrases of explicit manual text. Zero fabrications. |
| Recall | A | 34/34 critical topics covered (100%), including the SC-specific hurricane evacuation route sign (Q136), Move-Over law, Zipper Merge, DDI/RCUT intersections, and SC's primary safety-belt enforcement law. |
| Coverage | A | All 10 canonical categories present and well balanced (top category `safe_driving_rules` at 24.6%, well under the 40% over-concentration ceiling). Density 1.74 questions/1k chars — squarely inside the healthy 0.5–3.0 range. |

## Precision

Method: For every non-sign question, distinctive 5-word phrases were
extracted from the `explanation` field and matched (case-insensitive,
whitespace-normalized) against `manual_text.txt`. Items missed by the
5-gram screen were re-checked with 4-grams and then by direct manual
inspection.

| Bucket | Count | % of non-sign |
|---|---|---|
| Total non-sign questions | 247 | 100.0% |
| Grounded (≥1 5-gram match in manual) | 241 | 97.6% |
| Partial (no 5-gram, ≥3 4-grams) | 0 | 0.0% |
| Unmatched by mechanical grep | 6 | 2.4% |

The 6 unmatched IDs were manually inspected and **all 6 are grounded** — the
mismatch is paraphrase shape, not fabrication:

| ID | Claim | Manual evidence |
|---|---|---|
| 4  | "Minimum age to obtain a Class G moped license is 15." | Manual line 213: *"(Minimum age 15)"* in the Class G section. |
| 10 | "Class E single unit >26,000 GVW; Class F combination >26,000 GVW." | Manual lines 178–202 spell out both definitions verbatim. |
| 15 | "Class D, E, F, or M permit three-wheel vehicle operation." | Manual lines 160, 182, 202, 225 each name three-wheel vehicle as permitted under those classes. |
| 137 | "White lane markings indicate a one-direction roadway; yellow markings indicate a two-direction roadway." | Manual lines 2768–2772 (Pavement Markings section) describe one-direction vs. two-direction roadways via white/yellow markings. |
| 178 | "Increase your following distance on slippery roads, at night, in fog, or in inclement weather." | Manual lines 3635–3650 — verbatim bullet list under "Increase your following distance". |
| 243 | "Regulatory signs are white." | Manual lines 5097–5100 (Practice Test answer 6c: *"Regulatory signs are: ... c. white."*); also lines 2613–2614 ("white with black, red, or green letters"). |

**Adjusted precision after manual inspection: 247/247 = 100.0% grounded, 0 fabricated.**

User-flagged SC-specific item — verified:

- **Hurricane evacuation route sign (Q136)** — directly traces to manual line 2723: *"Evacuation Route Sign— In the event of a hurricane, a mandatory evacuation may be declared for the coastal areas of SC. This sign indicates the road or highway is used as an evacuation route in this type of emergency."* Q136's stem ("When might you see an Evacuation Route sign…"), answer ("During a mandatory evacuation for a hurricane"), and explanation are a clean paraphrase of this passage. **No issues.**

Sign questions (n=34, IDs 248–281) are excluded from precision analysis —
they are deterministically generated from `data/signs/` MUTCD imagery (not
the manual text) and are audited structurally by
`tools/audit_questions.py`.

## Recall

Method: 34 critical SC driving topics were derived from `manual_text.txt`'s
table-of-contents headings (Sections 1–12) plus state-specific items
(hurricane evacuation, Move-Over law, Zipper Merge, DDI/RCUT, primary
safety-belt enforcement). Each topic was matched against the union of
`question + explanation` text across all 281 questions via keyword
overlap.

**Coverage: 34 / 34 critical topics (100%)**

| # | Topic | # Qs | # | Topic | # Qs |
|---|---|---:|---|---|---:|
| 1 | License classes (D/E/F/G/M) | 12 | 18 | Pavement markings (white vs. yellow) | 2 |
| 2 | GVW/GVWR weight thresholds | 7 | 19 | Roundabouts / DDI / RCUT intersections | 7 |
| 3 | Beginner's permit age/hours | 4 | 20 | School bus stopping rules | 2 |
| 4 | Graduated / conditional license restrictions | 9 | 21 | Parking rules / hills / disability | 14 |
| 5 | License renewal & ID card | 6 | 22 | Passing / Zipper merge | 25 |
| 6 | Point system / 12-point suspension | 6 | 23 | Following distance (4-second rule) | 6 |
| 7 | Vision / hearing / health requirements | 13 | 24 | Hydroplaning / wet roads / flooding | 4 |
| 8 | Driver distractions / texting | 1 | 25 | Stopping distance / perception / reaction | 3 |
| 9 | Aggressive driving / road rage | 3 | 26 | Emergencies: ABS, skids, malfunctions | 5 |
| 10 | DUI/DUAC and BAC limits (0.02 / 0.05 / 0.15) | 26 | 27 | Pedestrians / bicyclists / motorcyclists | 19 |
| 11 | Implied consent | 3 | 28 | Move-Over Law / emergency vehicles | 2 |
| 12 | Over-the-counter / prescription drugs | 3 | 29 | Work zones / construction | 5 |
| 13 | Safety belts (primary enforcement) | 5 | 30 | Night driving / high beam / low beam | 7 |
| 14 | Air bags | 4 | 31 | Winter driving / ice / snow | 4* |
| 15 | Child passenger safety / car seats / boosters | 4 | 32 | **Hurricane evacuation route sign (SC-specific)** | **1** |
| 16 | Stop signs / yield signs / right-of-way | 17 | 33 | Slow-moving vehicles / farm equipment | 1 |
| 17 | Traffic signal colors and arrows | 6 | 34 | Safe trailering | 9 |

\* "Winter" as a keyword catches incidental prose ("in winter…") in many
questions; the substantive winter-driving topic is covered through the
ABS / skid / ice / snow questions and matches the manual's brief Section 11
treatment.

**SC-specific items both confirmed:**

- **Hurricane evacuation route sign** — Q136 directly tests it (see
  Precision section). The manual itself devotes only one short paragraph
  (line 2723) to this sign, so 1 question is proportionate to the manual's
  emphasis.
- **Move-Over Law** — covered by 2 questions; manual lines 4503–4527.

**Thin coverage** (flag, not fail):

- *Driver distractions / texting* — only 1 question; the manual's distractions
  subsection is short, so 1 is defensible, but a second on hand-held device
  specifics would round it out.
- *Move-Over Law* — 2 questions; given how prominently SC promotes this and
  the manual's full subsection, 3–4 would better match its weight.
- *Slow-moving vehicles* — 1 question; manual covers SMV triangle, farm
  machinery, and animal-drawn vehicles — could absorb 1–2 more.
- *School bus stopping rules* — 2 questions; manual gives this its own
  section with multiple sub-rules (passing rules, multi-lane exemptions),
  could justify 3–4 questions.

## Coverage

### Category distribution

Target: all 10 categories represented, no single category > 40%.

| Category | Count | % |
|---|---:|---:|
| safe_driving_rules | 69 | 24.6% |
| signs_and_signals | 51 | 18.1% |
| license_system | 33 | 11.7% |
| defensive_driving | 32 | 11.4% |
| sharing_the_road | 24 | 8.5% |
| vehicle_information | 20 | 7.1% |
| driver_testing | 15 | 5.3% |
| penalties_and_points | 14 | 5.0% |
| driver_responsibility | 13 | 4.6% |
| alcohol_drugs_health | 10 | 3.6% |
| **Total** | **281** | **100%** |

All 10 canonical categories present. Top category (`safe_driving_rules`) at
24.6% sits comfortably under the 40% over-concentration ceiling.
`alcohol_drugs_health` (3.6%) and `driver_responsibility` (4.6%) are the
lightest — defensible given the SC manual's emphasis, but each could absorb
2–3 more questions to reach the platform average (~5–7% per minor category).

### Question density

- Manual text size: 159,739 chars (~140 PDF pages)
- LLM-generated questions: 247
- Density: **1.55 questions per 1k chars** of manual text (or **1.74** counting
  all 281 questions including sign questions) — squarely inside the platform's
  healthy 0.5–3.0 range; no dilution or over-stuffing.

### Sign-question contribution

- Sign questions (`image:`-tagged): 34 / 281 = **12.1%**
- LLM questions: 247 / 281 = 87.9%

Mix is typical for the platform.

## Recommended Actions

Quality is high; these are **enhancements**, not defects:

1. **Add 2–3 `alcohol_drugs_health` questions** — at 3.6% (10 questions),
   this is the leanest canonical category. SC's manual has rich BAC / DUI /
   DUAC / implied-consent content (lines 1424–1542) that could support more
   coverage on three-month vs. six-month suspensions and the ADSAP program.
2. **Add 1–2 distracted-driving / texting questions** — only 1 question
   currently. Even a short question on whether electronic devices are
   permitted during the knowledge test (manual lines 533–539) or general
   hand-held bans would round this out.
3. **Add 2 more school-bus questions** — sub-rules for multi-lane
   exemptions, amber-flashing-light response, and the "preparing to stop"
   rule (lines 3083–3110) are testable but underrepresented.
4. **Add 1–2 more Move-Over Law questions** — given SC explicitly cites this
   law (manual lines 4503–4527) and statewide enforcement campaigns, 3–4
   questions would better match its emphasis vs. the current 2.
5. **No fixes required for fabricated content** — precision audit found
   zero hallucinated claims after manual inspection of the 6 grep-missed
   items. All 6 were paraphrase mismatches, not factual errors.
6. **Hurricane evacuation route sign — confirmed correct.** Q136 is a
   faithful test of the manual's coverage; no action needed.

---

*Generated: 2026-04-29. Verifier methodology: `/home/ivanmkc/.claude/plans/agile-pondering-truffle.md`.*
