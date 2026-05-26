"""Compose v1 marketing imagery for App Store + Play Store from the design mocks.

Runs locally without external assets. Uses bundled DejaVu fonts as stand-ins for
IBM Plex Serif + Inter (production assets should be re-rendered with the real
fonts before submission).

Outputs:
    docs/app-store/marketing/feature-graphic-play.png        (1024x500)
    docs/app-store/screenshots/ios-6.7/{1..5}-{caption}.png  (1290x2796)
    docs/app-store/screenshots/play-phone/{1..5}-{caption}.png (1080x1920)
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
SOURCE = ROOT / "screenshots" / "source"
OUT_MARKETING = ROOT / "marketing"
OUT_IOS = ROOT / "screenshots" / "ios-6.7"
OUT_PLAY = ROOT / "screenshots" / "play-phone"

NAVY = (30, 58, 95)
NAVY_DEEP = (15, 23, 42)
BRASS = (197, 165, 114)
WHITE = (255, 255, 255)
SLATE = (203, 213, 225)
SURFACE = (248, 250, 252)
INK = (15, 23, 42)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    """Solid two-stop vertical gradient image."""
    w, h = size
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = round(top[0] + (bottom[0] - top[0]) * t)
        g = round(top[1] + (bottom[1] - top[1]) * t)
        b = round(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def feature_graphic_play() -> Image.Image:
    """1024x500 Play Store feature graphic."""
    W, H = 1024, 500
    img = vertical_gradient((W, H), NAVY, NAVY_DEEP)
    draw = ImageDraw.Draw(img)
    # Brass divider on the left edge of the text block
    draw.rectangle([(48, 90), (52, 410)], fill=BRASS)

    eyebrow = ImageFont.truetype(SANS_BOLD, 18)
    headline = ImageFont.truetype(SERIF, 56)
    sub = ImageFont.truetype(SANS, 22)
    micro = ImageFont.truetype(SANS, 16)

    draw.text((76, 95), "DRIVER'S TEST PREP", font=eyebrow, fill=BRASS, spacing=2)
    draw.text((76, 130), "Study from", font=headline, fill=WHITE)
    draw.text((76, 200), "the real manual.", font=headline, fill=WHITE)
    draw.text(
        (76, 290),
        "50 states  ·  17,753 questions  ·  Free  ·  Offline",
        font=sub,
        fill=SLATE,
    )
    draw.text(
        (76, 340),
        "Every question cites your state's manual.",
        font=sub,
        fill=SLATE,
    )
    draw.text((76, 410), "v1.0", font=micro, fill=BRASS)

    # Mini phone glyph on the right
    quiz = Image.open(SOURCE / "03-quiz-light.png").convert("RGB")
    qw, qh = quiz.size
    target_h = 420
    target_w = round(qw * target_h / qh)
    quiz = quiz.resize((target_w, target_h), Image.Resampling.LANCZOS)
    img.paste(quiz, (W - target_w - 40, 40))

    return img


def device_screenshot(source_file: Path, caption: str, *, output_size: tuple[int, int]) -> Image.Image:
    """Compose a marketing screenshot: navy header band with caption + the mock device shot below."""
    OUT_W, OUT_H = output_size
    img = Image.new("RGB", (OUT_W, OUT_H), SURFACE)
    draw = ImageDraw.Draw(img)

    # Top caption band (navy)
    band_h = round(OUT_H * 0.18)
    band = vertical_gradient((OUT_W, band_h), NAVY, (35, 65, 105))
    img.paste(band, (0, 0))

    # Brass rule under band
    draw.rectangle([(0, band_h), (OUT_W, band_h + 6)], fill=BRASS)

    # Caption text wrapping for ~40 chars per line
    cap_font = ImageFont.truetype(SERIF, round(OUT_W * 0.045))
    eyebrow_font = ImageFont.truetype(SANS_BOLD, round(OUT_W * 0.018))
    draw.text((round(OUT_W * 0.06), round(band_h * 0.22)), "REAL DMV MANUALS · 50 STATES", font=eyebrow_font, fill=BRASS)

    # Wrap caption
    words = caption.split()
    lines: list[str] = []
    current = ""
    max_chars = 32
    for w in words:
        candidate = (current + " " + w).strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)

    y = round(band_h * 0.45)
    for line in lines:
        draw.text((round(OUT_W * 0.06), y), line, font=cap_font, fill=WHITE)
        y += int(cap_font.size * 1.15)

    # Device screenshot below band
    device = Image.open(source_file).convert("RGB")
    dw, dh = device.size
    avail_h = OUT_H - band_h - 60
    scale = avail_h / dh
    new_w = round(dw * scale)
    new_h = round(dh * scale)
    if new_w > OUT_W - 80:
        scale = (OUT_W - 80) / dw
        new_w = round(dw * scale)
        new_h = round(dh * scale)
    device = device.resize((new_w, new_h), Image.Resampling.LANCZOS)
    paste_x = (OUT_W - new_w) // 2
    paste_y = band_h + 40
    img.paste(device, (paste_x, paste_y))

    return img


CAPTIONS: list[tuple[str, str]] = [
    ("01-home-light.png", "Practice for your permit, grounded in the real DMV manual."),
    ("02-state-picker-light.png", "Every US state. Latest handbook edition for each."),
    ("03-quiz-light.png", "Every question cites the exact page in your state's manual."),
    ("05-results-light.png", "Pass-rate at a glance. Drill into what you missed."),
    ("06-stats-light.png", "Track your weak categories. Practice them first."),
]


def main() -> None:
    OUT_MARKETING.mkdir(parents=True, exist_ok=True)
    OUT_IOS.mkdir(parents=True, exist_ok=True)
    OUT_PLAY.mkdir(parents=True, exist_ok=True)

    print("Composing Play feature graphic...")
    fg = feature_graphic_play()
    fg.save(OUT_MARKETING / "feature-graphic-play.png", optimize=True)
    print(f"  -> {OUT_MARKETING / 'feature-graphic-play.png'}")

    print("\nComposing iOS App Store screenshots (1290x2796, 6.7in)...")
    for i, (filename, caption) in enumerate(CAPTIONS, start=1):
        src = SOURCE / filename
        if not src.exists():
            print(f"  ! missing source {src}, skipping")
            continue
        out = OUT_IOS / f"{i:02d}-{filename.replace('-light.png', '').replace('-dark.png', '')}.png"
        device_screenshot(src, caption, output_size=(1290, 2796)).save(out, optimize=True)
        print(f"  -> {out.name}")

    print("\nComposing Play Store phone screenshots (1080x1920)...")
    for i, (filename, caption) in enumerate(CAPTIONS, start=1):
        src = SOURCE / filename
        if not src.exists():
            continue
        out = OUT_PLAY / f"{i:02d}-{filename.replace('-light.png', '').replace('-dark.png', '')}.png"
        device_screenshot(src, caption, output_size=(1080, 1920)).save(out, optimize=True)
        print(f"  -> {out.name}")

    print("\nDone.")


if __name__ == "__main__":
    sys.exit(main())
