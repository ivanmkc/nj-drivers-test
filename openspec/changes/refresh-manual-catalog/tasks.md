## 1. Build catalog verification

- [ ] 1.1 Add `tools/verify_manuals.py` that HEAD-checks every entry in `tools/manual_urls.json` and prints a table of `code | url | http | content-type | size | verdict`.
- [ ] 1.2 Implement a host allowlist (`*.gov`, common state subdomains) so re-found URLs from third-party mirrors are flagged as suspicious.
- [ ] 1.3 Add a `--update-timestamps` flag that, when verification passes, writes `last_verified` back into `manual_urls.json`.
- [ ] 1.4 Unit tests: mocked HTTP responses for 200/404/403/redirect/wrong-content-type cases.

## 2. Extend pipeline for multi-source manuals

- [ ] 2.1 Update `manual_urls.json` schema to allow optional `urls` (list of strings), `edition`, and `last_verified` fields. Document the schema at the top of the file as a JSON5-style comment or in the maintenance doc.
- [ ] 2.2 In `tools/setup_state.py`, branch on `urls` presence: download each URL in order, extract text from each, concatenate with a chapter separator (e.g., `\n\n=== chapter <n> ===\n\n`).
- [ ] 2.3 Add a small HTML scrape helper for HTML-index manuals (extract chapter `<a href>` links, fetch each, strip nav/footer, concatenate).
- [ ] 2.4 Backfill `edition` and `last_verified` fields onto the 23 existing `data/states/<code>/config.json` files using best-known values (or `unknown` / today's date for `last_verified`).

## 3. Refresh the catalog

- [ ] 3.1 Run `tools/find_manuals.py` for all 27 still-missing states (after `add-state-georgia` lands; exclude GA).
- [ ] 3.2 Run `tools/verify_manuals.py` against the refreshed entries. Iterate until all entries verify clean.
- [ ] 3.3 Re-verify the 23 already-onboarded states' URLs. Update any stale ones in-place; do not regenerate question banks.
- [ ] 3.4 Commit the refreshed `tools/manual_urls.json` as its own commit so the diff is reviewable in isolation.

## 4. Wave 1: single-PDF, low risk

> **Deferred — infrastructure-only PR.** Groups 4-7 require the GA work
> (`add-state-georgia`) to land first and represent tens of hours of Gemini API
> calls. They will be picked up in a follow-up session. This PR only delivers
> Groups 1, 2, 3, and 8.

- [ ] 4.1 For each of VT, WY, ND, SD, AK, DC, DE:
  - [ ] Run `setup_state.py` → `generate_questions.py` → `add_sign_questions.py`.
  - [ ] Spot-check 5 questions per state for manual-source citations.
  - [ ] Run `audit_questions.py`; fix any state-specific failures.
- [ ] 4.2 Bulk translate Wave 1 to es: `for c in vt wy nd sd ak dc de; do python3 tools/translate.py "$c" es; done`.
- [ ] 4.3 Run `bundle.py`; confirm all 7 states appear and that bundle size growth is reasonable (< 30% per state).
- [ ] 4.4 Smoke test on web frontend: each Wave 1 state selectable, test session works.
- [ ] 4.5 Smoke test on iOS + Android for at least 2 randomly chosen Wave 1 states.

## 5. Wave 2: single-PDF, broader coverage

- [ ] 5.1 For each of UT, AR, CT, OK, NH, NM, NE, ID, WV, RI, ME, HI, MT: same per-state pipeline as Wave 1.
- [ ] 5.2 Bulk translate Wave 2 to es.
- [ ] 5.3 Bundle, audit, smoke test (web + 2 native platforms).

## 6. Wave 3: multi-PDF / HTML-only

- [ ] 6.1 Confirm Wave-3 entries in `manual_urls.json` use the `urls` list form or HTML-index form as appropriate.
- [ ] 6.2 For each of MI, MN, AZ, CO, SC, MS, LA: run the pipeline.
- [ ] 6.3 Manually review **all** of the Michigan generated questions for duplicates (multi-PDF dedup risk). If duplicates found, add a dedup pass to `generate_questions.py` before continuing the wave.
- [ ] 6.4 Bulk translate Wave 3 to es.
- [ ] 6.5 Bundle, audit, smoke test.

## 7. Translation sweep

- [ ] 7.1 Run `translate.py <code> ja` for every state added in Waves 1-3 that doesn't yet have ja. Skip rate-limited batches.
- [ ] 7.2 Re-bundle after translations.

## 8. CI and documentation

- [ ] 8.1 Add `.github/workflows/verify-manuals.yml` running `verify_manuals.py` on cron `0 7 1 * *` and on manual dispatch. Job opens or updates a tracking issue with the verification results.
- [ ] 8.2 Write `docs/maintaining-state-data.md` covering: how to add a new state, how to refresh a stale URL, how to handle multi-PDF manuals, how to interpret the monthly tracking issue.
- [ ] 8.3 Link the new doc from the project root README.

## 9. Final verification

- [ ] 9.1 `python3 tools/audit_questions.py` clean across all 51 states.
- [ ] 9.2 `python3 tools/bundle.py` produces a bundle including all 51 states.
- [ ] 9.3 `ruff check . && ruff format --check . && pyright` all green.
- [ ] 9.4 Frontend, iOS, Android lint commands all green.
- [ ] 9.5 README updated to say "all 50 states + DC supported."
