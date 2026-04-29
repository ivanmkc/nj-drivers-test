## ADDED Requirements

### Requirement: South Carolina must be a supported state

The app SHALL ship a `data/states/sc/` data directory containing a valid `config.json` and at least an English question bank (`questions_en.yaml`), grounded in the December 2025 South Carolina Driver's Manual published by the SC DMV. The bundle compilation step SHALL include South Carolina, and South Carolina SHALL appear in the state-selection UI on iOS, Android, and the web frontend.

#### Scenario: Bundle includes South Carolina
- **WHEN** `python3 tools/bundle.py` runs after this change is applied
- **THEN** the resulting bundle contains an `sc` entry with at least one question per category referenced in `config.json`

#### Scenario: Test session honors South Carolina's specific format
- **WHEN** a user selects South Carolina in any platform's UI and starts a test session
- **THEN** the session presents 30 questions and applies an 80% passing threshold

#### Scenario: Questions trace to the official manual
- **WHEN** a reviewer audits a random sample of 10 non-sign entries from `data/states/sc/questions_en.yaml`
- **THEN** every entry's `explanation` field cites a specific section or page of the South Carolina Driver's Manual

#### Scenario: Manual URL is hosted on a clean .gov domain
- **WHEN** a maintainer inspects the `manual_url` recorded in `data/states/sc/config.json`
- **THEN** the URL host is `dmv.sc.gov` (a state government domain on the default allowlist), NOT `scdmvonline.com` (the legacy host that required an allowlist exception)
