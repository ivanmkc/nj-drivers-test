## Context

The user surfaced the gap on 2026-04-29 while reviewing the GA agent's output: the GA manual was downloaded to `/tmp/ga_manual.pdf` and discarded after question generation, leaving no checked-in evidence of what was generated from. Existing 23 states followed the same pattern. This is a structural problem — fixing GA alone would create an inconsistent project — so the change is project-wide.

The `refresh-manual-catalog` change makes catalog URLs first-class artifacts. This change makes the *content behind those URLs* first-class too. They're complementary: catalog tracks "where to look", provenance tracks "what we actually saw."

## Goals / Non-Goals

**Goals:**
- Every supported state ships with `manual.pdf` (LFS), `manual_text.txt`, `manual_provenance.json`.
- The provenance JSON is sufficient to detect any tampering (SHA-256 over PDF and text) and to reproduce question generation byte-for-byte.
- `setup_state.py` writes these artifacts automatically — no manual steps for new states.
- The audit script catches any state where `manual_provenance.json` doesn't match the actual files.
- Backfill the 23 existing states best-effort.

**Non-Goals:**
- OCR for image-only PDFs. If a state ships scanned-only PDFs (~rare), the text file is empty and the provenance records `text_extraction: "failed-image-only"`. That state's questions remain frozen until the agency publishes an extractable PDF.
- Storing every historical edition. We keep only the *current* edition per state (the one that grounds the live question bank). Older editions are git-history artifacts, not separate files.
- Switching off Git LFS later. Once committed, removing LFS objects requires history rewrite. Decide LFS-or-not once and live with it.
- Auto-refreshing manuals on a schedule. That's a `refresh-manual-catalog` concern (the verifier flags stale entries; humans decide when to re-onboard).
- Building a UI for browsing manuals. They're files; `open` works.
- Refactoring `generate_questions.py` to read from `data/states/<code>/manual_text.txt` instead of taking a path argument. That's a useful follow-up but out of scope here.

## Decisions

**1. Provenance schema.** Versioned via `schema_version`, single-PDF and multi-PDF use the same shape (multi-PDF uses a non-empty `sources` array):

```json
{
  "schema_version": 1,
  "code": "ga",
  "name": "Georgia",
  "agency": "DDS",
  "manual_url": "https://dds.georgia.gov/document/document/ga-drivers-manual-2023-2024/download",
  "edition": "2023-2024",
  "source_description": "Georgia Driver's Manual (dds.georgia.gov)",
  "downloaded_at": "2026-04-29T03:46:00Z",
  "extracted_with": "PyMuPDF 1.24.0",
  "pdf": {
    "filename": "manual.pdf",
    "size_bytes": 15416935,
    "sha256": "107ac52a...",
    "page_count": 52,
    "recovered": true,
    "compression": {
      "tool": "ghostscript",
      "preset": "ebook",
      "command": "gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -dCompatibilityLevel=1.4 -dNOPAUSE -dQUIET -dBATCH",
      "original_size_bytes": 49586555,
      "original_sha256": "e311de54..."
    }
  },
  "text": {
    "filename": "manual_text.txt",
    "char_count": 234086,
    "sha256": "def456..."
  },
  "sources": []
}
```

For multi-source (Michigan):

```json
{
  ...
  "pdf": {
    "filename": "manual.pdf",
    "note": "concatenated from sources[]",
    "size_bytes": 12345678,
    "sha256": "...",
    "page_count": 200,
    "recovered": true
  },
  "sources": [
    {
      "url": "https://www.michigan.gov/-/.../WEDMK_Chapter_One.pdf",
      "filename": "manual_part_1.pdf",
      "size_bytes": 1234567,
      "sha256": "..."
    },
    ...
  ]
}
```

**2. Git LFS, originals only — NO compression.** Decision: yes LFS, despite the contributor-prerequisite cost. PDFs are committed **as downloaded from the source agency**, with no compression layer.

Why no compression:
- Empirical: PDFs are already deflated internally. Generic lossless compression on GA's 49.5 MB original:
  - `gzip -9` → 45.1 MB (-4.6%)
  - `xz -9e` → 45.0 MB (-4.9%)
  - `zstd -22` → 44.9 MB (-5.0%)
  - `tar.gz` bundle (pdf+text+json) → 45.2 MB (-4.4%)
- The only thing that *meaningfully* shrinks a PDF is image downsampling via Ghostscript `/ebook` (-70% on GA), which is **lossy**. An earlier version of this design mandated gs `/ebook`; that decision was reverted on 2026-04-29 in favor of lossless preservation.
- 4-5% savings doesn't justify the tooling/policy complexity (Ghostscript prereq, smaller-or-skip rule, compression metadata in provenance, audit-script special-cases). Keep it simple.
- Storage estimate: 51 originals × ~30 MB avg = **~1.5 GB in LFS**. GitHub free tier is 1 GB; expect to need a paid LFS plan or sponsor once we cross ~30 states.
- Why LFS even without compression? 30 MB per file × ~2 revisions/year × 51 states = ~3 GB of history per year if stored as plain Git blobs. LFS keeps clones fast forever.
- Tradeoff: contributors must install `git lfs` (one-time, free). No Ghostscript prereq. Documented in README and `docs/maintaining-state-data.md`.
- Why not skip PDFs and only store text? Text alone loses original formatting, page numbers, image references, and the ability to verify extraction was correct. Reviewers should be able to open the PDF and visually confirm a question's source.

