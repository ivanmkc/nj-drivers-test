## 1. Define the schema

- [ ] 1.1 Document the `manual_provenance.json` schema (as in `design.md`) at the top of `docs/maintaining-state-data.md` (or a new `docs/manual-provenance-schema.md` if cleaner).
- [ ] 1.2 Add a Python dataclass or TypedDict in `tools/_provenance.py` that mirrors the schema, with a `validate(d: dict) -> None` helper that raises on shape errors.

## 2. Wire up Git LFS

- [ ] 2.1 Add `.gitattributes` at repo root: `data/states/*/manual.pdf filter=lfs diff=lfs merge=lfs -text` and `data/states/*/manual_part_*.pdf filter=lfs diff=lfs merge=lfs -text`.
- [ ] 2.2 Run `git lfs install` in the repo (creates `.git/hooks/pre-push` etc.) — document in README that this is also required for every contributor's local clone.
- [ ] 2.3 Update `.gitignore`: remove the legacy `drivermanual.pdf` and `manual_text.txt` lines (they're holdovers).
- [ ] 2.4 README + `docs/maintaining-state-data.md`: add Git LFS setup section ("install once: `git lfs install`; clones: `git lfs pull`").
- [ ] 2.5 CI workflows (`.github/workflows/{ios,android,verify-manuals}.yml`): add `git lfs install --skip-smudge` to checkout step + run `git lfs pull` only when needed (skip in lint-only jobs to save bandwidth).

## 3. Update setup_state.py

- [ ] 3.1 `setup_state.py` writes the downloaded PDF to `data/states/<code>/manual.pdf` (instead of `/tmp/<code>_manual.pdf`) and the extracted text to `data/states/<code>/manual_text.txt` (instead of `/tmp/<code>_manual_text.txt`).
- [ ] 3.1a Commit the downloaded PDF to `data/states/<code>/manual.pdf` **as-is, no compression.** Earlier drafts of this design mandated Ghostscript `/ebook`; that decision was reverted on 2026-04-29 — see design.md decision 2 for empirical numbers (~5% savings from any generic compression vs 70% lossy savings from gs, not worth the complexity). Extract text from the as-downloaded PDF.
- [ ] 3.2 After download + compress + extract, write `data/states/<code>/manual_provenance.json` with all schema fields populated, including SHA-256 hashes computed via `hashlib.sha256`, `extracted_with` set from the PyMuPDF version, and a `pdf.compression` sub-object recording the tool/preset/command/original_size_bytes/original_sha256.
- [ ] 3.3 For multi-source states (entries with non-empty `urls` in the catalog), download each part to `data/states/<code>/manual_part_<n>.pdf`, concatenate to `manual.pdf`, and populate the `sources` array in provenance.
- [ ] 3.4 Add a `--re-fetch` flag that re-downloads even if the per-state files exist (useful when an edition updates).

## 4. Extend audit_questions.py

- [ ] 4.1 For each state, verify `data/states/<code>/manual_provenance.json` exists and validates against the schema.
- [ ] 4.2 Recompute SHA-256 of `manual.pdf` and `manual_text.txt`; HARD FAIL on mismatch when `pdf.recovered: true`.
- [ ] 4.3 If `manual.pdf` is missing entirely on a `recovered: true` state, soft warn (LFS may not be pulled in CI; don't false-fail there).
- [ ] 4.4 If `recovered: false`, pass silently (acknowledged gap).

## 5. Apply to Georgia (the trigger state)

- [ ] 5.1 In the GA worktree (or a follow-up commit on main after GA merges): move `/tmp/ga_manual.pdf` and `/tmp/ga_manual_text.txt` to `data/states/ga/`.
- [ ] 5.2 Generate `data/states/ga/manual_provenance.json`.
- [ ] 5.3 `git lfs track` the PDF; commit.
- [ ] 5.4 Verify clone-from-scratch + `git lfs pull` round-trips both files clean.

## 6. Backfill the 23 existing states (best-effort)

- [ ] 6.1 For each of {al, ca, fl, ia, il, in, ks, ky, ma, md, mo, nc, nj, nv, ny, oh, or, pa, tn, tx, va, wa, wi}: re-download from the (refreshed) `manual_url`, extract text, write provenance.
- [ ] 6.2 Where the URL works: commit PDF (LFS), text, and provenance with `recovered: true`.
- [ ] 6.3 Where the URL is unrecoverable: commit only `manual_provenance.json` with `recovered: false` and a `note` explaining (e.g., "URL 404 as of 2026-04-29; pre-existing question bank retained").
- [ ] 6.4 Spot-check 2-3 backfilled states: do the existing question banks' explanations cite content that appears in the recovered text?

## 7. Documentation

- [ ] 7.1 Update `.claude/skills/add-state/SKILL.md`: pipeline writes to `data/states/<code>/manual.{pdf,txt}` + `manual_provenance.json`; add Git LFS prereq.
- [ ] 7.2 Update `README.md`'s "Adding a New State" section.
- [ ] 7.3 Update `CLAUDE.md` Gotchas: note that `manual.pdf` is LFS-tracked and contributors must run `git lfs install`.
- [ ] 7.4 Update `SOURCES.md`: each state's entry can now include `Provenance: data/states/<code>/manual_provenance.json` as a one-liner pointer.

## 8. Verify and ship

- [ ] 8.1 `python3 tools/audit_questions.py` clean across all states (with the new provenance checks).
- [ ] 8.2 `python3 tools/bundle.py` produces an unchanged bundle (provenance files are NOT included in the bundle — they're audit-only).
- [ ] 8.3 `ruff check . && ruff format --check . && pyright` green.
- [ ] 8.4 GitHub LFS storage usage check: confirm we're under quota; if not, document next steps.
