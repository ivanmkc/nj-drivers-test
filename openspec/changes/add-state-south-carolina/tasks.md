## 1. Pre-flight (depends on `refresh-manual-catalog` merged)

- [ ] 1.1 Confirm `refresh-manual-catalog` has landed on main.
- [ ] 1.2 Run `python3 tools/verify_manuals.py` and confirm the `sc` entry passes (host migrated from `scdmvonline.com` to `dmv.sc.gov` during the refresh — should now pass without an allowlist exception).

## 2. Run the pipeline

- [ ] 2.1 `python3 tools/setup_state.py --from-catalog sc` (single-PDF, Dec 2025 ed.).
- [ ] 2.2 `python3 tools/translate.py sc es`.

## 3. Quality

- [ ] 3.1 `python3 tools/audit_questions.py` — must pass clean.
- [ ] 3.2 Spot-check 10 random questions. Each `explanation` must trace to the SC manual.
- [ ] 3.3 Verify SC-specific content (hurricane-evacuation procedures, contraflow-lane rules, beach-driving statutes) is represented if present in the manual.
- [ ] 3.4 `ruff check . && ruff format --check . && pyright` — all green.

## 4. Bundle and smoke test

- [ ] 4.1 `python3 tools/bundle.py` — confirm `sc` appears with 30 questions / 80% pass.
- [ ] 4.2 Frontend: dev server, pick SC, run a session.
- [ ] 4.3 At least one native platform — best-effort. Document in PR.

## 5. Docs

- [ ] 5.1 Add South Carolina section to `SOURCES.md`.
- [ ] 5.2 Flip SC checkbox in `TODO_JURISDICTIONS.md`; bump the count.

## 6. Validate the host-allowlist policy in practice

- [ ] 6.1 Confirm the `dmv.sc.gov` host is accepted by `verify_manuals.py` without needing an entry on the allowlist exception list. If it requires an exception, that's a bug in the allowlist regex — surface it before completing this change.