**2a. No `compression` sub-object in provenance.** Earlier drafts of this design used a `pdf.compression` sub-object to record the gs preset, original size, and original SHA-256. With compression removed from the policy, that field is no longer used. Provenance files written before this revision (and any worktrees that haven't been reverted yet) MAY still include the field — readers MUST tolerate it for backward compatibility. The audit script verifies `pdf.sha256` against the actual file bytes; that's all it needs.

**2b. Migration: existing gs-compressed worktrees revert to originals.** As of 2026-04-29, GA + MI + CO + SC + 21 backfilled states had been onboarded with gs-compressed PDFs (the prior policy). A revert pass re-downloads each state's original from `manual_url`, replaces `manual.pdf`, re-extracts text, and removes `compression` from provenance. AZ (compression skipped from the start) and MN (already reverted via the obsolete smaller-or-skip rule) need no further action.

**3. Text file is normal-tracked, NOT gzipped, NOT LFS.**
- Text files are small (~200-500KB each, ~12MB total for 51 states), diff-friendly, and grep-friendly.
- Putting text in LFS would defeat the audit value (can't grep an LFS pointer).
- gzip on text gives ~67% savings (228 KB → 76 KB on GA), but only ~0.7% of total per-state size after PDF compression. Not worth requiring tools to pipe through `gunzip`. Keep grep-able.

**4. SHA-256 in provenance, not just file size.**
- SHA-256 catches tampering; file size doesn't.
- Cheap to compute (~50ms per PDF), zero ongoing cost.
- The audit script extension recomputes SHA-256s on every audit run and fails on mismatch.

**5. Multi-source PDFs are concatenated into a canonical `manual.pdf` AND kept individually as `manual_part_<n>.pdf`.**
- The canonical `manual.pdf` is what the question generator reads. Single source of truth.
- The per-chapter parts are kept for traceability (which chapter each question came from).
- Increases LFS storage by ~2x for multi-source states. Acceptable.

**6. Backfill is best-effort, not blocking.**
- Try the (refreshed) `manual_url` for each of the 23 existing states.
- If it works: hash, write provenance, commit. State now meets the new requirement.
- If it doesn't (URL rotted past recovery): write a stub provenance with `pdf.recovered: false` and `note: "<reason>"`. State stays in compliance via the stub; question bank is left alone (it's still grounded — we just can't re-verify the source bytes).
- Don't regenerate any state's question bank during backfill.

**7. `audit_questions.py` extension is non-strict for backfilled states with `recovered: false`.**
- Hard fail if the SHA mismatches a *recovered* manual (tampering signal).
- Soft warn if the manual is missing entirely on a recovered-true entry.
- Pass silently if `recovered: false` (acknowledged data gap).

**8. `.gitignore` cleanup**: remove the legacy `drivermanual.pdf` and `manual_text.txt` patterns. They were holdovers from the NJ-only era, before per-state directories existed.

## Risks / Trade-offs

- **Risk: Git LFS quota overflow on GitHub free tier.** Mitigation: monitor usage; document the limit in README; budget for paid plan once crossed. Fallback: switch to LFS-on-S3 via `lfs.url` config.
- **Risk: contributors don't have `git lfs` installed and silently commit LFS-mode files as raw bytes** (corrupting both git history and the LFS object). Mitigation: pre-commit hook or CI gate that rejects PRs containing oversized blobs in `data/states/*/manual.pdf`. Document the prereq prominently.
- **Risk: state agencies may have terms-of-use restricting redistribution.** Reality check: every state DMV manual checked has been published as US government work or public information without redistribution restrictions. If a specific state has restrictions, set `pdf.recovered: false` with a note and don't commit the PDF. Text-only is also fine for the rare restricted case.
- **Risk: large PDF rev churn.** Each new manual edition rewrites the LFS object. ~1-2 revisions per state per year × 51 states = ~100 LFS object writes/year; well within paid LFS plan limits.
- **Trade-off: storing multi-source twice (concatenated + parts)** doubles storage for those states. Accepted because the concatenated PDF is the canonical input and the parts are the canonical sources.
- **Trade-off: SHA-256 in provenance means any whitespace change to text invalidates the audit.** Accepted because that's the *point* — extraction must be deterministic.
- **Open question: do we need a `tools/refresh_manual.py` to re-download a single state's manual without going through the full setup_state.py pipeline?** Probably yes eventually, but not in this change — just use `setup_state.py --re-fetch <code>` for now.
