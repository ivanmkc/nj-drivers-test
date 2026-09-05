"""Generate the static About / Privacy / Support / 404 pages for the web app.

The pages are plain HTML with inline CSS (light + dark), written into
frontend/public/ so Vite copies them into the GitHub Pages artifact. The About
page is built from data/states/*/config.json and verification_report.json so
the public source list never drifts from what the app ships.

Usage:
    python3 tools/build_site_pages.py
"""

from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATES_DIR = ROOT / "data" / "states"
OUT = ROOT / "frontend" / "public"

SITE_URL = "https://ivanmkc.github.io/nj-drivers-test/"
REPO_URL = "https://github.com/ivanmkc/nj-drivers-test"
ISSUES_URL = f"{REPO_URL}/issues/new"
APP_NAME = "Driver's Test Prep"
BASE = "/nj-drivers-test/"

CSS = """
:root{color-scheme:light dark;--bg:#F9FAFB;--fg:#111827;--muted:#6B7280;--card:#FFFFFF;--border:#E5E7EB;--primary:#1A56DB;--primary-soft:#E8F0FE}
@media (prefers-color-scheme:dark){:root{--bg:#111827;--fg:#F9FAFB;--muted:#9CA3AF;--card:#1F2937;--border:#374151;--primary:#5B8DEF;--primary-soft:#1E293B}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:44rem;margin:0 auto;padding:1.5rem 1rem 4rem}header{display:flex;align-items:center;gap:.75rem;margin-bottom:1.5rem}
header img{width:40px;height:40px;border-radius:9px}header a{color:inherit;text-decoration:none;font-weight:600}
h1{font-size:1.75rem;line-height:1.2;margin:.5rem 0 1rem}h2{font-size:1.2rem;margin:2rem 0 .5rem}h3{font-size:1rem;margin:1.25rem 0 .25rem}
.muted{color:var(--muted)}a{color:var(--primary)}
table{width:100%;border-collapse:collapse;font-size:.9rem}th,td{text-align:left;padding:.45rem .5rem;border-bottom:1px solid var(--border);vertical-align:top}
th{color:var(--muted);font-weight:600}.wrap{overflow-x:auto;border:1px solid var(--border);border-radius:12px;background:var(--card)}
.note{background:var(--primary-soft);border-radius:12px;padding:.75rem 1rem;margin:1rem 0}
footer{margin-top:3rem;font-size:.8rem;color:var(--muted)}footer a{margin-right:1rem}
.btn{display:inline-block;background:var(--primary);color:#fff;padding:.6rem 1.1rem;border-radius:10px;text-decoration:none;font-weight:600}
"""


