# Persona UX Study: Drivers-Test App Comprehension (Gemini 3.1 Pro)

**Date:** 2026-08-09 · **Surface:** deployed frontend (https://ivanmkc.github.io/nj-drivers-test/) · **Method:** agentic-persona structured Q&A scored against ground truth (gemini-ux-study methodology)

## Method

- 4 personas, each with a realistic goal, device, theme, and state; 14 screenshots captured from the **live deployed site** via Playwright (`studies/capture_personas.py`)
- Each persona received their full flow's screenshots in order plus 5–7 questions, answered in character by `gemini-3.1-pro-preview` at temperature 0.1 with JSON output (`studies/run_persona_study.py`, raw answers in `studies/answers/`)
- Factual answers scored against encoded ground truth (config values, manual passages, verification reports, and my own reading of the fixtures); open-ended answers mined for findings
- Hallucination (inventing UI that doesn't exist) tracked as its own bucket

| Persona | Profile | Device / theme | State | Focus |
|---|---|---|---|---|
| Jordan | 17, first-time learner | mobile, light | NJ | test-format facts, affordances, feedback |
| María | 34, Spanish speaker, limited English | mobile, light, app in ES | NV | official-test-language comprehension, localization |
| Ken | 68, prefers dark mode, low-vision tendencies | desktop, dark | WY | trust info, results/stats, readability |
| Aisha | 29, skeptical data journalist | desktop, dark | CA | evidence, verification claims, no-claim handling |

## Score table

| Persona | Factual correct | Partial | Wrong | Hallucinated | Confidence |
|---|---|---|---|---|---|
| Jordan | 6/6 | 0 | 0 | 0 | high |
| María | 5/5 | 0 | 0 | 0 | high |
| Ken | 5/5 | 0 | 0 | 0 | high |
| Aisha | 4/4 | 0 | 0 | 0 | high |
| **Total** | **20/20 (100%)** | 0 | 0 | **0** | high |

Every persona correctly extracted: pass conditions (NJ 50/40/80%, WY 25/20/80%), weak-spots affordance, answer feedback semantics (✓/✕ + explanation + manual quote), source attribution and how to independently verify it, official-test-language seals (NJ Spanish ✓, NV Japanese ✗ practice-only, WY English-only, CA explicit no-claim), results pass/fail, and stats state. Zero invented UI.

## What works (evidence-backed)

- **Pass conditions land instantly** — every persona quoted the "Real test: N questions, M correct to pass (X%)" line verbatim.
- **The official-test-language system is fully comprehensible** — María correctly concluded she can take the real NV test in Spanish but not Japanese, citing the seal, the localized caption, and the About row; Aisha praised CA's "surprisingly transparent" no-claim disclaimer.
- **Trust chain reads end-to-end** — all personas found the source link, verification badges, and per-question manual quotes; Aisha (professional skeptic) rated the verbatim citations and category transparency as trust-increasing.
- **Answer feedback is unambiguous** — icon + color + counter + explanation + quote were all parsed correctly; pass/fail on results is text, not color-only.

## Findings → recommendations

**P1 — Spanish localization gaps (María).** With the app in ES, these remain English: the "About this test" header and internals, category names everywhere ("PENALTIES AND POINTS" chip, CATEGORIES breakdown), the "All" count button, and "Exit". María: *"It makes me feel like I'm missing important context."* The core LEP audience hits this on every screen. → Localize the About header/labels and the `All`/`Exit` strings; add localized display names for the 10 categories (a small static map — categories are a fixed enum).

**P1 — Stats "Accuracy by Category: Unknown" (fixture observation).** The stats screen shows a single category literally labeled "Unknown" at 0% — the per-question category isn't reaching the frontend store's records. Also the 0% average score renders in success-green. → Fix category recording in the store write path; make avg-score color severity-aware.

**P2 — Manual quotes are English-only for ES users (María).** By design (evidence is verbatim), but unlabeled: María can't read the one element meant to build her trust. → Keep the verbatim EN quote, add a localized label ("Cita del manual oficial (en inglés)") so it reads as intentional rather than broken.

**P2 — Category rows look tappable but aren't (Jordan).** First instinct was to tap "Signs And Signals (43)" to practice that category; no per-category practice exists. → Either add category-filtered practice mode (natural extension of the Weak Spots mode) or visually de-emphasize the rows as read-only.

**P2 — Verification metrics lack a methodology reference (Aisha).** "Grade A / Fidelity 9.95/10" impressed but she'd "challenge metrics that lack any visible methodology." → Add a one-line info affordance linking to a short method note (the verification pipeline is documented in-repo; expose a plain-language summary).

**P3 — Muted-text readability for older users (Ken).** The 12px gray captions (checkmark note, About sub-notes, missed-question explanations on results) were the hardest to read. → Raise the smallest muted text one step and/or use the higher-contrast gray token; longer-term, respect platform text-scaling.

**P3 — No back-to-previous-question in quiz (Jordan).** Noted as missing; current design is forward-only with review-at-results. Document as intentional or add back-navigation within a session.

**Model artifact (not a finding):** Aisha flagged "Verified Jul 26, 2026" as a suspicious *future* date — the model's clock, not the UI; the date is in the past. Kept here for honesty about the method's limits.

## Fixture gaps (honest accounting)

- No persona exercised: results after a *passing* quiz, the JA/FR UI languages, the state-picker search field, offline/error states, or the web (Flask) surface. Recommended follow-up fixtures if a v2 study runs.
- Ken's "large text" preference was simulated by persona framing only — a real `Dynamic Type`/browser-zoom fixture would test L-category properly.

## Artifacts

- `studies/capture_personas.py` — Playwright capture (live site)
- `studies/screenshots/*.png` — 14 fixtures (4 personas × flows)
- `studies/run_persona_study.py` — persona Q&A runner (gemini-3.1-pro-preview)
- `studies/answers/*.json` — raw in-character answers with confidence

## Aggregated comprehension score: 20/20 (100%)

The recent UX work (trust info, language seals, dark mode, feedback icons) is fully comprehensible to all four personas. The remaining work is not comprehension — it's the localization completeness and polish items above.
