"""Capture mockup screenshots via Playwright. Runs against vite dev server.

Usage:
    python3 docs/design/polish-ui-official-look/_screenshot.py <vite_base_url>

Example:
    python3 docs/design/polish-ui-official-look/_screenshot.py http://127.0.0.1:5175/nj-drivers-test
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).parent

# (output filename, hash route, viewport width, viewport height)
SHOTS: list[tuple[str, str, int, int]] = [
    ("00-tokens.png", "#/tokens", 1200, 760),
    ("01-home-light.png", "#/home/light", 460, 880),
    ("02-state-picker-light.png", "#/picker/light", 460, 880),
    ("03-quiz-light.png", "#/quiz/light", 460, 880),
    ("04-quiz-dark.png", "#/quiz/dark", 460, 880),
    ("05-results-light.png", "#/results/light", 460, 880),
    ("06-stats-light.png", "#/stats/light", 460, 880),
]


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    base = sys.argv[1].rstrip("/")
    target = f"{base}/mock.html"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for filename, route, w, h in SHOTS:
            url = f"{target}{route}"
            print(f"  {filename}  ←  {url}", flush=True)
            ctx = browser.new_context(
                viewport={"width": w, "height": h},
                device_scale_factor=2,
                color_scheme="dark" if "/dark" in route else "light",
            )
            page = ctx.new_page()
            page.goto(url, wait_until="networkidle")
            # Give web fonts an extra beat to settle.
            page.wait_for_timeout(700)
            page.screenshot(path=str(OUT_DIR / filename), full_page=False)
            ctx.close()
        browser.close()

    print(f"\nWrote {len(SHOTS)} screenshots -> {OUT_DIR}")


if __name__ == "__main__":
    main()
