## ADDED Requirements

### Requirement: Colorado must be a supported state

The app SHALL ship a `data/states/co/` data directory containing a valid `config.json` and at least an English question bank (`questions_en.yaml`), grounded in the January 2025 Colorado Driver Handbook (DR 2337) published by the Colorado DMV. The bundle compilation step SHALL include Colorado, and Colorado SHALL appear in the state-selection UI on iOS, Android, and the web frontend.

#### Scenario: Bundle includes Colorado
- **WHEN** `python3 tools/bundle.py` runs after this change is applied
- **THEN** the resulting bundle contains a `co` entry with at least one question per category referenced in `config.json`

#### Scenario: Test session honors Colorado's specific format
- **WHEN** a user selects Colorado in any platform's UI and starts a test session
- **THEN** the session presents 25 questions and applies an 80% passing threshold

#### Scenario: Questions trace to the official manual
- **WHEN** a reviewer audits a random sample of 10 non-sign entries from `data/states/co/questions_en.yaml`
- **THEN** every entry's `explanation` field cites a specific section or page of the Colorado Driver Handbook (DR 2337)

#### Scenario: Mountain-driving content is represented
- **WHEN** the CO manual covers chain laws, brake-fade rules, runaway-truck ramps, or altitude-related vehicle limits
- **THEN** at least one question in `questions_en.yaml` covers each such topic, sourced from the CO manual
