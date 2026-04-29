## ADDED Requirements

### Requirement: Arizona must be a supported state

The app SHALL ship a `data/states/az/` data directory containing a valid `config.json` and at least an English question bank (`questions_en.yaml`), grounded in the 2025 Arizona Driver License Manual published by AZDOT MVD. The bundle compilation step SHALL include Arizona, and Arizona SHALL appear in the state-selection UI on iOS, Android, and the web frontend.

#### Scenario: Bundle includes Arizona
- **WHEN** `python3 tools/bundle.py` runs after this change is applied
- **THEN** the resulting bundle contains an `az` entry with at least one question per category referenced in `config.json`

#### Scenario: Test session honors Arizona's specific format
- **WHEN** a user selects Arizona in any platform's UI and starts a test session
- **THEN** the session presents 30 questions and applies an 80% passing threshold

#### Scenario: Questions trace to the official manual
- **WHEN** a reviewer audits a random sample of 10 non-sign entries from `data/states/az/questions_en.yaml`
- **THEN** every entry's `explanation` field cites a specific section or page of the 2025 Arizona Driver License Manual

#### Scenario: AZ-specific content is represented when present in the source
- **WHEN** the AZ manual covers desert-driving topics (dust storms, runaway truck ramps, monsoon flooding)
- **THEN** at least one question in `questions_en.yaml` covers each such topic, sourced from the AZ manual rather than memorized cross-state knowledge
