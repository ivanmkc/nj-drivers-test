## Why

Georgia is the largest unfinished state by population (~11M residents) and has a distinctive test format (40 questions, 75% pass) that exercises the bundle/UI in ways the existing 23 states don't. Adding it also forces us to confront the stale-catalog problem: the URL in `tools/manual_urls.json` returns 404, and the official DDS site no longer exposes a single monolithic PDF — both are recurring patterns we'll hit for most remaining states.

This change is intentionally scoped to a single state so the existing pipeline (`setup_state.py` → `generate_questions.py` → `add_sign_questions.py` → `translate.py` → `bundle.py`) gets exercised end-to-end before we attempt waves of states in the follow-up `refresh-manual-catalog` change.

## What Changes

- Find and verify a current official Georgia DDS manual source (PDF or HTML); update `tools/manual_urls.json` with the working URL.
- Run the full state-onboarding pipeline for `ga`, producing `data/states/ga/{config.json,questions_en.yaml,questions_es.yaml,questions_ja.yaml}`.
- Generate sign questions and confirm shared MUTCD signs cover GA-specific signage (or extend `data/signs/` if not).
- Audit the generated questions against the manual; fix any that don't trace cleanly to source.
- Verify the bundle builds and that GA appears correctly in iOS, Android, and frontend state lists.
- If the GA manual is multi-PDF (chapter-by-chapter, like Michigan now is), document the concatenation workaround in this change's `design.md` and flag it as work for `refresh-manual-catalog` to systematize.

## Capabilities

### New Capabilities
<!-- None — this is a data addition, not a behavior change. -->

### Modified Capabilities
<!-- None — adding a state's data files does not change spec-level requirements of any existing capability. -->

## Impact

- **Data**: new `data/states/ga/` directory (source of truth, checked in).
- **Catalog**: one entry updated in `tools/manual_urls.json`.
- **Build artifacts**: regenerated bundles for iOS/Android/web (gitignored, rebuilt on every build).
- **No code changes** if the GA manual is single-PDF and text-extractable. If multi-PDF, a small one-off concat step is documented but not productionized here.
- **No platform UI changes** — state list is data-driven.
