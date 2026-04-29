## 1. Pre-flight (depends on `refresh-manual-catalog` merged)

- [ ] 1.1 Confirm `refresh-manual-catalog` has landed on main.
- [ ] 1.2 Run `python3 tools/verify_manuals.py` and confirm the `mn` entry passes (host moved to `assets.dps.mn.gov` during the refresh).

## 2. Run the pipeline

- [ ] 2.1 `python3 tools/setup_state.py --from-catalog mn` (single-PDF, May 2025 ed.).
- [ ] 2.2 `python3 tools/translate.py mn es`.

## 3. Quality

- [ ] 3.1 `python3 tools/audit_questions.py` — must pass clean.
- [ ] 3.2 Spot-check 10 random questions. Each `explanation` must trace to the MN manual.
- [ ] 3.3 Verify winter-driving questions (skid recovery, snow-emergency rules, snowplow following distance, chain restrictions) cite specific MN manual sections.
- [ ] 3.4 Confirm any snowmobile/ATV road-use rules from the manual are represented if they're test content.
- [ ] 3.5 `ruff check . && ruff format --check . && pyright` — all green.

## 4. Bundle and smoke test

- [ ] 4.1 `python3 tools/bundle.py` — confirm `mn` appears with 40 questions / 80% pass.
- [ ] 4.2 Frontend: dev server, pick MN, run a session.
- [ ] 4.3 At least one native platform — best-effort. Document in PR.

## 5. Docs

- [ ] 5.1 Add Minnesota section to `SOURCES.md`.
- [ ] 5.2 Flip MN checkbox in `TODO_JURISDICTIONS.md`; bump the count.
