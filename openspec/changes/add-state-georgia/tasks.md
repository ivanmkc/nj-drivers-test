## 1. Find and verify the current GA manual source

- [ ] 1.1 Browse `dds.georgia.gov/drivers-manual` and `dds.georgia.gov/dds-forms-and-manuals/manuals`; identify the current 2025/2026 edition.
- [ ] 1.2 Curl-test any candidate `.pdf` URL with `-A "Mozilla/5.0"`; confirm HTTP 200 and `Content-Type: application/pdf`.
- [ ] 1.3 If no single PDF exists, list each chapter URL from `dds.georgia.gov/drivers-manual-contents` and curl-test all of them.
- [ ] 1.4 Record the chosen approach (single PDF vs. chapter scrape) in `design.md` Decisions section.

## 2. Update catalog and config

- [ ] 2.1 Update the `ga` entry in `tools/manual_urls.json` with the verified URL (or for chapter-scrape, the contents-page URL).
- [ ] 2.2 Confirm `passing_score_pct: 75` and `test_question_count: 40` are correct via the official DDS site, not third-party sources.

## 3. Run the onboarding pipeline

- [ ] 3.1 `python3 tools/setup_state.py ga "Georgia" "DDS" 75 40 <verified_url> "2026 Georgia Driver's Manual (dds.georgia.gov)"`.
- [ ] 3.2 If chapter-scrape fallback: write the concatenated text to `/tmp/ga_manual_text.txt` manually before running `generate_questions.py`.
- [ ] 3.3 `python3 tools/generate_questions.py ga /tmp/ga_manual_text.txt`.
- [ ] 3.4 `python3 tools/add_sign_questions.py ga`.
- [ ] 3.5 Spot-check 10 random questions in `data/states/ga/questions_en.yaml`: each must cite a manual page/chapter in `explanation`.

## 4. Translate

- [ ] 4.1 `python3 tools/translate.py ga es`. Check output for skipped batches.
- [ ] 4.2 `python3 tools/translate.py ga ja` (optional; skip if rate-limited).

## 5. Audit and bundle

- [ ] 5.1 `python3 tools/audit_questions.py` — fix any GA-specific failures.
- [ ] 5.2 `python3 tools/bundle.py` — confirm `ga` appears in the bundle output.
- [ ] 5.3 `ruff check . && ruff format --check . && pyright` — confirm no new lint/type errors.

## 6. Platform smoke tests

- [ ] 6.1 Frontend: `cd frontend && npm run dev` — confirm GA appears in state list, test session uses 40 questions / 75% threshold, signs render.
- [ ] 6.2 iOS: build in Xcode, switch to GA, run a full mock test. Confirm pass/fail messaging at 75%.
- [ ] 6.3 Android: `./gradlew assembleDebug`, install on emulator, switch to GA, same checks.

## 7. Document multi-PDF learnings (if applicable)

- [ ] 7.1 If chapter-scrape was needed, write a 1-paragraph note in `design.md` Risks section describing what was hard, so `refresh-manual-catalog` can systematize it.
