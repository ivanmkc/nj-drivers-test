## 1. Pre-flight (depends on `refresh-manual-catalog` merged)

- [ ] 1.1 Confirm `refresh-manual-catalog` has landed on main.
- [ ] 1.2 Run `python3 tools/verify_manuals.py` and confirm the `co` entry passes (host previously 403'd default curl — ensure `verify_manuals.py` uses `Mozilla/5.0` UA).

## 2. Run the pipeline

- [ ] 2.1 `python3 tools/setup_state.py --from-catalog co` (single-PDF, DR 2337 Jan 2025 ed.).
- [ ] 2.2 `python3 tools/translate.py co es`.

## 3. Quality

- [ ] 3.1 `python3 tools/audit_questions.py` — must pass clean.
- [ ] 3.2 Spot-check 10 random questions. Each `explanation` must trace to the CO manual.
- [ ] 3.3 Verify mountain-driving questions (chain laws, brake fade, runaway truck ramps, altitude-related vehicle limits) cite specific CO manual sections — these are CO-specific test content and should not be omitted.
- [ ] 3.4 `ruff check . && ruff format --check . && pyright` — all green.

## 4. Bundle and smoke test

- [ ] 4.1 `python3 tools/bundle.py` — confirm `co` appears with 25 questions / 80% pass.
- [ ] 4.2 Frontend: dev server, pick CO, run a session.
- [ ] 4.3 At least one native platform — best-effort. Document in PR.

## 5. Docs

- [ ] 5.1 Add Colorado section to `SOURCES.md`.
- [ ] 5.2 Flip CO checkbox in `TODO_JURISDICTIONS.md`; bump the count.
