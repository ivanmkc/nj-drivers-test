## ADDED Requirements

### Requirement: Every supported state SHALL ship its source manual

Every `data/states/<code>/` directory MUST contain three new artifacts in addition to the existing `config.json` and `questions_*.yaml`:

- `manual.pdf` — the source PDF the question bank was generated from, tracked via Git LFS.
- `manual_text.txt` — the PyMuPDF-extracted plain text used as input to question generation.
- `manual_provenance.json` — structured metadata sufficient to reproduce the question generation byte-for-byte.

States whose original PDF cannot be recovered from any source MAY omit `manual.pdf` and `manual_text.txt`, but MUST still ship a `manual_provenance.json` with `pdf.recovered: false` and a human-readable `note` explaining the gap.

#### Scenario: New state onboarding writes the source materials
- **WHEN** `python3 tools/setup_state.py --from-catalog <code>` runs successfully for a new state
- **THEN** the resulting `data/states/<code>/` directory contains `manual.pdf`, `manual_text.txt`, and `manual_provenance.json`, with the provenance file populated for every schema field

#### Scenario: Audit detects tampering with the manual
- **WHEN** `python3 tools/audit_questions.py` runs and any state's actual `manual.pdf` or `manual_text.txt` SHA-256 differs from the value recorded in `manual_provenance.json` (and `pdf.recovered: true`)
- **THEN** the audit fails with a clear error identifying the tampered file

#### Scenario: Audit tolerates missing LFS objects in CI
- **WHEN** `python3 tools/audit_questions.py` runs in an environment where `manual.pdf` is an LFS pointer that has not been smudged (`git lfs pull` not yet run)
- **THEN** the audit emits a soft warning rather than failing, so lint-only CI jobs don't require LFS bandwidth

#### Scenario: Recovered-false states pass the audit
- **WHEN** `python3 tools/audit_questions.py` runs against a state whose `manual_provenance.json` declares `pdf.recovered: false`
- **THEN** the audit passes silently for that state's manual checks (the data gap is acknowledged in the provenance file)

### Requirement: Provenance JSON SHALL declare its schema version

Every `manual_provenance.json` MUST include a top-level `schema_version` integer. The current schema is version `1`, defined in `docs/maintaining-state-data.md` (or equivalent). Future schema changes increment the version; tooling that reads provenance files MUST handle unknown schema versions gracefully (warn, don't crash).

#### Scenario: Tooling rejects malformed provenance
- **WHEN** any tool (`audit_questions.py`, future `verify_provenance.py`) reads a `manual_provenance.json` whose schema fails validation against the declared `schema_version`
- **THEN** the tool reports the specific validation error with the file path, and exits non-zero (for non-CI use) or warns (for CI use)

### Requirement: Multi-source manuals SHALL preserve per-chapter sources

For states whose catalog entry uses the `urls` list field (multi-PDF manuals, e.g., Michigan), each source PDF MUST be committed individually as `manual_part_<n>.pdf` (LFS-tracked) AND concatenated into a canonical `manual.pdf`. The `sources` array in `manual_provenance.json` MUST record one entry per source URL with `url`, `filename`, `size_bytes`, and `sha256`.

#### Scenario: Michigan multi-source onboarding records every chapter
- **WHEN** `setup_state.py` runs against the Michigan catalog entry (which has multiple URLs)
- **THEN** the resulting `data/states/mi/` directory contains `manual.pdf`, `manual_part_1.pdf`, `manual_part_2.pdf`, ..., and `manual_provenance.json` whose `sources` array has one entry per source URL with hashes that match each `manual_part_<n>.pdf` file
