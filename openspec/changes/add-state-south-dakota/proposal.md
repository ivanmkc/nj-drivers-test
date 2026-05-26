## Why

South Dakota is one of two jurisdictions still missing (the other is DC). It currently exists as a stub at `data/states/sd/manual_provenance.json` with `recovered: false`. The catalog URL `https://dps.sd.gov/application/files/9717/0863/8492/sd-driver-manual-rev-12-2023.pdf` (verified working April 2026) now hard-redirects to a JS-rendered ServiceNow portal at `https://www.sd.gov/dps`. *Every* `dps.sd.gov/application/files/*` URL — including the 2018 edition — 302-redirects to the same shell, so this is not a moved-file problem; SD migrated document hosting away from the path tree the canonical URLs live on.

There is, however, a clean recovery path. The Internet Archive holds a byte-identical snapshot of the canonical PDF captured 2024-11-25 (`Content-Length: 2364323`, `Content-Type: application/pdf`). The bytes are SD's, just retrieved through `web.archive.org` instead of `dps.sd.gov`. Using this snapshot is meaningfully different from a third-party study-guide site like driving-tests.org: the archive preserves *the government's published document* (same hash, same edition, same publication date), it does not republish summarized content.

DC has no equivalent recovery path — the Auto Driver Manual was only ever published as an Issuu flipbook and has zero PDF captures in Wayback's CDX index. So SD is the single tractable state to onboard now, getting us to 50/51 with one PR.

## What Changes

- **Catalog**: add a `recovery_url` field to the SD entry in `tools/manual_urls.json` pointing to the Wayback snapshot. Keep `manual_url` as the canonical dead URL so future re-verification will detect if SD republishes.
- **Verifier**: teach `tools/verify_manuals.py` to honor `recovery_url` — when the canonical URL fails but `recovery_url` returns a valid PDF, mark the entry as `recovered` (a new status, distinct from `ok` and `stale`).
- **Fetcher**: teach `tools/_manual_fetch.py` to prefer `recovery_url` over `manual_url` when present.
- **Pipeline**: run `setup_state.py --from-catalog sd` → `generate_questions.py` → `add_sign_questions.py` → `translate.py sd es`, producing `data/states/sd/{config.json,questions_en.yaml,questions_es.yaml}` grounded in the Dec 2023 manual.
- **Provenance**: replace the existing `data/states/sd/manual_provenance.json` stub with a full record that names BOTH URLs (intended `dps.sd.gov/...`, actual `web.archive.org/...`) and records `extracted_with: "wayback_machine_snapshot"`.
- **Quality**: run `quiz_gates.py sd --write-report` (precision/recall/coverage). Must hit Grade A or B.
- **Docs**: flip SD checkbox in `TODO_JURISDICTIONS.md` (49 → 50). Add SD section to `SOURCES.md` documenting the archive-recovery exception with the snapshot timestamp.

## Capabilities

### New Capabilities
<!-- None — adds a new state requirement under supported-states. -->

### Modified Capabilities
<!-- The catalog/verifier/fetcher tweaks support the supported-states requirement; they're small enough to live in this change rather than splitting an infra-only proposal. -->

## Impact

- **Data**: new question banks in `data/states/sd/`; replaces existing stub.
- **Catalog**: one entry gains a `recovery_url` field; no new exception added to the host allowlist (Wayback URLs are routed through `recovery_url`, not `manual_url`, so the allowlist is never consulted for them).
- **Code**: ~30 LOC across `_manual_fetch.py` (prefer recovery_url) and `verify_manuals.py` (new `recovered` status). No public-API change.
- **Depends on**: nothing (no in-flight infra changes are touching the catalog or fetcher).
- **Risk**: the Dec 2023 edition is now ~2.5 years old. SD's actual written test may have evolved (point system, fees, distracted-driving statutes change frequently). Mitigation: `quiz_gates` is run against the snapshot, so questions are faithful to the published document; staleness vs. live test is a known acceptance.
- **Spot-check focus**: SD content unique enough that fabrication would be detectable — winter-driving rules (no studs Apr 16 – Sep 30), graduated licensing minimums (14 yr instruction permit), wildlife-collision protocol (deer are abundant), and gravel-road handling.
