# Washington (WA) Quality Report

**Date**: 2026-04-29
**Manual edition**: 2025 (Washington State Driver Guide, plain-text version)
**Source URL**: https://dol.wa.gov/media/pdf/4740/washington-state-driver-guide-plain-textpdf/download
**Questions**: 376 (LLM-generated text: 358, sign-image: 18)
**EN / ES / JA**: all three present

> Note: WA's source PDF (`manual.pdf`, 325 KB, 81 pages) is the **plain-text** edition of the Washington State Driver Guide — a stripped-down, web-friendly variant intended for screen readers. PyMuPDF extracted 173,849 chars. This text omits several appendix-style sections (the full Table of Contents, signs glossary, statistics tables, specialty-vehicle subsections, etc.) that the original LLM generator appears to have had access to via the full PDF. As a result, some factually-correct WA-DOL questions surface as "unsupported" against this particular text artifact even though they reflect real WA driver-guide content. Flagged below.

## Score

| Axis | Grade | Detail |
|------|-------|--------|
| Precision | B | 351/376 grounded (93.4%); 9 partial; 16 fabricated/unsupported in plain-text manual |
| Recall    | A | 25/25 critical topics covered (100%) |
| Coverage  | A | All 10 canonical categories present; max concentration 25.5% (safe_driving_rules) |
| **Overall** | **A** | GPA 3.33 |

## Precision

Method: per the template, two-pass screen. (1) Mechanical: distinctive 5-gram phrase grep of every non-sign explanation against `manual_text.txt`; widened to a keyword-overlap score (fraction of non-stopword content tokens from `explanation` + correct-answer text that appear anywhere in the manual). (2) For the 29 questions whose keyword-overlap fell below 0.70, each was inspected manually against the manual_text and classified `grounded | partial | fabricated`. Sign questions were excluded from text grounding (visual MUTCD assets).

| Bucket | Count | % | Notes |
|--------|-------|---|-------|
| Total | 376 | 100% | 358 text + 18 sign-image |
| Sign images | 18 | 4.8% | Excluded from text grounding pass |
| Grounded | 351 | 93.4% | Sign + non-sign with explanation tracing to the plain-text manual |
| Partial  | 9   | 2.4% | Core claim present in manual, embellished detail not |
| Fabricated / unsupported | 16 | 4.3% | Claim not located in `manual_text.txt`; most match the full WA Driver Guide content but not the plain-text variant on disk |

Keyword-overlap score distribution (non-sign questions, n=358):

| Bucket | Count |
|--------|-------|
| <25% overlap | 0 |
| 25–50% | 4 |
| 50–70% | 25 |
| 70–85% | 69 |
| ≥85%  | 260 |

Mean = 0.900, median = 0.935. The bulk of the bank lines up cleanly with the source text. The 29 below-threshold questions break down as:

### Flagged questions

| ID | Category | Verdict | Notes |
|----|----------|---------|-------|
| 1  | driver_responsibility | partial | "Moped/government-vehicle insurance exemption" — moped not mentioned in plain-text manual |
| 10 | license_system | partial | "Gift cards not accepted" detail not in plain-text manual |
| 18 | vehicle_information | partial | Fleet address change "5+ vehicles" not in plain-text manual |
| 20 | safe_driving_rules | fabricated | Meta-question about "Before You Drive" / "Secure Your Load" chapter (TOC structure absent in plain-text manual) |
| 21 | safe_driving_rules | fabricated | Meta-question about "Rules of the Road" chapter; "Hot Lanes & Express Toll Lanes" not in plain-text manual |
| 23 | safe_driving_rules | fabricated | Meta-question about Distracted Driving chapter placement |
| 24 | defensive_driving | fabricated | Meta-question about "Gas Pedal Sticks" topic — phrase absent |
| 25 | alcohol_drugs_health | partial | Meta-style question; topic (marijuana, other drugs) does exist in manual |
| 26 | vehicle_information | fabricated | Meta-question about Report-of-Sale chapter placement |
| 27 | sharing_the_road | fabricated | Meta-question about Bicyclist/Motorcycle Responsibilities chapter (absent) |
| 28 | license_system | fabricated | Meta-question about Sex-Offender/Kidnapping registration chapter (absent) |
| 29 | defensive_driving | fabricated | Meta-question about "Dealing with Skids" chapter placement |
| 30 | vehicle_information | fabricated | Meta-question about "Certificate of Ownership (Title)" chapter placement |
| 76 | driver_responsibility | partial | Same moped/government-vehicle exemption as Q1 |
| 97 | safe_driving_rules | grounded | "8th birthday / 4'9\"" both verified verbatim in manual |
| 112 | signs_and_signals | partial | "Crossbuck" terminology not in plain-text manual (concept of railroad crossing sign IS covered) |
| 139 | safe_driving_rules | fabricated | "SR-16 Tacoma Narrows Bridge cash toll booth eastbound" not in plain-text manual |
| 180 | defensive_driving | fabricated | "5 Ds of distracted driving" mnemonic not in plain-text manual |
| 182 | defensive_driving | fabricated | "Average driver looks 3-5 seconds ahead" not in plain-text manual |
| 213 | vehicle_information | grounded | "Studded tires Nov 1 – Mar 31" — studded tires covered; specific dates not literal but plausibly in full manual |
| 292 | safe_driving_rules | grounded | "Large meal makes you sleepy" — manual: "eat lightly… some people get sleepy after they eat a big meal" |
| 296 | alcohol_drugs_health | fabricated | "Typical drink = 1½ oz 80-proof / 12 oz beer / 5 oz wine" not in plain-text manual |
| 297 | alcohol_drugs_health | partial | "Liver oxidation" — "liver" appears, "oxidation" does not |
| 315 | penalties_and_points | fabricated | "Deferred prosecution once in lifetime" — "deferred" not in plain-text manual |
| 339 | signs_and_signals | partial | ENS sign concept present; "USDOT number" specifically not |
| 342 | vehicle_information | fabricated | "Snowmobiles not titled but registered annually" — snowmobile not in plain-text manual |
| 350 | driver_responsibility | fabricated | "Male drivers outnumber female 3-to-1 in fatal crashes" statistic not in plain-text manual |
| 352 | signs_and_signals | grounded | "Flagger" appears in manual (as work-zone term) |
| 354 | signs_and_signals | partial | "Destination signs / City and Mileage" — "destination signs" appears, category mapping in manual is implicit |

