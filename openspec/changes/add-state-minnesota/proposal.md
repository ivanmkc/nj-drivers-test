## Why

Minnesota is the sixth-largest unfinished state (~5.7M). The 2025-05 edition PDF is verified on `assets.dps.mn.gov`, single-source. The MN manual has notable winter-driving content (black ice, skid recovery, snow-emergency rules, ice-fishing road-use exceptions) — like Colorado's mountain content, this exercises the LLM on conditions-specific material that benefits from grounded source citations.

Thin per-state add — infrastructure lives in `refresh-manual-catalog`.

## What Changes

- Run the pipeline against the verified MN catalog entry: `setup_state.py --from-catalog mn` → `generate_questions.py` → `add_sign_questions.py` → `translate.py mn es`.
- Produce `data/states/mn/{config.json,questions_*.yaml}` grounded in the 2025 Minnesota Driver's Manual.
- Audit, bundle, smoke test (40 questions, 80% pass).
- Update `SOURCES.md` and `TODO_JURISDICTIONS.md`.

## Capabilities

### New Capabilities
<!-- None. -->

### Modified Capabilities
<!-- None — adds a new state requirement under supported-states. -->

## Impact

- **Data**: new `data/states/mn/` directory.
- **Catalog**: none — already verified.
- **Code**: none expected.
- **Depends on**: `refresh-manual-catalog` infrastructure landed.
- **Spot-check focus**: winter-driving questions (skid recovery, snow emergencies, snowplow distance laws) must cite specific manual sections. MN is also one of the few states with statutory rules around snowmobile/ATV road-use; verify those aren't omitted.
