"""Compose v1 marketing imagery for App Store + Play Store from the design mocks.

Runs locally without external assets. Uses bundled DejaVu fonts as stand-ins for
IBM Plex Serif + Inter (production assets should be re-rendered with the real
fonts before submission).

Outputs:
    docs/app-store/marketing/feature-graphic-play.png        (1024x500)
    docs/app-store/screenshots/ios-6.7/{NN-{slug}}.png       (1290x2796)
    docs/app-store/screenshots/play-phone/{NN-{slug}}.png    (1080x1920)
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

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BAND_HEIGHT_RATIO = 0.18
BAND_BRASS_RULE_PX = 6
CAPTION_FONT_RATIO = 0.045
EYEBROW_FONT_RATIO = 0.018
CONTENT_X_RATIO = 0.06
EYEBROW_Y_RATIO_IN_BAND = 0.22
CAPTION_Y_RATIO_IN_BAND = 0.45
CAPTION_LINE_HEIGHT = 1.15
MAX_CAPTION_CHARS = 32
DEVICE_TOP_PADDING_PX = 40
DEVICE_BOTTOM_PADDING_PX = 60
DEVICE_HORIZONTAL_PADDING_PX = 80
EYEBROW_TEXT = "REAL DMV MANUALS · 50 STATES"


def vertical_gradient(
    size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]
) -> Image.Image:
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


def feature_graphic_play(quiz_image: Image.Image) -> Image.Image:
    """1024x500 Play Store feature graphic."""
    W, H = 1024, 500
    TEXT_X = 76
    img = vertical_gradient((W, H), NAVY, NAVY_DEEP)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(48, 90), (52, 410)], fill=BRASS)

    eyebrow = ImageFont.truetype(SANS_BOLD, 18)
    headline = ImageFont.truetype(SERIF, 56)
    sub = ImageFont.truetype(SANS, 22)
    micro = ImageFont.truetype(SANS, 16)

    draw.text((TEXT_X, 95), "DRIVER'S TEST PREP", font=eyebrow, fill=BRASS, spacing=2)
    draw.text((TEXT_X, 130), "Study from", font=headline, fill=WHITE)
    draw.text((TEXT_X, 200), "the real manual.", font=headline, fill=WHITE)
    draw.text(
        (TEXT_X, 290),
        "50 states  ·  17,753 questions  ·  Free  ·  Offline",
        font=sub,
        fill=SLATE,
    )
    draw.text(
        (TEXT_X, 340),
        "Every question cites your state's manual.",
        font=sub,
        fill=SLATE,
    )
    draw.text((TEXT_X, 410), "v1.0", font=micro, fill=BRASS)

    qw, qh = quiz_image.size
    target_h = 420
    target_w = round(qw * target_h / qh)
    quiz = quiz_image.resize((target_w, target_h), Image.Resampling.LANCZOS)
    img.paste(quiz, (W - target_w - 40, 40))

    return img


def _wrap_caption(caption: str, max_chars: int) -> list[str]:
    words = caption.split()
    lines: list[str] = []
    current = ""
    for w in words:
        candidate = (current + " " + w).strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def device_screenshot(
    device_image: Image.Image, caption: str, *, output_size: tuple[int, int]
) -> Image.Image:
    """Compose a marketing screenshot: navy header band with caption + the mock device shot below."""
    OUT_W, OUT_H = output_size
    img = Image.new("RGB", (OUT_W, OUT_H), SURFACE)
    draw = ImageDraw.Draw(img)

    band_h = round(OUT_H * BAND_HEIGHT_RATIO)
    band = vertical_gradient((OUT_W, band_h), NAVY, (35, 65, 105))
    img.paste(band, (0, 0))
    draw.rectangle([(0, band_h), (OUT_W, band_h + BAND_BRASS_RULE_PX)], fill=BRASS)

    cap_font = ImageFont.truetype(SERIF, round(OUT_W * CAPTION_FONT_RATIO))
    eyebrow_font = ImageFont.truetype(SANS_BOLD, round(OUT_W * EYEBROW_FONT_RATIO))
    content_x = round(OUT_W * CONTENT_X_RATIO)
    draw.text(
        (content_x, round(band_h * EYEBROW_Y_RATIO_IN_BAND)),
        EYEBROW_TEXT,
        font=eyebrow_font,
        fill=BRASS,
    )

    y = round(band_h * CAPTION_Y_RATIO_IN_BAND)
    for line in _wrap_caption(caption, MAX_CAPTION_CHARS):
        draw.text((content_x, y), line, font=cap_font, fill=WHITE)
        y += int(cap_font.size * CAPTION_LINE_HEIGHT)

    dw, dh = device_image.size
    avail_h = OUT_H - band_h - DEVICE_BOTTOM_PADDING_PX
    scale = avail_h / dh
    if round(dw * scale) > OUT_W - DEVICE_HORIZONTAL_PADDING_PX:
        scale = (OUT_W - DEVICE_HORIZONTAL_PADDING_PX) / dw
    new_w = round(dw * scale)
    new_h = round(dh * scale)
    device = device_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    img.paste(device, ((OUT_W - new_w) // 2, band_h + DEVICE_TOP_PADDING_PX))

    return img


CAPTIONS: list[tuple[str, str]] = [
    ("01-home-light.png", "Practice for your permit, grounded in the real DMV manual."),
    ("02-state-picker-light.png", "Every US state. Latest handbook edition for each."),
    ("03-quiz-light.png", "Every question cites the exact page in your state's manual."),
    ("05-results-light.png", "Pass-rate at a glance. Drill into what you missed."),
    ("06-stats-light.png", "Track your weak categories. Practice them first."),
]

STORE_OUTPUTS: list[tuple[Path, tuple[int, int], str]] = [
    (OUT_IOS, (1290, 2796), "iOS App Store (1290x2796, 6.7in)"),
    (OUT_PLAY, (1080, 1920), "Play Store phone (1080x1920)"),
]


def _slug(filename: str) -> str:
    return Path(filename).stem.removesuffix("-light").removesuffix("-dark")


def _check_fonts() -> None:
    for path in (SERIF, SANS, SANS_BOLD):
        if not Path(path).exists():
            raise FileNotFoundError(
                f"Required font {path} not found. Install DejaVu fonts "
                "(Debian/Ubuntu: apt install fonts-dejavu)."
            )


def main() -> None:
    _check_fonts()
    OUT_MARKETING.mkdir(parents=True, exist_ok=True)
    for out_dir, _, _ in STORE_OUTPUTS:
        out_dir.mkdir(parents=True, exist_ok=True)

    sources: dict[str, Image.Image] = {}
    for filename, _ in CAPTIONS:
        src = SOURCE / filename
        if src.exists():
            sources[filename] = Image.open(src).convert("RGB")

    print("Composing Play feature graphic...")
    quiz = sources.get("03-quiz-light.png")
    if quiz is None:
        raise FileNotFoundError(f"Required quiz source missing: {SOURCE / '03-quiz-light.png'}")
    feature_graphic_play(quiz).save(OUT_MARKETING / "feature-graphic-play.png", optimize=True)
    print(f"  -> {OUT_MARKETING / 'feature-graphic-play.png'}")

    for out_dir, size, label in STORE_OUTPUTS:
        print(f"\nComposing {label}...")
        for filename, caption in CAPTIONS:
            device = sources.get(filename)
            if device is None:
                print(f"  ! missing source {SOURCE / filename}, skipping")
                continue
            slug = _slug(filename)
            out = out_dir / f"{slug}.png"
            device_screenshot(device, caption, output_size=size).save(out, optimize=True)
            print(f"  -> {out.name}")

    print("\nDone.")


if __name__ == "__main__":
    sys.exit(main())
