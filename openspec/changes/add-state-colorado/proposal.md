## Why

Colorado is the fifth-largest unfinished state (~5.9M). The 2025-01 edition PDF is verified on `dmv.colorado.gov`, single-source. CO is interesting beyond population: the manual has substantial mountain/altitude/snow-driving content (chain laws, runaway-truck ramps, brake-fade rules) that few other state manuals cover in depth — this stresses the LLM generator on technical content rather than generic rules-of-the-road.

Thin per-state add — infrastructure lives in `refresh-manual-catalog`.

## What Changes

- Run the pipeline against the verified CO catalog entry: `setup_state.py --from-catalog co` → `generate_questions.py` → `add_sign_questions.py` → `translate.py co es`.
- Produce `data/states/co/{config.json,questions_*.yaml}` grounded in the 2025 Colorado Driver Handbook (DR 2337).
- Audit, bundle, smoke test (25 questions, 80% pass).
- Update `SOURCES.md` and `TODO_JURISDICTIONS.md`.

## Capabilities

### New Capabilities
<!-- None. -->

### Modified Capabilities
<!-- None — adds a new state requirement under supported-states. -->

## Impact

- **Data**: new `data/states/co/` directory.
- **Catalog**: none — already verified.
- **Code**: none expected.
- **Depends on**: `refresh-manual-catalog` infrastructure landed.
- **Spot-check focus**: ensure mountain/altitude/chain-law questions cite specific manual sections, not generic safe-driving rules. CO is one of only a few states where these are mandatory test content.
