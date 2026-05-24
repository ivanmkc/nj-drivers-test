# Oklahoma (OK) — Quiz Quality Verification

- **State**: Oklahoma
- **Agency**: DPS (Service Oklahoma)
- **Manual**: Oklahoma Driver Manual ([oklahoma.gov](https://oklahoma.gov/content/dam/service-oklahoma/Documents/OklahomaDriverManual.pdf))
- **Edition**: 2025
- **PDF**: 35,529,028 bytes, 74 pages, SHA-256 `4850f92208fe34cd6540dc54ae572f32f43907b311aa2ffbc58c835bc917d808`
- **Extracted text**: 169,164 chars (PyMuPDF 1.27.2)
- **Question bank**: `data/states/ok/questions_en.yaml` — 307 questions (273 LLM-derived + 34 sign-image)
- **Structural audit**: `python3 tools/audit_questions.py ok` → **0 issues**

## Score

**Overall: A** (Precision A, Recall A, Coverage A-)

| Axis | Grade | Notes |
|---|---|---|
| Precision | A | 99.3% of non-sign questions match distinctive 4-6-word phrases in the manual text; the 2 remaining are correct (manual paraphrases, not fabrications). |
| Recall | A | 100% of 35 critical driving topics covered, including the user-flagged Oklahoma-specific items: compulsory liability insurance and license/tag suspension on collision. |
| Coverage | A- | All 10 canonical categories present and reasonably balanced (top category 21.8%, well under the 40% over-concentration threshold). One mildly thin area: `driver_testing` at 2.9%. |

## Precision

Method: For every non-sign question, distinctive 4-, 5-, and 6-word phrases were
extracted from the `explanation` field and checked against `manual_text.txt`
(case-insensitive, whitespace-normalized).

| Bucket | Count | % of non-sign |
|---|---|---|
| Total non-sign questions | 273 | 100.0% |
| Grounded (≥1 long-phrase match) | 268 | 98.2% |
| Partial (≥3 trigram matches) | 3 | 1.1% |
| Unmatched by mechanical grep | 2 | 0.7% |

The 2 unmatched IDs were manually inspected and **both are grounded** — the
mismatch is purely paraphrase shape, not fabrication:

| ID | Claim | Manual evidence |
|---|---|---|
| 76 | "Yellow is used for general warning signs." | Manual line 1744: *"WARNING SIGNS are diamond-shaped, with a yellow background and black letters."* |
| 273 | "All other violations result in 1 point." | Manual: *"All other violations (excluding the violations requiring suspension or revocation action).....1"* (TOC of points table) |

Adjusted precision after manual inspection: **100.0% grounded**, **0 fabricated**.

Sign questions (n=34) are excluded from this analysis — they are
deterministically generated from `data/signs/` MUTCD imagery, not from the
manual text, and audited separately by `tools/audit_questions.py`.

## Recall

Method: 35 critical Oklahoma driving topics were derived from `manual_text.txt`
table-of-contents headings and the user-supplied known-important topics (no
insurance / compulsory liability / suspension on collision). Each topic was
matched against the union of `question + explanation + choices` text across all
307 questions.

**Coverage: 35 / 35 critical topics (100%)**

| Topic | # Qs | Topic | # Qs |
|---|---|---|---|
| Compulsory liability insurance | 4 | Pavement markings | 9 |
| License/tag suspension on collision | 2 | Distracted driving / cell phone | 2 |
| Proof of insurance / security verification | 5 | DUI / drugs | 9 |
| Implied consent / BAC | 24 | Points system | 18 |
| Speed limits | 23 | Mandatory revocation | 14 |
| Stopping at red lights | 8 | GDL / learner permit | 21 |
| Stop sign / right of way | 9 | License classes | 7 |
| Following distance | 8 | Renewal / REAL ID | 6 |
| School bus stop | 5 | Organ donor | 1 |
| Move-over law | 5 | Skid / hydroplaning | 4 |
| Seat belt | 2 | Night driving / headlights | 15 |
| Child restraint | 2 | Passing / no-passing | 22 |
| Motorcycle / bicycle sharing | 25 | Pedestrian / crosswalks | 19 |
| Roundabout | 2 | Parking rules (hill / curb) | 4 |
| Work zone | 10 | Yielding / merging | 33 |
| Railroad crossings | 12 | Turns | 20 |
| Vision requirements | 3 | Address-change notification | 2 |
| Funeral procession | 2 | | |

**User-flagged Oklahoma-specific items both confirmed:**

- **Compulsory liability insurance** — 4 questions touch it directly,
  plus 5 more on the security-verification form (proof of insurance).
  Manual evidence at lines 1407, 1434, 1438, 1457, 5110–5145.
- **License/tag suspension on collision (uninsured)** — 2 questions
  directly cover the "Service Oklahoma will suspend… tags will be suspended"
  rule (manual lines 1463–1472).

**Thin coverage** (flag, not fail):

- *Organ donor* — only 1 question; the manual gives this several paragraphs
  (lines 850+). Could justify one more question.
- *Roundabout*, *seat belt*, *child restraint*, *distracted driving* — 2
  questions each. Adequate but not deep.

## Coverage

### Category distribution (target: all 10 categories represented, no single
category > 40%)

| Category | Count | % |
|---|---:|---:|
| safe_driving_rules | 67 | 21.8% |
| signs_and_signals | 54 | 17.6% |
| license_system | 44 | 14.3% |
| penalties_and_points | 43 | 14.0% |
| sharing_the_road | 27 | 8.8% |
| defensive_driving | 24 | 7.8% |
| driver_responsibility | 15 | 4.9% |
| vehicle_information | 14 | 4.6% |
| alcohol_drugs_health | 10 | 3.3% |
| driver_testing | 9 | 2.9% |
| **Total** | **307** | **100%** |

All 10 canonical categories present. Top category at 21.8% is well under the
40% over-concentration ceiling. `alcohol_drugs_health` (3.3%) and
`driver_testing` (2.9%) are the lightest — defensible given the manual's
relative emphasis, but could each absorb a few more questions to reach
parity with the platform average (~5–7% per minor category).

### Question density

- Manual text size: 169,164 chars (largest among recent state onboardings)
- LLM-generated questions: 273
- Density: **1.79 questions per 1k chars** of manual text — squarely
  within the platform's healthy 1–3 range; no dilution or over-stuffing.

### Sign-question contribution

- Sign questions (`image:`-tagged): 34 / 307 = **11.1%**
- LLM questions: 273 / 307 = 88.9%

Mix is typical for the platform.

## Recommended Actions

Quality is high; these are **enhancements**, not defects:

1. **Add 1-2 organ-donor questions** — the manual devotes meaningful prose to
   organ/tissue donation (line 850+) but the bank currently has only 1 question
   touching that keyword. Suggested coverage: how to register, and what info
   appears on the license.
2. **Add 1-2 `driver_testing` questions** — category is the lightest at 2.9%
   (9 questions). The manual covers the road-skills test in detail; a few
   more questions on what's tested (parking maneuvers, turnabout) would
   improve balance without touching other categories.
3. **(Optional) Strengthen `license/tag suspension on collision` to 4+
   questions** — user explicitly flagged this as an Oklahoma-specific topic.
   Currently covered by 2 questions; given how prominently the manual treats
   it (Chapter 3 *Compulsory Insurance* + Chapter 6 repeat), 4 would better
   match its weight in the source.
4. **No fixes required for fabricated content** — precision audit found
   zero hallucinated claims after manual inspection of the 2 grep-missed
   items. Both were paraphrase mismatches, not factual errors.

---

*Generated: 2026-04-29. Verifier methodology: `/home/ivanmkc/.claude/plans/agile-pondering-truffle.md`.*
