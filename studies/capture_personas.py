"""Capture persona-flow screenshots from the live deployed app for the UX study."""

import os

from playwright.sync_api import ViewportSize, sync_playwright

BASE = "https://ivanmkc.github.io/nj-drivers-test/"
OUT = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT, exist_ok=True)

MOBILE = ViewportSize(width=390, height=844)
DESKTOP = ViewportSize(width=1440, height=900)


def shot(pg, name):
    pg.screenshot(path=os.path.join(OUT, f"{name}.png"), full_page=False)
    print("captured", name)


def open_state(ctx, state_name):
    pg = ctx.new_page()
    pg.goto(BASE)
    pg.wait_for_selector(f"text={state_name}", timeout=30000)
    pg.locator("button", has_text=state_name).first.click()
    pg.wait_for_selector("text=About this test", timeout=15000)
    return pg


def answer_one(pg):
    pg.evaluate(
        "[...document.querySelectorAll('button')]"
        ".find(b=>/^[A-D]\\b/.test(b.innerText.trim()))?.click()"
    )
    pg.wait_for_timeout(700)


with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox"])

    # --- Jordan: mobile light, NJ, first-time flow ---
    ctx = browser.new_context(color_scheme="light", viewport=MOBILE)
    pg = ctx.new_page()
    pg.goto(BASE)
    pg.wait_for_selector("text=New Jersey", timeout=30000)
    shot(pg, "jordan-01-statepicker")
    pg.locator("button", has_text="New Jersey").first.click()
    pg.wait_for_selector("text=About this test", timeout=15000)
    shot(pg, "jordan-02-home")
    pg.locator("text=About this test").click()
    pg.wait_for_timeout(500)
    shot(pg, "jordan-03-about-expanded")
    pg.locator("button", has_text="Start").first.click()
    pg.wait_for_selector("button:has-text('A')", timeout=15000)
    shot(pg, "jordan-04-quiz")
    answer_one(pg)
    shot(pg, "jordan-05-quiz-answered")
    ctx.close()

    # --- Maria: mobile light, app switched to Spanish, NV ---
    ctx = browser.new_context(color_scheme="light", viewport=MOBILE)
    pg = open_state(ctx, "Nevada")
    pg.locator("button", has_text="ES").first.click()
    pg.wait_for_timeout(700)
    shot(pg, "maria-01-home-es")
    pg.locator("text=Acerca de").or_(pg.locator("text=About this test")).first.click()
    pg.wait_for_timeout(500)
    shot(pg, "maria-02-about-es")
    pg.locator("button", has_text="Comenzar").or_(
        pg.locator("button", has_text="Start")
    ).first.click()
    pg.wait_for_selector("button:has-text('A')", timeout=15000)
    answer_one(pg)
    shot(pg, "maria-03-quiz-answered-es")
    ctx.close()

    # --- Ken: desktop dark, WY, trust + stats ---
    ctx = browser.new_context(color_scheme="dark", viewport=DESKTOP)
    pg = open_state(ctx, "Wyoming")
    shot(pg, "ken-01-home-dark")
    pg.locator("text=About this test").click()
    pg.wait_for_timeout(500)
    shot(pg, "ken-02-about-dark")
    # play a 10-question quiz to generate stats history
    pg.locator("button", has_text="10").first.click()
    pg.locator("button", has_text="Start").first.click()
    pg.wait_for_selector("button:has-text('A')", timeout=15000)
    for _ in range(10):
        answer_one(pg)
        nxt = pg.locator("button", has_text="Next").or_(
            pg.locator("button", has_text="See Results")
        )
        nxt.first.click()
        pg.wait_for_timeout(500)
    shot(pg, "ken-03-results-dark")
    stats = pg.locator("button", has_text="stats").or_(pg.locator("text=Stats"))
    if stats.count():
        stats.first.click()
        pg.wait_for_timeout(700)
        shot(pg, "ken-04-stats-dark")
    ctx.close()

    # --- Aisha: desktop dark, CA, skeptic flow ---
    ctx = browser.new_context(color_scheme="dark", viewport=DESKTOP)
    pg = open_state(ctx, "California")
    pg.locator("text=About this test").click()
    pg.wait_for_timeout(500)
    shot(pg, "aisha-01-about-ca")
    pg.locator("button", has_text="Start").first.click()
    pg.wait_for_selector("button:has-text('A')", timeout=15000)
    answer_one(pg)
    shot(pg, "aisha-02-quiz-evidence")
    ctx.close()

    browser.close()

print("done")
