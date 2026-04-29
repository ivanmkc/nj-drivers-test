## Why

The project's question banks are *generated from* state driver manuals — but the manuals themselves have never been checked into the repo. Today they live in `/tmp/<code>_manual.pdf` and `/tmp/<code>_manual_text.txt`, both ephemeral. Once the temp files are wiped (reboot, agent worktree teardown, CI runner cleanup), the original source is gone.

This breaks four things that matter:

1. **Reproducibility** — re-running `generate_questions.py` later requires the *exact same source*. Catalog URLs rot constantly (refresh-manual-catalog showed 7/7 of probed top-population URLs were broken), so "just re-download" isn't reliable.
2. **Audit trail** — spot-checking "does this question's explanation actually appear in the manual?" requires having the manual. Today reviewers have to re-download (and the URL may be dead).
3. **Provenance** — when a state ships a new edition with renumbered chapters, we need the original we used to defend each existing question.
4. **Resilience** — if a state DMV pulls a PDF offline (which happens — they restructure their sites every ~2 years), every question grounded in that manual becomes unverifiable.

Per-question `explanation` strings cite chapters/pages, but the chapters/pages themselves disappear unless we hold the source.

## What Changes

- New per-state artifacts, committed to the repo:
  - `data/states/<code>/manual.pdf` — the source PDF, **pre-compressed via Ghostscript `/ebook` preset** (typical 70% savings, e.g. GA 49.5 MB → 14.7 MB) and tracked via **Git LFS** (avoids permanent repo bloat).
  - `data/states/<code>/manual_text.txt` — PyMuPDF-extracted plain text (committed normally; small, grep-able, diffable; not gzipped — see design.md decision 3).
  - `data/states/<code>/manual_provenance.json` — structured metadata: source URL(s), edition, download timestamp, SHA-256 hashes of the PDF and text, page count, extractor version, and a `pdf.compression` sub-object recording the original (pre-compression) hash and size for byte-level reproducibility. Schema versioned via a `schema_version` field.
- For multi-source manuals (Michigan), per-chapter source files are stored as `manual_part_<n>.pdf` (LFS-tracked) with an array of source URLs in `manual_provenance.json`.
- New `.gitattributes` declares LFS filters for `data/states/*/manual*.pdf`.
- `tools/setup_state.py` writes manuals to the per-state directory (not `/tmp/`) and emits the provenance JSON automatically.
- `.gitignore` cleanup: remove the legacy `drivermanual.pdf` / `manual_text.txt` ignore lines (they were holdovers from when the project was NJ-only and stored manuals at the repo root).
- Documentation updates: `add-state` skill, `README.md`, `docs/maintaining-state-data.md` all explain the new layout and the Git LFS prerequisite for contributors.
- Backfill is a separate task group, scoped to the 23 already-onboarded states. Best-effort — for states where the original URL has rotted past recovery, the provenance file records `pdf_recovered: false` and the question bank stays as-is.

## Capabilities

### New Capabilities
- `manual-provenance`: tracks the per-state policy that every supported state SHALL ship with the source manual it was generated from, the extracted text, and structured provenance metadata sufficient to verify the question bank against the source.

### Modified Capabilities
<!-- None — this introduces a new capability rather than modifying existing ones. The supported-states capability is unaffected. -->

## Impact

- **Repo size growth**: ~30MB per state PDF × 51 states = ~1.5GB total in Git LFS. Text + metadata adds ~12MB total normal-tracked. Clones stay fast (LFS is fetched on demand or via `git lfs pull`).
- **Contributor prerequisite**: Git LFS must be installed locally to onboard new states or modify provenance. Documented in README. CI must run `git lfs install` before checkout.
- **GitHub LFS quota**: free tier is 1GB storage + 1GB bandwidth/month. May need a paid plan or LFS bandwidth sponsor as states are added. Document the limit; revisit if it becomes a real constraint.
- **`tools/setup_state.py` change**: now writes to per-state directory; also accepts an `--no-commit-source` escape hatch for cases where the manual is restricted (none currently known, but reserve the flag).
- **Audit script extension**: `tools/audit_questions.py` learns to verify, for each state, that `manual.pdf` and `manual_text.txt` exist AND that their SHA-256s match `manual_provenance.json`. Catches accidental tampering.
- **Backfill**: 23 existing states need the new artifacts. ~half a day of work — download from current `manual_url` (refreshed by `refresh-manual-catalog`), extract text, hash, write provenance. For any state whose URL is unrecoverable, mark `pdf_recovered: false`.
- **Coordination with `refresh-manual-catalog`**: this change should land *after* the catalog refresh so the URLs we pull from for backfill are fresh.
