# Maintaining State Driver-Manual Data

How to keep `tools/manual_urls.json` (the catalog) and the per-state YAML
question banks fresh as agencies churn URLs and republish manuals.

## TL;DR

* Edit `tools/manual_urls.json` to add/refresh state metadata. Run
  `python3 tools/verify_manuals.py --update-timestamps` to confirm the URL
  works and stamp `last_verified`.
* To onboard a state from scratch, run
  `python3 tools/setup_state.py --from-catalog <code>` (auto-handles
  single-PDF, multi-PDF, and HTML-index sources).
* The monthly **Manual catalog verification — monthly tracker** GitHub issue
  shows entries that have rotted since the last run; whoever maintains the
  data should triage it.

## `tools/manual_urls.json` schema

```jsonc
[
  {
    // Strict JSON has no comments — schema docs live in this sentinel.
    "_schema_doc": "see docs/maintaining-state-data.md"
  },
  {
    "code": "vt",                        // lowercase 2-letter state code
    "name": "Vermont",                   // display name
    "agency": "DMV",                     // agency that publishes the manual
    "manual_url": "https://dmv.vermont.gov/.../VN-007-Drivers_Manual.pdf",
    "source_description": "Vermont Driver's License Manual (dmv.vermont.gov)",
    "passing_score_pct": 80,             // verified on the official DMV/DOT site
    "test_question_count": 20,           // verified on the official DMV/DOT site
    "edition": "2024-11",                // optional: free-form edition tag
    "last_verified": "2026-04-29",       // optional: written by verify_manuals.py
    "urls": []                           // optional: multi-PDF chapter list (see below)
  }
]
```

### Required fields (real entries)

| Field                  | Type   | Notes                                                             |
| ---------------------- | ------ | ----------------------------------------------------------------- |
| `code`                 | string | Lowercase 2-letter state code. `dc` for District of Columbia.     |
| `name`                 | string | Display name shown in the state-selection UI.                     |
| `agency`               | string | DMV / DOT / DPS / DDS / etc.                                      |
| `manual_url`           | string | Canonical entry-point URL. Shown to users as the source citation. |
| `source_description`   | string | Human-readable citation that appears in the UI footer.            |
| `passing_score_pct`    | int    | Pass threshold as a percentage. Verify on the official site.      |
| `test_question_count`  | int    | Number of questions on the real exam.                             |

### Optional fields

| Field             | Type      | Purpose                                                   |
| ----------------- | --------- | --------------------------------------------------------- |
| `urls`            | list[str] | Multi-PDF manual: ordered list of chapter PDF URLs.       |
| `edition`         | string    | Free-form tag (e.g. `"2025-10"`, `"2025-2027"`).          |
| `last_verified`   | string    | ISO date written by `verify_manuals.py --update-timestamps`. |

### Sentinel object

The leading `_schema_doc` object documents the schema inline (strict JSON has
no comment syntax). `tools/verify_manuals.py:load_catalog` and
`tools/setup_state.py` both skip dicts that lack a `code` field. When you
write back to the catalog via `verify_manuals.save_catalog`, the sentinel is
preserved automatically.

## Verifier (`tools/verify_manuals.py`)

```bash
# Read-only HEAD-check every entry.
python3 tools/verify_manuals.py

# Same, but also write last_verified=<today> for entries that pass.
python3 tools/verify_manuals.py --update-timestamps

# Restrict to specific state codes.
python3 tools/verify_manuals.py --codes mi mn co
```

The verifier:

* Issues `HEAD` with `User-Agent: Mozilla/5.0 (...) drivers-test-verify/1.0`.
  Falls back to a 1KB ranged `GET` when `HEAD` is rejected (some CDNs do
  that).
* Validates HTTP 200 (after redirects), `Content-Type` matches expectation
  (`application/pdf` for `.pdf` URLs; `text/html` allowed for HTML indices),
  and `Content-Length` >= 100 KB.
* Validates the host. Allowlist defaults to `*.gov` plus `*.<state>.us`. A
  small documented exception list (currently `scdmvonline.com`,
  `honolulu.gov`) covers official portals on non-`.gov` hosts. Third-party
  mirror sites (`driving-tests.org`, `dmvquestionbank.com`,
  `usdrivertraining.com`, etc.) are flagged as `suspicious-host`.
* **Always exits 0.** A failed verification doesn't break CI. Drift surfaces
  via the monthly tracking issue instead.

Verdicts in the output column:

| Verdict           | Meaning                                                                    |
| ----------------- | -------------------------------------------------------------------------- |
| `ok`              | Passed all checks — URL still serves a real manual.                        |
| `stale`           | Reachable host but wrong status / content-type / size — URL needs refresh. |
| `suspicious-host` | URL reaches a non-allowlisted host. Find an official replacement.          |
| `error`           | Transport failure (DNS, SSL, timeout). Retry once before assuming dead.    |

## Refreshing a stale URL

1. **Confirm the catalog is stale**:
   ```bash
   python3 tools/verify_manuals.py --codes <code>
   ```
