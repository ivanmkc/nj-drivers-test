## ADDED Requirements

### Requirement: South Dakota must be a supported state

The app SHALL ship a `data/states/sd/` data directory containing a valid `config.json` and at least an English question bank (`questions_en.yaml`), grounded in the December 2023 edition of the South Dakota Driver Manual published by the South Dakota Department of Public Safety. The bundle compilation step SHALL include South Dakota, and South Dakota SHALL appear in the state-selection UI on iOS, Android, and the web frontend.

#### Scenario: Bundle includes South Dakota
- **WHEN** `python3 tools/bundle.py` runs after this change is applied
- **THEN** the resulting bundle contains an `sd` entry with at least one question per category referenced in `config.json`

#### Scenario: Test session honors South Dakota's specific format
- **WHEN** a user selects South Dakota in any platform's UI and starts a test session
- **THEN** the session presents 25 questions and applies an 80% passing threshold

#### Scenario: Questions trace to the Dec 2023 SD manual
- **WHEN** a reviewer audits a random sample of 10 non-sign entries from `data/states/sd/questions_en.yaml`
- **THEN** every entry's `explanation` field cites a specific section or page of the December 2023 South Dakota Driver Manual

### Requirement: Catalog entries MAY declare a recovery URL for documents broken at the canonical source

When a state's canonical `manual_url` no longer resolves to the published document (e.g., the agency migrated its hosting), the catalog entry MAY include a `recovery_url` field pointing to an Internet Archive snapshot of the same canonical URL. The fetcher SHALL prefer `recovery_url` over `manual_url` when both are present. The host allowlist enforced on `manual_url` SHALL NOT be enforced on `recovery_url`.

#### Scenario: Fetcher prefers recovery_url when present
- **WHEN** `tools/_manual_fetch.py::assemble_manual_text` resolves a catalog entry that includes a non-empty `recovery_url`
- **THEN** it downloads from `recovery_url` rather than `manual_url`, while logging both URLs

#### Scenario: Verifier emits a `recovered` status when canonical fails but recovery succeeds
- **WHEN** `tools/verify_manuals.py` probes a catalog entry whose `manual_url` fails the freshness check but whose `recovery_url` returns `application/pdf` with `Content-Length` above the minimum
- **THEN** the result row's status is `recovered`, distinct from both `ok` and `stale`, and the verifier exits with a soft warning rather than a hard failure for that row

#### Scenario: Recovery URL invariant — canonical must still be on an official host
- **WHEN** a catalog entry declares a `recovery_url`
- **THEN** its `manual_url` SHALL still satisfy the official-host allowlist used by `_is_official_host`; the verifier SHALL reject any entry that uses `recovery_url` to bypass the allowlist

### Requirement: Provenance records the actual retrieval method for archive-recovered manuals

When a state's manual is fetched via Internet Archive snapshot, `data/states/<code>/manual_provenance.json` SHALL record both the canonical `manual_url` and the `recovery_url` actually fetched, along with `extracted_with: "wayback_machine_snapshot"`.

#### Scenario: South Dakota's provenance names both URLs
- **WHEN** a maintainer inspects `data/states/sd/manual_provenance.json` after this change is applied
- **THEN** the file contains `manual_url` pointing to `dps.sd.gov/application/files/9717/0863/8492/sd-driver-manual-rev-12-2023.pdf`, a `recovery_url` pointing to the `web.archive.org/web/20241125195101/...` snapshot of that same URL, `extracted_with` set to `"wayback_machine_snapshot"`, and `pdf.recovered` set to `true`
