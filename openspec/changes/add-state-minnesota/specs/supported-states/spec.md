## ADDED Requirements

### Requirement: Minnesota must be a supported state

The app SHALL ship a `data/states/mn/` data directory containing a valid `config.json` and at least an English question bank (`questions_en.yaml`), grounded in the May 2025 Minnesota Driver's Manual published by Minnesota DPS-DVS. The bundle compilation step SHALL include Minnesota, and Minnesota SHALL appear in the state-selection UI on iOS, Android, and the web frontend.

#### Scenario: Bundle includes Minnesota
- **WHEN** `python3 tools/bundle.py` runs after this change is applied
- **THEN** the resulting bundle contains an `mn` entry with at least one question per category referenced in `config.json`

#### Scenario: Test session honors Minnesota's specific format
- **WHEN** a user selects Minnesota in any platform's UI and starts a test session
- **THEN** the session presents 40 questions and applies an 80% passing threshold

#### Scenario: Questions trace to the official manual
- **WHEN** a reviewer audits a random sample of 10 non-sign entries from `data/states/mn/questions_en.yaml`
- **THEN** every entry's `explanation` field cites a specific section or page of the Minnesota Driver's Manual

#### Scenario: Winter-driving content is represented
- **WHEN** the MN manual covers skid recovery, snow-emergency rules, snowplow following distance, or chain restrictions
- **THEN** at least one question in `questions_en.yaml` covers each such topic, sourced from the MN manual