2. **Find the new URL** — pick one of:
   * `python3 tools/find_manuals.py <code>` (Gemini + Google Search).
     Requires Vertex AI auth.
   * Manual web search (`site:dmv.<state>.gov drivers manual PDF`) plus a
     `curl -sIL -A "Mozilla/5.0" '<url>'` to confirm before committing.
3. **Edit `tools/manual_urls.json`** by hand. Update `manual_url`,
   `source_description`, and `edition` for the changed entry.
4. **Re-verify and stamp**:
   ```bash
   python3 tools/verify_manuals.py --codes <code> --update-timestamps
   ```
5. Commit only `tools/manual_urls.json` (one focused commit so the diff is
   reviewable).
6. **Don't regenerate the question bank** unless you also intend to refresh
   the question content. The existing YAML is still grounded in whichever
   edition the bank was generated from. Refreshing the URL keeps the source
   citation accurate without invalidating the questions.

## Multi-PDF manuals

Some agencies (Michigan's `What Every Driver Must Know`, others) publish
the manual as several chapter PDFs rather than one monolith. Configure the
catalog entry with both `manual_url` (canonical landing page, used as the
source citation) and a `urls` array (ordered chapter PDFs):

```jsonc
{
  "code": "mi",
  "manual_url": "https://www.michigan.gov/sos/resources/forms/what-every-driver-must-know",
  "urls": [
    "https://www.michigan.gov/.../WEDMK_Chapter_One_Your_Drivers_License.pdf",
    "https://www.michigan.gov/.../WEDMK_Chapter_Two_Your_Driving_Record.pdf",
    "https://www.michigan.gov/.../WEDMK_Chapter_Three_Voter_Registration.pdf"
  ]
}
```

`tools/setup_state.py` (and the underlying `tools/_manual_fetch.py` helper)
auto-detect the `urls` list and download each in order, then concatenate the
extracted text with `\n\n=== chapter <n> ===\n\n` separators before passing
to `generate_questions.py`.

The verifier HEAD-checks the **first** entry in `urls` only — that's enough
to detect catalog rot without thrashing every chapter URL on every run.

## HTML-index manuals

If a state publishes its manual only as an HTML index page (no PDF), set
`manual_url` to the HTML URL and leave `urls` absent.
`tools/_manual_fetch.fetch_html_text` will scrape the page (BeautifulSoup),
strip nav/header/footer/script/style/aside/form, prefer `<main>`/`<article>`,
and return the visible text.

For a deep multi-page HTML manual, use the `urls` list with the chapter URLs
rather than relying on a single index — explicit ordering avoids surprises.

## Onboarding a new state

```bash
python3 tools/setup_state.py --from-catalog <code>
```

This reads the entry from `tools/manual_urls.json` (so make sure it's
populated and verified first), downloads + extracts the manual text to
`/tmp/<code>_manual_text.txt`, writes `data/states/<code>/config.json`, and
chains into `generate_questions.py` -> `add_sign_questions.py` -> `translate.py
<code> es`. See [`.claude/skills/add-state/SKILL.md`](../.claude/skills/add-state/SKILL.md)
for the full pipeline (audit, bundle, smoke-test).

## Monthly tracking issue

`.github/workflows/verify-manuals.yml` runs the verifier on the 1st of every
month at 07:00 UTC, then opens (or comments on) a long-running GitHub issue
titled "Manual catalog verification — monthly tracker". The issue carries
the verbose verifier output as a collapsible block plus the summary line
(e.g. `summary: error=0 ok=49 stale=2 total=51`).

Triage:

1. Open the latest comment on the tracker issue.
2. For each `stale` / `suspicious-host` / `error` row, follow
   ["Refreshing a stale URL"](#refreshing-a-stale-url).
3. Once the catalog is clean, no issue close is required — the next monthly
   run posts a fresh comment.

The issue is intentionally never auto-closed; the persistent-thread pattern
makes drift visible across months without inbox spam.

## Common gotchas

* **Strip third-party mirror URLs.** Sites like `driving-tests.org`,
  `dmvquestionbank.com`, and `usdrivertraining.com` host identical PDFs but
  are not authoritative. The verifier flags them; refuse to use them as the
  catalog `manual_url`.
* **`.pdf` URLs that return HTML are silently broken.** State sites
  occasionally retarget a stale PDF path to an HTML "page not found" without
  changing the status code. The verifier catches this by requiring
  `Content-Type: application/pdf` for `.pdf` URLs.
* **Tiny 200 responses are usually error pages.** The 100 KB minimum length
  catches most "200 with a 4 KB error landing page" cases. Don't trust a
  refresh that reports a `?`-sized body — that means `Content-Length` was
  missing AND the URL didn't satisfy the size check by other means.
* **`last_verified` does not auto-expire.** A timestamp older than ~90 days
  is a hint to re-run `verify_manuals.py`; the field is informational only.
* **Don't relax the host allowlist.** If a state genuinely serves its manual
  off a non-`.gov` domain (e.g. SC's `scdmvonline.com`), add the bare host
  to `OFFICIAL_HOST_ALLOWLIST_EXCEPTIONS` in `tools/verify_manuals.py` with
  a one-line justification, not by removing the check.
