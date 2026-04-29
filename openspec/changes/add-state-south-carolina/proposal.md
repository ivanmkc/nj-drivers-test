## Why

South Carolina is the seventh-largest unfinished state (~5.4M). The 2025-12 edition PDF is verified on `dmv.sc.gov` — note the catalog refresh moved away from the legacy `scdmvonline.com` URL that was on the documented allowlist exception list, in favor of the cleaner `.gov` host. This is the **first onboarding to validate the catalog refresh's host-allowlist rule** in practice (clean `.gov` host, no exception needed).

Thin per-state add — infrastructure lives in `refresh-manual-catalog`.

## What Changes

- Run the pipeline against the verified SC catalog entry: `setup_state.py --from-catalog sc` → `generate_questions.py` → `add_sign_questions.py` → `translate.py sc es`.
- Produce `data/states/sc/{config.json,questions_*.yaml}` grounded in the December 2025 South Carolina Driver's Manual.
- Audit, bundle, smoke test (30 questions, 80% pass).
- Update `SOURCES.md` and `TODO_JURISDICTIONS.md`.

## Capabilities

### New Capabilities
<!-- None. -->

### Modified Capabilities
<!-- None — adds a new state requirement under supported-states. -->

## Impact

- **Data**: new `data/states/sc/` directory.
- **Catalog**: none — already verified at the new `.gov` host.
- **Code**: none expected.
- **Depends on**: `refresh-manual-catalog` infrastructure landed.
- **Spot-check focus**: SC manual covers hurricane-evacuation procedures, contraflow-lane rules, and beach-driving statutes (Hilton Head, Myrtle Beach areas). These are SC-specific and should appear in the question bank if present in the manual.
