# Quality Verification — Massachusetts (MA)

- **State**: Massachusetts
- **Agency**: RMV
- **Manual source (declared)**: Massachusetts Driver's Manual — https://www.mass.gov/doc/english-drivers-manual/download
- **Manual edition**: *(not recorded — `manual_provenance.json` `edition` field is empty)*
- **Manual PDF on disk**: **MISSING** (`data/states/ma/manual.pdf` does not exist)
- **Manual extracted text on disk**: **MISSING** (`data/states/ma/manual_text.txt` does not exist)
- **Question bank**: `data/states/ma/questions_en.yaml` — 456 questions (EN + ES)
- **Provenance note**: `URL https://www.mass.gov/doc/english-drivers-manual/download returned HTTP 403 (Akamai bot challenge) on 2026-04-29; mass.gov blocks programmatic downloads; pre-existing question bank retained from prior onboarding` (`manual_provenance.json` → `pdf.recovered: false`)

## Score

**INCOMPLETE — source manual not recovered.**

Precision and recall cannot be measured for MA because the verification methodology (`docs/quality` plan, sections "Precision pass" and "Recall pass") requires `manual_text.txt` as the grounding corpus. That file is absent because the canonical Mass.gov download URL is gated by an Akamai bot-protection layer that returned HTTP 403 to the recovery backfill on 2026-04-29 (see `manual_provenance.json` `note`). The question bank itself was preserved from an earlier onboarding run, but the source-of-truth text it was generated against is no longer reproducible from this repo.

No letter grade is assigned. The state should be treated as **unverified** until the manual is re-fetched (see Recommended Actions).

## Precision

**Not measurable.** Precision in this methodology = "% of question explanations whose distinctive 4–6-word phrases match the manual text, plus LLM-judge adjudication on the remainder." Both halves of that test require `manual_text.txt`, which is absent. No grep pass and no Gemini grounding pass were performed; reporting a precision number here would be fabricated.

What *is* known about the question bank's surface form (from `tools/audit_questions.py` structural checks):

| Metric | Value |
|---|---|
| Total questions | 456 |
| Questions with non-empty `explanation` | 456 / 456 (100%) |
| Sign-image questions (`image:` field) | 18 |
| Structural audit (`audit_questions.py ma`) | 0 issues |

These say the bank is internally well-formed; they say nothing about whether claims like fines, ages, BAC limits, distances, or rule citations match the current Massachusetts RMV manual.

## Recall

**Not measurable.** Recall in this methodology = "fraction of the 25 critical topics Gemini extracts from `manual_text.txt` that appear in `questions_en.yaml`." With no manual text, there is no topic list to score against, and no way to detect omissions (e.g., MA-specific Junior Operator License rules, MA's specific BAC thresholds, or MA's "right-of-way at rotaries" guidance) without risking LLM-knowledge fabrication — exactly the failure mode the critical rule in `CLAUDE.md` forbids ("Never generate questions from LLM knowledge alone").

## Coverage

Coverage *can* be partially reported — it depends only on the YAML, not the manual.

**Category distribution (456 questions):**

| Category | Count | % |
|---|---:|---:|
| safe_driving_rules | 102 | 22.4% |
| penalties_and_points | 71 | 15.6% |
| license_system | 60 | 13.2% |
| sharing_the_road | 48 | 10.5% |
| signs_and_signals | 42 | 9.2% |
| driver_testing | 34 | 7.5% |
| defensive_driving | 31 | 6.8% |
| driver_responsibility | 29 | 6.4% |
| vehicle_information | 24 | 5.3% |
| alcohol_drugs_health | 15 | 3.3% |

- **All 10 canonical categories present.** No missing categories.
- **No over-concentration.** Largest bucket (`safe_driving_rules` at 22.4%) is well under the 40% threshold flagged in the plan.
- **Underweight bucket worth a look:** `alcohol_drugs_health` at 3.3% is roughly half the next-smallest category. For a US jurisdiction with strict OUI/Melanie's Law statutes, ~15 questions feels light. (Cannot confirm without the manual.)
- **Sign questions:** 18 image-tagged questions — in line with the other 34-state cohort.
- **Question count vs manual size:** **not computable** (no `manual_text.txt` char count).
- **Question count vs cohort:** 456 sits comfortably in the cohort range (202–874); MA is in the upper-middle for question volume.

## Recommended Actions

Listed in priority order. None are blocking for ship — the bank still passes `audit_questions.py` and renders correctly — but none of them are optional if MA should carry the same verification guarantee as the other 33 merged states.

1. **Re-recover the manual** (unblocks everything else). Options, in order of preference:
   - Manual download via a browser session (Akamai cookie present) and commit the PDF to Git LFS as `data/states/ma/manual.pdf`.
   - Use a recovery script with a real User-Agent + cookie-jar that survives the Akamai challenge.
   - Fall back to a mirror: the RMV occasionally posts a static-CDN copy; the Internet Archive snapshot of `mass.gov/doc/english-drivers-manual/download` may also work.
   - As a last resort, source the manual from a non-Mass.gov but RMV-affiliated channel (e.g., the AAA-distributed reprint) and record the alternate provenance in `manual_provenance.json`.
2. **Re-run extraction**: once the PDF lands, run the standard PyMuPDF extraction to produce `manual_text.txt`, update `manual_provenance.json` (`edition`, `extracted_with`, `pdf.recovered: true`, `text.sha256`, etc.).
3. **Re-run this verifier**: with `manual_text.txt` in place, the precision / recall passes become possible and this report should be replaced with a graded one.
4. **Sanity-check `alcohol_drugs_health` coverage** after the manual is back, focusing on Massachusetts-specific items (Melanie's Law, ignition-interlock thresholds, 24D disposition, .02 limit for under-21). If those facts are missing from the bank, regenerate the category against the recovered manual.
5. **Fill in `config.json` and `manual_provenance.json` metadata**: `edition` is empty and the provenance `sources: []`. Once the new manual is fetched, populate both.
6. **Do not regenerate questions blindly from LLM knowledge.** Per `CLAUDE.md` ("All questions must be grounded in official state driver manuals"), any regeneration must happen *after* the manual is recovered, not before.
