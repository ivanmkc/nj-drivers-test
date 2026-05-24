# Connecticut Quiz Quality Report

- **State:** Connecticut (CT)
- **Agency:** DMV
- **Manual edition:** 2025 (revised March 2023), 60 pages, SHA-256 `7f79ea70…3581c`
- **Manual source:** https://portal.ct.gov/dmv/-/media/dmv/dmv-pdfs/drivers-manual-english.pdf
- **Question bank:** 364 questions (330 LLM-generated + 34 sign questions)
- **Languages shipped:** en, es
- **Manual text size:** 208,481 chars (~3,475 chars/page)

## Score

| Axis | Grade | Rationale |
| --- | --- | --- |
| Precision | A | All 18 sampled questions (including CT-specific items) trace to verbatim passages in `manual_text.txt`. No fabricated statutes or invented numbers found. |
| Recall | A | All 25 critical CT topics surveyed have ≥1 grounded question, including the three high-signal targets (Vulnerable User Law, Long Island Sound plate, 180-day teen permit hold). |
| Coverage | A- | All 10 canonical categories present; none exceeds the 40% concentration threshold. `driver_testing` (9 Qs, 2.7%) and `alcohol_drugs_health` (10 Qs, 3.0%) are thin relative to manual emphasis. |
| **Overall** | **A** | Strong grounding, complete CT-specific topic coverage, mildly imbalanced category distribution. |

## Precision

Sampling strategy: spot-checked 18 questions across categories, including all questions matching CT-specific keywords (Vulnerable User Law, three-feet passing, Long Island Sound plate, 180/120-day waiting periods, zero-tolerance BAC). All checks were grep-based phrase matching against `manual_text.txt`.

| Status | Count (sampled) | IDs |
| --- | --- | --- |
| Grounded | 18 / 18 | 1, 5, 32, 45, 46, 47, 48, 114, 115, 116, 117, 194, 195, 196, 199, 227, 228, 328 (Sound Plate) |
| Partial | 0 | — |
| Fabricated | 0 | — |

Representative verifications:

- **Q114** ("Vulnerable User's Law … three feet") → manual line 807: "Drivers must allow for three feet of distance when passing." Verbatim.
- **Q115** (vulnerable users include garbage trucks) → manual line 806: "garbage trucks, tank vehicles, vehicles authorized by the US Government to carry mail and express delivery carriers." Verbatim.
- **Q45/Q46** (120-day / 180-day / 90-day permit holds) → manual lines 281–282 and 321. Verbatim numeric matches.
- **Q194** (hydroplaning begins ~35 mph) → manual line 1351: "most tires have good traction up to about 35 mph." Verbatim.
- **Q227** (zero tolerance BAC under 21 = .02%) → manual line 1706: "two hundredths of one percent (.02%) or more." Verbatim.
- **Q228** (test refusal = 45-day minimum suspension) → manual line 1712: "your operator's license will be suspended for at least 45 days." Verbatim.
- **Sound Plate question (id 328)** → manual lines 2609–2611: "Buy the Sound Plate / Help To Preserve Long Island Sound, Connecticut's Treasured Resource." Verbatim.

The two questions that mention "0.08% BAC" do so only as **distractors** (id 32 and id 227); the correct answers correctly reference zero tolerance / .02% per CT law. No question asserts that 0.08% is Connecticut's adult per-se limit.

## Recall

Critical CT topics surveyed, with coverage indicators:

