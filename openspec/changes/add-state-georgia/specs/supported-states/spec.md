## ADDED Requirements

### Requirement: Georgia must be a supported state

The app SHALL ship a `data/states/ga/` data directory containing a valid `config.json` and at least an English question bank (`questions_en.yaml`), grounded in the official Georgia DDS Driver's Manual. The bundle compilation step SHALL include Georgia, and Georgia SHALL appear in the state-selection UI on iOS, Android, and the web frontend.

#### Scenario: Bundle includes Georgia
- **WHEN** `python3 tools/bundle.py` runs after this change is applied
- **THEN** the resulting bundle (`shared/questions_bundle.json` and per-platform copies) contains a `ga` entry with at least one question per category referenced in `config.json`

#### Scenario: Test session honors Georgia's specific format
- **WHEN** a user selects Georgia in any platform's UI and starts a test session
- **THEN** the session presents 40 questions and applies a 75% passing threshold (per the official DDS test format)

#### Scenario: Questions trace to the official manual
- **WHEN** a reviewer audits a random sample of 10 entries from `data/states/ga/questions_en.yaml`
- **THEN** every entry's `explanation` field cites a specific chapter or page of the Georgia DDS Driver's Manual

#### Scenario: Manual URL is verifiable
- **WHEN** a maintainer issues an HTTP HEAD request to the `manual_url` recorded in `data/states/ga/config.json`
- **THEN** the response is HTTP 200 and the content type is either `application/pdf` or scrapeable HTML hosted on `dds.georgia.gov`
