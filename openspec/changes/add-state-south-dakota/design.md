# Design: SD via Internet Archive snapshot

## Context

`dps.sd.gov` migrated to a ServiceNow-hosted portal in 2025. Every URL under `dps.sd.gov/application/files/*` — including the canonical Dec 2023 driver manual PDF (`sd-driver-manual-rev-12-2023.pdf`) and the older 2018 edition — now `302`-redirects to a JS-rendered shell at `https://www.sd.gov/dps`. No predictable PDF path replaces them. The new portal exposes documents only through a JS-rendered search UI; there is no public catalog endpoint, sitemap, or stable URL pattern observed as of 2026-05-26.

## The recovery question

Three credible sources exist:

| Source | Pros | Cons |
|---|---|---|
| **Wayback Machine snapshot** (`web.archive.org/web/20241125195101/https://dps.sd.gov/.../sd-driver-manual-rev-12-2023.pdf`) | Byte-identical to government original; archive preserves provenance chain; one-shot fetch | Not on the official host; archive could prune in theory; date-frozen |
| **Headless browser scrape of ServiceNow portal** | Pulls the current live document if/when SD re-uploads | Implementation cost (Playwright); fragile to portal changes; out of scope per earlier session note |
| **Third-party mirror** (driving-tests.org, etc.) | Easy to fetch | Republished/reformatted content; violates the "official sources only" rule; would taint precision/recall reports |

## Decision: use the Wayback snapshot, treat as a *recovery*, not a *substitution*

The distinction matters for provenance. We are not saying "the manual is at web.archive.org" — we are saying "the manual was published by SD DPS at `dps.sd.gov/application/files/9717/0863/8492/sd-driver-manual-rev-12-2023.pdf`, and because SD broke that URL we retrieved the same bytes from an Internet Archive capture of that URL."

To preserve this distinction in the data model:

- `manual_url` in the catalog stays pointed at the canonical dead URL. This is the source of truth for "what SD officially published."
- `recovery_url` is a new optional field on the catalog entry. When present, the fetcher prefers it; the verifier uses it as a fallback when the canonical URL fails.
- `manual_provenance.json` records BOTH URLs and sets `extracted_with: "wayback_machine_snapshot"` so any downstream auditor can see exactly how the bytes were obtained.

## Allowlist policy

The existing host allowlist (`OFFICIAL_HOST_ALLOWLIST_EXCEPTIONS` in `tools/verify_manuals.py`) is consulted for `manual_url`. We do **NOT** add `web.archive.org` to that list. The allowlist exists to enforce the official-source rule on `manual_url`; `recovery_url` lives outside that rule by construction. A `recovery_url` is only valid if the canonical `manual_url` it shadows is on an official host — that invariant is checked by the verifier.

## Re-verification cadence

`verify_manuals.py` continues to probe `manual_url` on every run. If SD ever re-publishes a working `dps.sd.gov` (or `www.sd.gov`) PDF, the canonical check will start passing again; at that point a maintainer can drop the `recovery_url` field and refresh the snapshot. The catalog's `last_verified` timestamp tracks this.

## Out of scope

- Headless-browser scraping of the ServiceNow portal. Deferred. If SD's content drifts materially from the Dec 2023 PDF in a future edition, that's the path; until then it's not worth the complexity.
- Generalizing `recovery_url` to other states. Only SD needs it today. The mechanism is general, but the project's catalog doesn't currently have other broken-but-archivable entries. Add when a second case appears.
- DC. DC's situation is materially different (no PDF ever published; Issuu-only) and has no Wayback recovery path. DC stays as a stub, tracked in `TODO_JURISDICTIONS.md`.
