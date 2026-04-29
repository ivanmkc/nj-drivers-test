## 1. Pre-flight (depends on `refresh-manual-catalog` merged)

- [ ] 1.1 Confirm `refresh-manual-catalog` has landed on main.
- [ ] 1.2 Run `python3 tools/verify_manuals.py` and confirm the `az` entry passes.

## 2. Run the pipeline

- [ ] 2.1 `python3 tools/setup_state.py --from-catalog az` (single-PDF happy path).
- [ ] 2.2 `python3 tools/translate.py az es`.

## 3. Quality

- [ ] 3.1 `python3 tools/audit_questions.py` — must pass clean.
- [ ] 3.2 Spot-check 10 random questions in `data/states/az/questions_en.yaml`. Each `explanation` must trace to the AZ manual.
- [ ] 3.3 Verify desert/mountain-driving questions (dust storms, runaway truck ramps) cite AZ-specific sections, not generic content the LLM may have memorized from NV/NM manuals.
- [ ] 3.4 `ruff check . && ruff format --check . && pyright` — all green.

## 4. Bundle and smoke test

- [ ] 4.1 `python3 tools/bundle.py` — confirm `az` appears with 30 questions / 80% pass.
- [ ] 4.2 Frontend: dev server, pick AZ, run a session.
- [ ] 4.3 At least one native platform — best-effort. Document in PR.

## 5. Docs

- [ ] 5.1 Add Arizona section to `SOURCES.md`.
- [ ] 5.2 Flip AZ checkbox in `TODO_JURISDICTIONS.md`; bump the count.