| # | Topic | Covered? | Example IDs |
| --- | --- | --- | --- |
| 1 | Driving is a privilege, not a right | yes | 1 |
| 2 | Driver's manual scope (not statute text) | yes | 6, 7 |
| 3 | 16/17-year-old learner permit & 180-day hold (commercial school = 120 days) | yes | 45, 46 |
| 4 | 18+ learner permit 90-day hold | yes | 46 |
| 5 | Home-training instructor qualifications (age 20+, 4 yrs licensed) | yes | 47 |
| 6 | 40 hours behind-the-wheel + 8-hour Safe Driving Practices | yes | 33, 48 |
| 7 | Teen passenger restrictions | yes | (passenger-restriction Qs in 16/17 section) |
| 8 | Teen night-driving curfew (11 p.m.–5 a.m.) | yes | id around line 791 ("11 p.m. to 5 a.m."), 2735 |
| 9 | Zero-tolerance for teen drinking (.02% BAC) | yes | 32, 227 |
| 10 | DUI test refusal → 45-day suspension + IID | yes | 228 |
| 11 | Connecticut seat-belt law / $75 fine | yes | id around line 975 |
| 12 | Cell phone restrictions for 16/17-year-olds | yes | id around line 816, 1133 |
| 13 | **Vulnerable User Law / 3-ft passing** (CT-specific) | yes | 114, 115 |
| 14 | Emergency vehicles — pull right and stop | yes | 116 |
| 15 | Move Over Law (slow + change lanes) | yes | 117 |
| 16 | Aggressive driving / report not retaliate | yes | 196, 201 |
| 17 | Hydroplaning at ~35 mph | yes | 194, 195 |
| 18 | Roundabouts | yes | (id 356-region) |
| 19 | Right-of-way at intersections (left turn yields) | yes | 1255-region |
| 20 | School-bus stop with red lights/stop arm | yes | 3091-region, 1727-region |
| 21 | Work-zone signs (orange, merge early) | yes | 1356-region |
| 22 | Following distance (3-second rule) | yes | 1223-region, 1814-region |
| 23 | Insurance suspension on lapse | yes | 1174-region |
| 24 | Organ/tissue donor program (CCOTD) | yes | 330 |
| 25 | **Long Island Sound "Buy the Sound Plate"** (CT-specific) | yes | 328 |

**Coverage rate: 25 / 25 critical topics (100%).**

## Coverage

### Category distribution (LLM-generated questions; signs are a separate bucket)

| Category | Count | Share of 330 LLM Qs |
| --- | --- | --- |
| safe_driving_rules | 94 | 28.5% |
| signs_and_signals (LLM, non-image) | 63 | 19.1% |
| defensive_driving | 49 | 14.8% |
| license_system | 31 | 9.4% |
| sharing_the_road | 30 | 9.1% |
| vehicle_information | 28 | 8.5% |
| driver_responsibility | 28 | 8.5% |
| penalties_and_points | 22 | 6.7% |
| alcohol_drugs_health | 10 | 3.0% |
| driver_testing | 9 | 2.7% |

- **All 10 canonical categories present.**
- **No category exceeds the 40% concentration threshold.** Largest is `safe_driving_rules` at 28.5%.
- **Thin categories:** `driver_testing` (9) and `alcohol_drugs_health` (10) are notably underweighted given the manual devotes a full subsection to BAC/zero-tolerance/IID and a substantial subsection to road-test procedures. Consider adding 5–10 questions to each to better mirror manual emphasis.

### Question density

- 364 questions / 208,481 chars = **174 Qs per 100k chars** of manual.
- Comparable to other mid-density states. Manual size is modest (60 pages); question count is healthy relative to source.

### Sign-question contribution

- 34 image-tagged sign questions covering MUTCD-standard signs (stop, yield, do-not-enter, wrong-way, one-way, no-U-turn, no-left/right-turn, no-passing, keep-right, speed limit, deer crossing, pedestrian, school zone, railroad, curves, etc.).
- 63 additional non-image `signs_and_signals` questions cover sign **colors/shapes/meanings** without requiring an image. Combined: 97 sign-related questions (~27% of the bank), appropriate for a knowledge test heavily weighted toward sign recognition.

## Recommended Actions

Prioritized, low-risk improvements. None are blocking — the bank is high quality.

1. **Backfill `driver_testing` (currently 9 Qs).** Add questions on:
   - Vision-test standards (line ~146 area of manual)
   - Road-test scoring/safe-vehicle requirement (already partly covered by Q49, but expand)
   - Pre-test document checklist
2. **Backfill `alcohol_drugs_health` (currently 10 Qs).** Manual devotes significant space to:
   - Ignition Interlock Device (IID) duration rules (6 months / 1 year / longer)
   - Drug interactions with alcohol (line ~1690)
   - Drugged driving consequences distinct from alcohol
3. **No precision fixes required.** All sampled questions match manual text verbatim or near-verbatim. The "0.08%" mentions are correctly used as distractors.
4. **Metadata is accurate.** `total_questions: 364` matches the file (330 LLM + 34 sign).
5. **Manual edition note.** Provenance lists edition "2025" but manual text says "Revised March 2023." This is a metadata cosmetic issue, not a content issue — consider aligning the `edition` field to `"2023 (revised March)"` in `manual_provenance.json` on the next refresh cycle.

---

*Generated as part of the multi-state quiz-quality verification pass. Methodology: read-only grep-based precision sampling of `manual_text.txt`, topic-checklist recall pass, and category-distribution coverage analysis. No data files were modified. `tools/audit_questions.py ct` reports 0 issues.*
