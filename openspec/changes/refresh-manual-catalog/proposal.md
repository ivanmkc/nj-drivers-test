## Why

Spot-checking `tools/manual_urls.json` against live DMV/DOT sites revealed that the catalog has rotted: of the 28 missing-state entries probed (GA, MI, AZ, CO, MN, CT, LA, …), most return 404, 403, or HTML directory pages rather than PDFs. State agencies churn manual URLs every 1-2 editions, and the current catalog was last refreshed >12 months ago.

Two problems compound:

1. **Stale URLs make the existing 28-state backlog impossible to onboard at scale.** Running `setup_state.py` on a dead URL silently produces an empty manual text file and then a useless question bank. Every state currently requires manual URL hunting.
2. **Some states have moved away from monolithic PDFs.** Michigan's "What Every Driver Must Know" (Oct 2025 ed.) is now ~9 chapter-PDFs. The pipeline only handles single PDFs. Without multi-PDF support, ~5-8 states are blocked indefinitely.

The follow-up to `add-state-georgia` (which proves the pipeline still works on a single state) is to **fix these two systemic gaps** so the remaining 27 states can be added in 3-4 waves rather than one painful state at a time.

## What Changes

- **Catalog verification tool**: extend `tools/find_manuals.py` (or add a sibling `verify_manuals.py`) to HEAD-check every URL in `tools/manual_urls.json`, flag stale entries, and re-search for current ones via Gemini-with-Google-Search. Run it as part of CI on a monthly cadence.
- **Multi-PDF manual support**: `setup_state.py` learns to accept either a single URL or a list of URLs in `manual_urls.json`. When multiple URLs are given, it downloads and concatenates them in declared order before text extraction.
- **HTML-fallback support**: when no PDF exists, allow `manual_url` to point to an HTML index page; a new helper scrapes the linked chapter pages and produces a single text file.
- **Refreshed catalog**: re-find current URLs for all 27 still-missing states (everything except GA, which is handled by `add-state-georgia`) plus re-verify the 23 already-onboarded states. Update `tools/manual_urls.json`.
- **Onboard remaining 27 states in waves**, grouped by manual structure to surface bugs early:
  - Wave 1 (single-PDF, small): VT, WY, ND, SD, AK, DC, DE
  - Wave 2 (single-PDF, mid): UT, AR, CT, OK, NH, NM, NE, ID, WV, RI, ME, HI, MT
  - Wave 3 (multi-PDF or HTML-only): MI, MN, AZ, CO, SC, MS, LA
- **Per-edition tracking**: add an `edition` and `last_verified` field to each `manual_urls.json` entry and to each state's `config.json`, so future drift is visible at a glance.
- **Annual re-verification doc**: short `docs/maintaining-state-data.md` explaining the verify → re-find → audit loop and when to run it.

## Capabilities

### New Capabilities
- `manual-catalog`: tracks the canonical list of state manual sources, their freshness, their structure (single-PDF / multi-PDF / HTML), and the verification status of each entry.
- `multi-source-manual-extraction`: the pipeline behavior of accepting either a single URL, a list of URLs, or an HTML index page as the source for a state's manual text.

### Modified Capabilities
- `supported-states`: extended from "GA only" (introduced by `add-state-georgia`) to cover all 50 states + DC. Each remaining state added is a new scenario under the same requirement.

## Impact

- **Tooling**: changes to `tools/find_manuals.py` and `tools/setup_state.py`; possibly a new `tools/verify_manuals.py`.
- **Catalog file**: `tools/manual_urls.json` schema gains optional `urls` (list), `edition`, `last_verified` fields. Existing single-URL entries remain valid (backward compatible by reading `manual_url` if `urls` is absent).
- **Per-state config**: `data/states/<code>/config.json` gains `edition` and `last_verified` fields. Existing configs without them keep working; populated as each state is re-onboarded or added.
- **Data**: 27 new `data/states/<code>/` directories, each with en (required) + es (high-value). JA is no longer in scope.
- **CI**: add a monthly scheduled GitHub Actions job that runs the verifier and opens an issue when entries go stale. Non-blocking — informational only.
- **No platform UI changes** — state list stays data-driven.
- **No changes to question generation, sign extraction, or bundle format** beyond the multi-PDF text concatenation step.