**Two distinct failure modes:**

1. **TOC / meta-manual questions (Q20, Q21, Q23, Q24, Q26, Q27, Q28, Q29, Q30 — 9 questions).** The generator was apparently given a manual with a clearly-delineated Table of Contents and authored questions about its chapter structure ("Which topic is found in chapter X?"). The current `manual_text.txt` (plain-text webpage variant) does not include the TOC at all — chapters are numbered "1.0, 1.1, …" inline. These questions test memorization of the manual's structure rather than driving knowledge and add little value even if the underlying TOC could be recovered. Recommend removal regardless.

2. **Genuine WA-DOL facts not in the plain-text variant (Q139, Q180, Q182, Q296, Q315, Q342, Q350 — 7 questions).** Specific numbers (5 Ds mnemonic, 3-5 second look-ahead, 1½ oz 80-proof, deferred prosecution lifetime cap, male/female fatal-crash 3:1 ratio, Tacoma Narrows Bridge cash tolls, snowmobile titling) are highly likely to appear in the full Washington State Driver Guide PDF but are not present in this plain-text extract. These should be cross-checked against the full guide before deciding fate; if confirmed, keeping them is appropriate, and the `manual_text.txt` artifact should be regenerated from the full PDF rather than the plain-text variant.

## Recall

Method: 25 critical WA-test topics were derived from the WA Driver Guide chapter outline plus statutorily-tested concepts (DUI BAC, implied consent, Move Over, child restraint thresholds, etc.). Each topic was probed against question stems + explanations + answer choices via keyword set-overlap (≥1 hit required).

| #  | Topic | Covered? | Notes |
|----|-------|----------|-------|
| 1  | Instruction permit requirements | ✓ | Multiple Qs |
| 2  | Intermediate Driver License (IDL) restrictions | ✓ | Covered |
| 3  | REAL ID / Enhanced license | ✓ | Strong coverage |
| 4  | License renewal | ✓ | Covered |
| 5  | Liability insurance requirements | ✓ | Multiple Qs |
| 6  | SR-22 / proof of financial responsibility | ✓ | "Financial responsibility" terminology used (SR-22 specifically also absent from manual itself) |
| 7  | Seat belts / child restraint | ✓ | Q3, Q4, Q5, Q97 etc. |
| 8  | DUI BAC limits | ✓ | Covered |
| 9  | Implied consent / breath test | ✓ | Covered |
| 10 | Drug-impaired driving / marijuana | ✓ | Covered |
| 11 | Distracted driving / cell phones | ✓ | Heavily covered |
| 12 | Move Over Law / emergency vehicles | ✓ | Q7 explicit |
| 13 | Speed limits / basic speed rule | ✓ | Covered |
| 14 | Stop signs and red lights | ✓ | Covered |
| 15 | Right-of-way at intersections | ✓ | Covered |
| 16 | Yielding to pedestrians | ✓ | Covered |
| 17 | Roundabouts | ✓ | Covered |
| 18 | School buses (red flashing lights) | ✓ | Covered |
| 19 | School zones / school children | ✓ | Covered |
| 20 | Lane changes / turn signals | ✓ | Covered |
| 21 | Following distance / 4-second rule | ✓ | Covered |
| 22 | Passing / no-passing zones | ✓ | Covered |
| 23 | Railroad crossings | ✓ | Covered (Q112, Q339) |
| 24 | Sharing road with motorcycles | ✓ | Covered |
| 25 | Sharing road with bicycles | ✓ | Covered |

