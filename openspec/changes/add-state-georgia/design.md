## Context

Georgia DDS recently restructured their manual hosting. The catalog URL (`https://dds.georgia.gov/document/manual/georgia-drivers-manual/download`) returns 404. The current entry points found via search:

- `https://dds.georgia.gov/drivers-manual` — landing page (HTML)
- `https://dds.georgia.gov/dds-forms-and-manuals/manuals` — manuals index (HTML)
- `https://dds.georgia.gov/drivers-manual-contents` — chapter-by-chapter table of contents
- `https://dds.georgia.gov/georgia-department-driver-services-drivers-manual-2023-2024` — archived 2023-2024 edition reference

We need to navigate from one of these to a current PDF (or scrape the chapter pages to text).

## Goals / Non-Goals

**Goals:**
- One working `data/states/ga/` directory with grounded questions, audited and bundled.
- A verified `manual_url` in `tools/manual_urls.json` that resolves with HTTP 200 and returns either `application/pdf` or scrapeable HTML.
- Clear notes on multi-PDF handling (if encountered) so the follow-up `refresh-manual-catalog` change can lift the workaround into a real pipeline feature.

**Non-Goals:**
- Generalizing multi-PDF support, scraping helpers, or catalog-verification tooling. That belongs in `refresh-manual-catalog`.
- Adding any other state. One state, one pipeline run, one PR.
- Re-verifying the URLs of the 23 already-done states.
- Hand-editing questions to compensate for poor manual extraction — if extraction is bad, fix extraction.

## Decisions

**1. Manual source: try PDF first, fall back to chapter HTML scrape.**
   - First attempt: search `dds.georgia.gov` and the manuals index page for any link ending in `.pdf`. If exactly one current-edition PDF exists, use it.
   - Fallback: fetch each chapter URL listed under `/drivers-manual-contents`, concatenate into a single text file, point `manual_url` at the contents page (since that's the canonical entry), and keep the chapter URLs in this design doc for traceability.
   - If only third-party mirrors host the PDF: do **not** use them. The "ground in official sources" rule is non-negotiable.

**2. Translations: en is required; es is high-value (Georgia has ~1M Spanish speakers); ja is optional.**
   - Run `translate.py ga es`. Skip `ja` if rate-limited or if it adds significant time — it can be added later without blocking ship.

**3. Sign images: reuse shared MUTCD set first; only extend `data/signs/` if a Georgia-specific sign appears in the manual and isn't already covered.**
   - Most state-specific signage is just MUTCD with state branding (e.g., "Welcome to Georgia"). These don't need to be question targets.

**4. Audit threshold: every generated question must cite a manual page or chapter in its `explanation` field.**
   - The audit script already enforces this. Don't relax it.

## Risks / Trade-offs

- **Risk: multi-PDF concatenation produces garbage text** (e.g., page-number artifacts, repeated chapter headers confuse the LLM). Mitigation: spot-check the extracted text before generation; if it's noisy, do a one-off cleanup with sed/awk and document the regex in this design.
- **Risk: 75% pass rate / 40-question test** surfaces a bug in the bundle's per-state config plumbing that 80%/varied-count states didn't hit. Mitigation: explicitly test on iOS, Android, and web that the GA test session uses the right thresholds.
- **Trade-off: doing this single-state work without first refreshing the whole catalog means some throwaway URL-hunting effort.** Accepted because (a) we need at least one fresh end-to-end pipeline run before scaling up, and (b) the catalog refresh proposal benefits from the lessons learned here.
- **Risk: GA manual revisions mid-2026** invalidate the URL again. Out of scope for this change — `refresh-manual-catalog` introduces ongoing verification.
