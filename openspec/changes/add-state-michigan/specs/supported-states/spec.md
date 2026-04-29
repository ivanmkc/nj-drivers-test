## ADDED Requirements

### Requirement: Michigan must be a supported state

The app SHALL ship a `data/states/mi/` data directory containing a valid `config.json` and at least an English question bank (`questions_en.yaml`), grounded in the official Michigan SOS publication *What Every Driver Must Know* (Oct 2025 ed.). The bundle compilation step SHALL include Michigan, and Michigan SHALL appear in the state-selection UI on iOS, Android, and the web frontend.

#### Scenario: Bundle includes Michigan
- **WHEN** `python3 tools/bundle.py` runs after this change is applied
- **THEN** the resulting bundle contains a `mi` entry with at least one question per category referenced in `config.json`

#### Scenario: Test session honors Michigan's specific format
- **WHEN** a user selects Michigan in any platform's UI and starts a test session
- **THEN** the session presents 50 questions and applies an 80% passing threshold

#### Scenario: Questions trace to the official manual
- **WHEN** a reviewer audits a random sample of 10 non-sign entries from `data/states/mi/questions_en.yaml`
- **THEN** every entry's `explanation` field cites a specific section or page of *What Every Driver Must Know*

#### Scenario: Multi-source extraction was exercised
- **WHEN** a maintainer inspects the source-text artifact `/tmp/mi_manual_text.txt` produced during onboarding
- **THEN** the file was assembled by `tools/_manual_fetch.assemble_manual_text` (i.e., the multi-source code path introduced by `refresh-manual-catalog`), not by the legacy single-PDF download branch in `setup_state.py`