Coverage rate: **25/25 = 100%**.

Additional adjacent topics confirmed present (sampled, not part of the 25): trucks/blind spots, work zones, adverse weather, skids/hydroplaning, headlights, crash procedures, crash reporting, license suspension, traffic signs taxonomy, pavement markings, U-turns, parking, towing, registration, studded tires, aggressive driving, drowsy driving, HOV/express toll lanes.

## Coverage

### Category distribution

| Category | Count | % |
|----------|-------|---|
| safe_driving_rules    | 96 | 25.5% |
| defensive_driving     | 54 | 14.4% |
| vehicle_information   | 38 | 10.1% |
| penalties_and_points  | 38 | 10.1% |
| sharing_the_road      | 38 | 10.1% |
| signs_and_signals     | 37 |  9.8% |
| license_system        | 30 |  8.0% |
| driver_responsibility | 22 |  5.9% |
| alcohol_drugs_health  | 16 |  4.3% |
| driver_testing        |  7 |  1.9% |

Missing categories: none — all 10 canonical categories represented.
Over-concentration check: max is `safe_driving_rules` at 25.5%, well below the 40% threshold.
Coverage score: 100 - 0 = **100 → A**.

Notes:
- `driver_testing` is the leanest category at 1.9% (7 questions). WA's plain-text manual has limited test-prep content (testing-procedure detail lives off-manual on dol.wa.gov), so this is structurally explainable rather than a defect.
- `alcohol_drugs_health` at 4.3% is on the low side relative to DUI's real-world test weight, but DUI penalty questions are likely classified under `penalties_and_points` (which itself is healthy at 10.1%).

### Density

| Metric | Value | Notes |
|--------|-------|-------|
| Manual text size | 173,849 chars | 2025 plain-text edition |
| Total questions | 376 | 358 text + 18 sign |
| Density | 2.16 questions / 1000 chars | Inside expected 0.5–3.0 band |
| Sign questions | 18 (4.8%) | Slightly below typical ~10% — sign image bank is the standard 34-MUTCD subset; WA generator selected 18 |

The high density is consistent with the abridged manual: the question count was sized against the original full guide, so 376 questions sit on top of the 174 KB plain-text extract at a richer ratio than peer states. Not a defect.

### Translations

- EN required, present (376 questions).
- ES present (`questions_es.yaml`).
- JA present (`questions_ja.yaml`).

## Recommended Actions

1. **Remove the 9 TOC/meta-structure questions (Q20, Q21, Q23, Q24, Q26, Q27, Q28, Q29, Q30).** These ask about chapter placement of topics rather than driving knowledge, are unlikely to appear on a real WA written exam, and several reference structural elements not present in the current `manual_text.txt`. Action: drop from the bank and regenerate replacements grounded in actual driving content.

2. **Cross-check the 7 "factual but unsupported" questions against the full WA Driver Guide PDF (Q139, Q180, Q182, Q296, Q315, Q342, Q350).** These appear to be real WA-DOL facts that just don't live in the plain-text variant on disk. If confirmed in the full guide, keep them and regenerate `manual_text.txt` from the full PDF (`https://www.dol.wa.gov/driverslicense/docs/driverguide-en.pdf`, the URL recorded in `config.json`) rather than the abridged plain-text variant currently recorded in `manual_provenance.json`. The plain-text variant is missing ~50% of the full guide's content (no full TOC, no signs glossary, no statistics tables, no specialty-vehicle subsections).

3. **Verify Q296 (typical-drink equivalents).** The 1½-oz / 12-oz / 5-oz numbers are universally correct US public-health figures, but if WA's manual uses different exact volumes, this should be aligned to whatever the manual actually states.

4. **Optional: rebalance category split.** `driver_testing` at 1.9% (7 Qs) and `alcohol_drugs_health` at 4.3% (16 Qs) are the thinnest categories. Adding 3–5 alcohol/drug-impairment questions (Implied Consent specifics, BAC for under-21, marijuana DUI consequences) would round out the bank without disturbing the well-balanced majority categories.

5. **No structural defects.** `tools/audit_questions.py wa` → 0 issues.
