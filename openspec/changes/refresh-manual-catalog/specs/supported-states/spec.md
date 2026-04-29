## MODIFIED Requirements

### Requirement: All 50 US states and DC SHALL be supported

The app SHALL ship `data/states/<code>/` data directories for all 50 US states plus the District of Columbia, each containing a valid `config.json` and at least an English question bank (`questions_en.yaml`) grounded in that jurisdiction's official driver manual. The bundle compilation step SHALL include every supported state, and every supported state SHALL appear in the state-selection UI on iOS, Android, and the web frontend.

This requirement extends the prior "Georgia must be a supported state" requirement (introduced by `add-state-georgia`) to cover the full set of US jurisdictions.

#### Scenario: Bundle includes every state
- **WHEN** `python3 tools/bundle.py` runs after this change is applied
- **THEN** the resulting bundle contains entries for all 51 jurisdictions: AL, AK, AZ, AR, CA, CO, CT, DC, DE, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NY, NC, ND, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VT, VA, WA, WV, WI, WY

#### Scenario: Each new state's test session honors its specific format
- **WHEN** a user selects any newly-added state and starts a test session
- **THEN** the session presents the question count and applies the passing threshold declared in that state's `config.json` (matching the state's official knowledge test format)

#### Scenario: Questions in each new state trace to the official manual
- **WHEN** a reviewer audits a random sample of 10 entries from any newly-added state's `questions_en.yaml`
- **THEN** every entry's `explanation` field cites a specific chapter or page of that state's official driver manual