def page(title: str, body: str, description: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · {APP_NAME}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="icon" href="{BASE}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{BASE}icons/icon-180.png">
<meta name="theme-color" content="#1A56DB">
<style>{CSS}</style>
</head>
<body>
<main>
<header><img src="{BASE}icons/icon-192.png" alt=""><a href="{BASE}">{APP_NAME}</a></header>
{body}
<footer>
<a href="{BASE}">App</a><a href="{BASE}about/">About &amp; sources</a><a href="{BASE}privacy/">Privacy</a><a href="{BASE}support/">Support</a><a href="{REPO_URL}">Source code</a>
<p>Unofficial study aid. Not affiliated with or endorsed by any state motor vehicle agency.</p>
</footer>
</main>
</body>
</html>
"""


def load_states() -> list[dict]:
    rows = []
    for d in sorted(STATES_DIR.iterdir()):
        cfg_path = d / "config.json"
        if not cfg_path.is_file():
            continue
        cfg = json.loads(cfg_path.read_text())
        report = {}
        rp = d / "verification_report.json"
        if rp.is_file():
            report = json.loads(rp.read_text())
        n_questions = 0
        yaml_en = d / "questions_en.yaml"
        if yaml_en.is_file():
            n_questions = sum(
                1 for line in yaml_en.read_text().splitlines() if line.startswith("  - id:")
            )
        langs = [p.stem.split("_")[1].upper() for p in sorted(d.glob("questions_*.yaml"))]
        rows.append(
            {
                "code": cfg["code"].upper(),
                "name": cfg["name"],
                "agency": cfg.get("agency", ""),
                "source": cfg.get("source", ""),
                "manual_url": cfg.get("manual_url", ""),
                "questions": n_questions,
                "langs": ", ".join(langs),
                "grade": report.get("overall_grade", ""),
                "verified": (report.get("verified_at") or "")[:10],
            }
        )
    return rows


def about_page(states: list[dict], today: str) -> str:
    shipped = [s for s in states if s["questions"]]
    total_q = sum(s["questions"] for s in shipped)
    rows = "\n".join(
        '<tr><td>{code}</td><td>{name}</td><td>{agency}</td><td><a href="{url}" rel="noopener">{src}</a></td><td>{q}</td><td>{langs}</td><td>{grade}</td></tr>'.format(
            code=s["code"],
            name=html.escape(s["name"]),
            agency=html.escape(s["agency"]),
            url=html.escape(s["manual_url"]),
            src=html.escape(s["source"] or s["manual_url"]),
            q=s["questions"] or "coming soon",
            langs=s["langs"],
            grade=s["grade"],
        )
        for s in states
    )
    repo_short = REPO_URL.replace("https://", "")
    body = f"""
<h1>About this app and its sources</h1>
<p>{APP_NAME} is a free, offline practice tool for the written knowledge test you take to get a learner's permit or driver's license in the United States. It is an independent project. <strong>It is not published by, affiliated with, or endorsed by any state motor vehicle agency</strong>, and passing a practice quiz here does not guarantee a result on the real test.</p>

<h2>Where the questions come from</h2>
<p>Every question is generated from the text of the <em>official driver manual</em> published by each state's licensing agency, using a language model that is given the manual as its only source. Questions are never written from general knowledge. Each state's bank is then checked against the manual in two ways:</p>
<ul>
<li><strong>Faithfulness:</strong> every question is judged against the manual text and must be directly supported by it; questions that are not are removed.</li>
<li><strong>Coverage:</strong> the must-know topics extracted from the manual must each be covered by at least one question.</li>
</ul>
<p>The grade in the table below summarises that check (A = passed both gates). In the app, the "About this test" panel shows the same information for your state, and each answered question shows the manual passage that supports it.</p>

<div class="note">Driving rules differ between states. Only questions about standard road signs are shared; everything else comes from your own state's manual, so always practise with the state you will be tested in.</div>

<h2>Source manuals ({len(shipped)} jurisdictions, {total_q:,} questions)</h2>
<div class="wrap"><table>
<thead><tr><th>Code</th><th>State</th><th>Agency</th><th>Official manual</th><th>Questions</th><th>Languages</th><th>Grade</th></tr></thead>
<tbody>
{rows}
</tbody></table></div>
<p class="muted">Links go to the agency's own website. Agencies move and republish manuals; the catalog is re-checked monthly and each state's edition is shown in the app. Manuals are the copyright of their respective agencies and are used here as the factual basis for study questions.</p>

<h2>Languages</h2>
<p>English banks are the reference. Spanish banks are machine-translated from the English bank and checked for faithfulness against it. A few states also carry older Japanese banks. The app marks a language as an <em>official test language</em> only where the state's own manual says the knowledge test is offered in it; every other language is labelled as practice-only. Check with your agency before relying on a non-English test.</p>

<h2>Road sign images</h2>
<p>Sign images are standard signs from the Manual on Uniform Traffic Control Devices (MUTCD), a US government work in the public domain, via Wikimedia Commons.</p>

<h2>Open source</h2>
<p>The app, the question-generation pipeline, and all question data are public at <a href="{REPO_URL}">{repo_short}</a>. Found a wrong or outdated question? <a href="{ISSUES_URL}">Open an issue</a> with the state, the question text, and the manual page it should match.</p>
<p class="muted">Last generated {today}.</p>
"""
    return page(
        "About & sources",
        body,
        f"How {APP_NAME} builds its practice questions from official state driver manuals, "
        "with the full list of sources.",
    )


def privacy_page(today: str) -> str:
    repo_short = REPO_URL.replace("https://", "")
    body = f"""
<h1>Privacy policy</h1>
<p class="muted">Effective {today}. Applies to the {APP_NAME} iOS app, Android app, and website.</p>

<h2>The short version</h2>
<p><strong>{APP_NAME} does not collect, transmit, sell, or share any personal data.</strong> There are no accounts, no analytics, no advertising, no crash reporting, and no third-party SDKs. The apps work entirely offline.</p>

<h2>What is stored on your device</h2>
<p>To show your progress, the app keeps a small amount of data locally on your device only:</p>
<ul>
<li>the state and language you selected,</li>
<li>which questions you have seen and how many times you answered each one incorrectly,</li>
<li>your quiz score history,</li>
<li>your light/dark theme preference (website only).</li>
</ul>
<p>On iOS this lives in the app's UserDefaults; on Android in the app's SharedPreferences; on the website in your browser's localStorage. None of it leaves your device. You can erase it at any time with <em>Reset all data</em> on the Stats screen, by deleting the app, or by clearing site data in your browser.</p>

<h2>Network access</h2>
<p>The iOS and Android apps make no network requests: all questions and images are bundled inside the app. The website is served from GitHub Pages, which, like any web host, receives your IP address and standard request logs when the page loads. See <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener">GitHub's privacy statement</a> for how GitHub handles that.</p>

<h2>Children</h2>
<p>The app does not knowingly collect any data from anyone, including children under 13.</p>

<h2>Changes</h2>
<p>If this policy changes, the new version will be published at this address with a new effective date.</p>

<h2>Contact</h2>
<p>Questions about privacy can be raised publicly at <a href="{ISSUES_URL}">{repo_short}/issues</a>.</p>
"""
    return page(
        "Privacy policy",
        body,
        f"{APP_NAME} collects no personal data. Progress is stored only on your device.",
    )


def support_page() -> str:
    body = f"""
<h1>Support</h1>
<p>{APP_NAME} is a free, open-source project. Support is provided through the public issue tracker.</p>
<p><a class="btn" href="{ISSUES_URL}">Report a problem or wrong question</a></p>

<h2>Frequently asked questions</h2>

<h3>A question or answer looks wrong.</h3>
<p>Please report it. Include the state, the language, the question text, and if possible the page of the official manual that shows the correct rule. Every question is generated from the manual and re-checked against it, but manuals change and generation is not perfect. Reported questions are corrected or removed in the next data release.</p>

<h3>Is this the real test?</h3>
<p>No. This is an unofficial study aid built from the same manual your agency publishes. The real knowledge test is written by your state's licensing agency, and its exact questions are not public. Use this app to learn the material, then read the manual.</p>

<h3>Which language will my real test be in?</h3>
<p>That depends on your state. Where the state's manual says the knowledge test is offered in a language, the app marks that language as official for that state. Where it does not, the language is labelled practice-only and you should confirm with your agency before test day.</p>

<h3>Does the app need internet?</h3>
<p>The iOS and Android apps do not. The website needs a connection to load the first time.</p>

<h3>Where is my progress stored? Can I sync it?</h3>
<p>Progress is stored only on the device you use. There is no account or sync. See the <a href="{BASE}privacy/">privacy policy</a>.</p>

<h3>My state is missing or "coming soon".</h3>
<p>The District of Columbia does not publish its manual as a downloadable document, so it has no question bank yet. All 50 states are available.</p>

<h3>How do I delete my data?</h3>
<p>Open Stats and choose <em>Reset all data</em>, or uninstall the app. On the website, clear site data for this site in your browser.</p>
"""
    return page("Support", body, f"Help and frequently asked questions for {APP_NAME}.")


def not_found_page() -> str:
    body = f"""
<h1>Page not found</h1>
<p>There is nothing at this address. The app lives at the link below.</p>
<p><a class="btn" href="{BASE}">Open {APP_NAME}</a></p>
"""
    return page("Not found", body, "Page not found.")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  {path.relative_to(ROOT)}")


def main() -> None:
    today = dt.date.today().isoformat()
    states = load_states()
    print("Writing site pages...")
    write(OUT / "about" / "index.html", about_page(states, today))
    write(OUT / "privacy" / "index.html", privacy_page(today))
    write(OUT / "support" / "index.html", support_page())
    write(OUT / "404.html", not_found_page())
    print("Done.")


if __name__ == "__main__":
    main()
