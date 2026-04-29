## Why

Michigan is the second-largest unfinished state by population (~10M). Beyond raw impact, MI is the **first real-world exercise of the multi-source manual pipeline** introduced by `refresh-manual-catalog` — the official manual is published as "What Every Driver Must Know" (Oct 2025 ed.) under an HTML index page on `michigan.gov/sos/resources/forms/what-every-driver-must-know`, with the full booklet PDF reachable via the catalog's `urls` list. Even though the catalog currently lists only the single full-booklet PDF (not chapter splits), this still validates the new `_manual_fetch.assemble_manual_text` code path end-to-end on a high-population state.

This change is intentionally a thin per-state add — the heavy lifting (URL verification, multi-source extraction, catalog hygiene) lives in `refresh-manual-catalog`. Once that lands, this change reduces to: run the pipeline, audit, bundle, smoke test, update docs.

## What Changes

- Run the existing pipeline against the verified MI catalog entry: `setup_state.py --from-catalog mi` (or equivalent) → `generate_questions.py` → `add_sign_questions.py` → `translate.py mi es`.
- Produce `data/states/mi/{config.json,questions_en.yaml,questions_es.yaml}` grounded in the WEDMK manual.
- Audit, bundle, and confirm MI appears with the right format (50 questions, 80% pass) on iOS, Android, and frontend.
- Update `SOURCES.md` and `TODO_JURISDICTIONS.md` (flip checkbox, update completion counts to 25/51).

## Capabilities

### New Capabilities
<!-- None — pure data addition under capabilities introduced by add-state-georgia and refresh-manual-catalog. -->

### Modified Capabilities
<!-- None — adds a new state requirement under supported-states; does not change spec-level behavior of any other capability. -->

## Impact

- **Data**: new `data/states/mi/` directory, ~300-500 questions (typical for state of MI's manual size).
- **Catalog**: no changes — entry already verified by `refresh-manual-catalog`.
- **Code**: none. If the multi-source path produces noisy text (repeated chapter headers, page-number garbage), document it as a follow-up rather than fixing inline.
- **Depends on**: `refresh-manual-catalog` infrastructure landed (multi-source `_manual_fetch.py`, catalog refresh).
- **Risk**: WEDMK is bilingual-coded (English on most pages but with multilingual references to other editions). The Gemini generator may try to produce questions about Spanish/Arabic editions of the manual itself — spot-check for this and discard such questions.
