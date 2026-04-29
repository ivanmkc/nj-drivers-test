## Why

Arizona is the fourth-largest unfinished state (~7.5M). The catalog has a verified 2025 PDF on `apps.azdot.gov`, single-source, no multi-PDF complications. AZ is the cleanest of the high-ROI single-PDF candidates, making it a good Wave-1 anchor: if the post-refresh-manual-catalog pipeline can't produce a clean question bank for AZ, something's wrong with the tooling, not the state.

This change is a thin per-state add — heavy lifting lives in `refresh-manual-catalog`.

## What Changes

- Run the pipeline against the verified AZ catalog entry: `setup_state.py --from-catalog az` → `generate_questions.py` → `add_sign_questions.py` → `translate.py az es`.
- Produce `data/states/az/{config.json,questions_*.yaml}` grounded in the 2025 Arizona Driver License Manual.
- Audit, bundle, smoke test (50% / 30 questions, 80% pass).
- Update `SOURCES.md` and `TODO_JURISDICTIONS.md` (flip checkbox, update count).

## Capabilities

### New Capabilities
<!-- None — pure data addition. -->

### Modified Capabilities
<!-- None — adds a new state requirement under supported-states. -->

## Impact

- **Data**: new `data/states/az/` directory.
- **Catalog**: none — already verified.
- **Code**: none expected. AZ is the canonical single-PDF happy path.
- **Depends on**: `refresh-manual-catalog` infrastructure landed.
- **Note on AZ-specifics**: the manual emphasizes desert/mountain driving (dust storms, runaway truck ramps) — verify generated questions don't conflate with similar Nevada/New Mexico content if the LLM has seen those manuals.
