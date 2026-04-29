## Context

After `add-state-georgia` lands, we still owe 27 states. Doing them serially as one-off PRs is wasteful: each PR repeats the same URL hunt, the same "is this PDF text-extractable?" check, the same multi-PDF workaround if applicable. The bottleneck isn't the per-state question generation — Gemini handles that fine — it's the **upstream sourcing problem**.

This design proposes treating the catalog as a first-class artifact with its own verification lifecycle, then onboarding states in waves grouped by manual structure so each wave surfaces a distinct class of bug at most once.

Empirical evidence the catalog is broken (HEAD-checked 2026-04-29):

| State | URL ext | HTTP | Issue |
|-------|---------|------|-------|
| GA    | /download | 404 | dead |
| MI    | .pdf    | 302→404 | moved, now multi-PDF |
| AZ    | .pdf    | 404 | dead |
| CO    | .pdf    | 403 | UA-blocked |
| MN    | .pdf    | 200 (HTML!) | wrong content-type |
| CT    | .pdf    | 200 (HTML!) | wrong content-type |
| LA    | NotesDB | n/a | not a PDF link |

That's 7/7 of the top-population missing states broken. The catalog can't be trusted.

## Goals / Non-Goals

**Goals:**
- A `tools/manual_urls.json` where every URL has been HTTP-verified within the last N days, with `last_verified` timestamps to prove it.
- A `setup_state.py` that handles single-PDF, multi-PDF, and HTML-index manual sources without per-state special cases.
- All 50 states + DC onboarded (23 existing + GA from prior change + 27 from this change).
- An ongoing process (CI job + maintenance doc) so the catalog stays fresh after this change ships.

**Non-Goals:**
- OCR for image-based PDFs. If a state ships only scanned PDFs, document it as out-of-scope and skip until the agency publishes text-based ones. (Suspected: maybe 1-2 small states. Address per-state if it becomes a real blocker.)
- Re-generating the question banks for the 23 already-done states, even if their URLs have drifted. Their existing question banks are still grounded in the prior edition; a separate change can refresh content when desired.
- Translating every new state to es. Each wave's translation work is best-effort — en is required, es is high-value for most states. JA translation is no longer in scope (preference recorded 2026-04-29).
- Cleaning up or restructuring the existing question generation prompt.
- Adding new question categories.
- Building a UI for catalog management. CLI + JSON file are sufficient.

## Decisions

**1. `manual_urls.json` schema evolves backward-compatibly.**

```json
{
  "code": "mi",
  "name": "Michigan",
  "agency": "SOS",
  "manual_url": "https://www.michigan.gov/sos/resources/forms/what-every-driver-must-know",
  "urls": [
    "https://www.michigan.gov/-/media/.../WEDMK_Chapter_One_Your_Drivers_License.pdf",
    "https://www.michigan.gov/-/media/.../WEDMK_Chapter_Two_Your_Driving_Record.pdf"
  ],
  "source_description": "What Every Driver Must Know (Oct 2025 ed.)",
  "edition": "2025-10",
  "last_verified": "2026-05-15",
  "passing_score_pct": 80,
  "test_question_count": 50
}
```

`manual_url` (singular) remains the canonical entry point shown in the UI/source citation. `urls` (plural) is optional; when present, `setup_state.py` downloads each, extracts text, and concatenates. When absent, behavior is identical to today.

**2. Verification is HEAD-only, with a fixed User-Agent.**

`tools/verify_manuals.py` issues `HEAD` requests with `User-Agent: Mozilla/5.0` (some state CDNs block default curl). It checks:
- HTTP 200 (after redirects)
- `Content-Type: application/pdf` for `.pdf` URLs, `text/html` for HTML index pages
- `Content-Length > 100KB` (catches the "200-but-tiny-error-page" pattern)

A failed verification doesn't block CI — it opens (or updates) a single tracking issue listing all stale entries, and updates `last_verified` to a sentinel timestamp.

**3. Wave grouping is by manual structure, not population.**

Population-sorted waves would mean tackling the hardest cases (multi-PDF MI, HTML-only GA) first while still building tooling. Structure-sorted waves let us validate the simple path first, then progressively exercise the harder paths:

- **Wave 1 — single-PDF, low risk** (7 states): VT, WY, ND, SD, AK, DC, DE. Small populations, simple manuals, mostly text-PDF. If anything breaks here, it's a pipeline regression, not a state-specific quirk.
- **Wave 2 — single-PDF, broader coverage** (13 states): UT, AR, CT, OK, NH, NM, NE, ID, WV, RI, ME, HI, MT. Same code path, just more volume.
- **Wave 3 — multi-PDF or HTML-only** (7 states): MI, MN, AZ, CO, SC, MS, LA. Exercises the new multi-source extraction path. Highest-population states are here, so the value is highest, but the risk is too — do them last when the pipeline is proven.

**4. CI verification cadence: monthly, on a schedule, non-blocking.**

GitHub Actions cron `0 7 1 * *` (1st of month, 07:00 UTC). Job runs `verify_manuals.py`, posts results as a comment on a long-running tracking issue (one issue, updated each run), and labels stale entries. Doesn't fail PR builds. Doesn't auto-update URLs (avoids silent drift to the wrong manual edition).

**5. Translations: en required per wave; es batched at end of each wave. JA dropped.**

Running translations inline per state burns Gemini budget. Better: complete en for the whole wave, then run a bulk `translate.py --all-pending es`. Catches translation failures in one place. JA is no longer in scope.

**6. Audit threshold stays unchanged.**

`tools/audit_questions.py` already enforces "every question must cite manual source." No change here. If a wave introduces a state where the audit consistently fails, that's a manual-quality issue, not an audit-rule issue — re-extract the manual.

## Risks / Trade-offs

- **Risk: Gemini-with-Search re-finds a third-party mirror as the "official" PDF.** Mitigation: `verify_manuals.py` rejects any URL whose host doesn't match a known state-agency domain pattern (`*.gov`, `dot.<state>.gov`, etc.). Maintain a small allowlist alongside the catalog.
- **Risk: multi-PDF concatenation produces text with repeated TOCs / page-number garbage** that confuses the LLM into generating duplicate questions. Mitigation: in Wave 3, manually review one MI question file before approving the wave; if duplicates appear, add a dedup pass before generation.
- **Risk: scope creep.** The temptation will be to also rewrite `generate_questions.py`, refresh the existing 23 states' content, build a UI for the catalog, etc. None of those are in this change. Keep them out.
- **Trade-off: monthly CI verification adds maintenance noise** (a tracking issue that updates every month). Accepted because the alternative — discovering the catalog is dead next time someone tries to onboard a state — is worse.
- **Trade-off: backward-compat `manual_url` + `urls` dual schema** is slightly ugly. Could deprecate `manual_url` and require `urls` always. Rejected: the singular `manual_url` is what gets shown to users in citations ("source: 2026 California Driver Handbook (dmv.ca.gov)") and is the canonical entry point even when content is split. Keep both.
- **Risk: HEAD requests get rate-limited or blocked entirely on some state CDNs.** Mitigation: spread checks across the day; back off on 429; if a host consistently blocks HEAD, fall back to GET with `Range: bytes=0-1023` to fetch only the first KB.
- **Open question: who owns the monthly tracking issue?** Probably whoever merged this change. Document in the maintenance doc but accept that an unowned issue may rot. The CI job's value is making rot visible; it doesn't promise to fix it automatically.
