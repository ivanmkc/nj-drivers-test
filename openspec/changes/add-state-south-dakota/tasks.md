## 1. Catalog + tooling

- [ ] 1.1 Add `recovery_url: "https://web.archive.org/web/20241125195101/https://dps.sd.gov/application/files/9717/0863/8492/sd-driver-manual-rev-12-2023.pdf"` to the `sd` entry in `tools/manual_urls.json`. Leave `manual_url` unchanged.
- [ ] 1.2 In `tools/_manual_fetch.py::assemble_manual_text`, when `entry.get("recovery_url")` is set, prefer it over `manual_url` for the actual download. Log both URLs.
- [ ] 1.3 In `tools/verify_manuals.py`, when `manual_url` fails but `recovery_url` returns `application/pdf` with `Content-Length > MIN_CONTENT_BYTES`, emit a new status `recovered` (not `ok`, not `stale`). Treat as a soft warning — surfaces the gap without blocking CI.
- [ ] 1.4 Confirm the host allowlist is NOT consulted for `recovery_url`; document the invariant inline (one comment).

## 2. Provenance

- [ ] 2.1 Replace `data/states/sd/manual_provenance.json` stub with a real record containing:
  - `manual_url`: canonical dead URL (intent)
  - `recovery_url`: Wayback snapshot URL (actual)
  - `extracted_with: "wayback_machine_snapshot"`
  - `pdf.recovered: true`
  - `pdf.sha256`: hash of the fetched bytes
  - `note`: short explanation of the ServiceNow migration

## 3. Run the pipeline

- [ ] 3.1 `python3 tools/setup_state.py --from-catalog sd` — downloads from `recovery_url`, extracts text via PyMuPDF, writes `data/states/sd/config.json`, generates `questions_en.yaml`, adds sign questions.
- [ ] 3.2 `python3 tools/translate.py sd es` — generate Spanish bank. (JA is out of scope per project rules.)
- [ ] 3.3 Confirm `data/states/sd/manual.pdf` is committed to Git LFS and the SHA matches the provenance record.

## 4. Quality

- [ ] 4.1 `python3 tools/audit_questions.py` — must pass clean for `sd`.
- [ ] 4.2 `python3 tools/quiz_gates.py sd --write-report` — Grade A or B; HARD_FAIL blocks the PR.
- [ ] 4.3 Spot-check 10 random questions. Each `explanation` must trace to the Dec 2023 SD manual. Pay particular attention to: studded-tire dates (Apr 16 – Sep 30 ban), instruction-permit minimum age (14), distracted-driving penalties, wildlife-collision protocol.
- [ ] 4.4 `ruff check . && ruff format --check . && pyright` — all green.

## 5. Bundle and smoke test

- [ ] 5.1 `python3 tools/bundle.py` — confirm `sd` appears with 25 questions / 80% pass.
- [ ] 5.2 Frontend dev server: pick South Dakota, run a session, confirm sign images render and explanations cite the manual.
- [ ] 5.3 Native platform smoke test — best-effort. Document in PR.

## 6. Docs

- [ ] 6.1 Add South Dakota section to `SOURCES.md` documenting the archive-recovery exception (snapshot timestamp, original URL, reason).
- [ ] 6.2 Flip SD checkbox in `TODO_JURISDICTIONS.md`; bump the US count 49 → 50. Leave DC as the single remaining stub with a one-line note about the Issuu-only blocker.

## 7. Followups (separate PRs, not blockers)

- [ ] 7.1 Re-verify `dps.sd.gov` quarterly. If SD republishes, drop `recovery_url` and re-fetch from the canonical URL.
- [ ] 7.2 If DC's Issuu situation persists, decide between (a) headless-browser scrape or (b) permanently document DC as a non-shipping jurisdiction.
