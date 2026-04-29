## ADDED Requirements

### Requirement: Catalog entries SHALL declare freshness metadata

Every entry in `tools/manual_urls.json` MUST include `edition` (free-form string identifying which edition of the manual the entry points to, e.g. `"2025-10"` or `"2026"`) and `last_verified` (ISO-8601 date of the most recent successful HEAD verification). Existing single-URL entries continue to validate; new fields are required only on entries added or updated by this change.

#### Scenario: Verifier writes back the timestamp on success
- **WHEN** `python3 tools/verify_manuals.py --update-timestamps` runs and an entry's URL responds with HTTP 200 and the expected content type
- **THEN** that entry's `last_verified` field is updated to today's date (UTC) and the file is written back with stable formatting

#### Scenario: Stale entries are visibly stale
- **WHEN** a maintainer opens `tools/manual_urls.json`
- **THEN** they can see at a glance which entries have a `last_verified` older than 90 days and which manual edition each entry corresponds to

### Requirement: Catalog URLs MUST resolve to official state-agency hosts

Every URL in `manual_url` and (if present) `urls` MUST be hosted on a state government domain (`*.<state>.gov`, `dot.<state>.gov`, or a documented allowlist exception such as `oklahoma.gov`). Third-party mirror sites (e.g., `driving-tests.org`, `dmvquestionbank.com`, `usdrivertraining.com`) are NOT acceptable sources, even when they host identical PDFs.

#### Scenario: Verifier rejects non-official hosts
- **WHEN** `verify_manuals.py` encounters an entry whose URL host is not on the official-host allowlist
- **THEN** it reports the entry as `suspicious-host` and does not update `last_verified`, even if the URL resolves with HTTP 200

### Requirement: A scheduled CI job SHALL surface catalog rot

A GitHub Actions workflow MUST run `verify_manuals.py` on a monthly schedule (cron `0 7 1 * *`) and on manual dispatch. Failures MUST NOT block PR builds. Verification results MUST be visible in a long-running tracking issue that is created on first run and updated on each subsequent run.

#### Scenario: Monthly verification posts to the tracking issue
- **WHEN** the scheduled workflow runs and any entries fail verification
- **THEN** the tracking issue receives a comment listing the failing entries with their codes, URLs, and HTTP status codes
