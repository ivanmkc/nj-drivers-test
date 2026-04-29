## 1. Pre-flight (depends on `refresh-manual-catalog` merged)

- [ ] 1.1 Confirm `refresh-manual-catalog` has landed on main; the `tools/_manual_fetch.py` module and `setup_state.py --from-catalog` flag must exist.
- [ ] 1.2 Run `python3 tools/verify_manuals.py` and confirm the `mi` entry passes (`http=200`, `content-type=application/pdf`, host on allowlist).

## 2. Run the pipeline

- [ ] 2.1 `python3 tools/setup_state.py --from-catalog mi` (uses `urls` list field via the multi-source code path).
- [ ] 2.2 If the chained `generate_questions.py` step doesn't auto-trigger, run it explicitly: `python3 tools/generate_questions.py mi /tmp/mi_manual_text.txt`.
- [ ] 2.3 `python3 tools/add_sign_questions.py mi`.
- [ ] 2.4 `python3 tools/translate.py mi es` (skip rate-limited batches; re-run to fill).

## 3. Quality

- [ ] 3.1 `python3 tools/audit_questions.py` — must pass clean, including MI.
- [ ] 3.2 Spot-check 10 random non-sign questions in `data/states/mi/questions_en.yaml`. Each `explanation` must reference a specific section/page of *What Every Driver Must Know*. Discard any question that's about translations of the manual rather than driving content.
- [ ] 3.3 `ruff check . && ruff format --check . && pyright` — all green.

## 4. Bundle and smoke test

- [ ] 4.1 `python3 tools/bundle.py` — confirm `mi` appears with 50 questions / 80% pass.
- [ ] 4.2 Frontend: `cd frontend && npm run dev` — pick MI, run a test session, verify thresholds.
- [ ] 4.3 At least one native platform (iOS or Android) — best-effort. Document in PR which were actually tested.

## 5. Docs

- [ ] 5.1 Add Michigan section to `SOURCES.md` (mirror existing format).
- [ ] 5.2 In `TODO_JURISDICTIONS.md`: move MI from "To Do" to "Complete" with question count and language matrix; bump the "X / 51" header.

## 6. Validate the multi-source path

- [ ] 6.1 Confirm `/tmp/mi_manual_text.txt` was assembled via `_manual_fetch.assemble_manual_text` (check for `=== chapter <n> ===` markers if multi-PDF, else just the single-PDF text).
- [ ] 6.2 If text quality is poor (repeated headers, page-number garbage, etc.), document the symptom in the PR for follow-up — do NOT hand-fix the text or weaken the audit.
