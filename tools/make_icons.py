"""Render the app icon for every platform from one vector description.

The mark is a white rounded diamond (a warning-sign silhouette) carrying a
bold checkmark on the brand blue from data/theme.json. Everything is drawn
with Pillow at 4x supersampling so no external SVG rasteriser is needed.

Outputs (all committed; re-run after changing the drawing):
    ios/DriversTest/DriversTest/Assets.xcassets/AppIcon.appiconset/icon-1024.png
    android/app/src/main/res/mipmap-{m,h,xh,xxh,xxxh}dpi/ic_launcher{,_round}.png
    frontend/public/icons/icon-{32,180,192,512}.png, icon-maskable-512.png
    docs/app-store/marketing/play-icon-512.png

Usage:
    python3 tools/make_icons.py
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
THEME = json.loads((ROOT / "data" / "theme.json").read_text())
BLUE = THEME["tokens"]["blue"]["light"]
WHITE = "#FFFFFF"

SS = 4  # supersampling factor
BASE = 1024  # design canvas in px; all coordinates below are in this space


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def draw_mark(canvas: Image.Image, scale: float = 1.0) -> None:
    """Draw the diamond + check centred on `canvas` (already at SS resolution).

    `scale` shrinks the mark relative to the canvas, used for Android's
    adaptive-icon safe zone and the maskable web icon.
    """
    w, h = canvas.size
    cx, cy = w / 2, h / 2
    unit = (w / BASE) * scale  # px per design unit

    # Diamond: rounded square rotated 45 degrees, drawn on its own layer.
    side = 560 * unit
    radius = 90 * unit
    layer_size = int(side * 1.6)
    layer = Image.new("RGBA", (layer_size, layer_size), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    off = (layer_size - side) / 2
    ld.rounded_rectangle([off, off, off + side, off + side], radius=radius, fill=WHITE)
    layer = layer.rotate(45, resample=Image.BICUBIC, expand=False)
    canvas.alpha_composite(layer, (int(cx - layer_size / 2), int(cy - layer_size / 2)))

    # Checkmark: thick polyline with round joints, in brand blue.
    d = ImageDraw.Draw(canvas)
    pts = [
        (cx - 150 * unit, cy + 10 * unit),
        (cx - 40 * unit, cy + 120 * unit),
        (cx + 170 * unit, cy - 110 * unit),
    ]
    width = int(92 * unit)
    d.line(pts, fill=BLUE, width=width, joint="curve")
    r = width / 2
    for x, y in (pts[0], pts[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=BLUE)


def render(size: int, *, rounded: bool, background: bool, mark_scale: float = 1.0) -> Image.Image:
    big = size * SS
    canvas = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    if background:
        d = ImageDraw.Draw(canvas)
        if rounded:
            d.rounded_rectangle([0, 0, big - 1, big - 1], radius=int(big * 0.22), fill=BLUE)
        else:
            d.rectangle([0, 0, big - 1, big - 1], fill=BLUE)
    draw_mark(canvas, mark_scale)
    return canvas.resize((size, size), Image.LANCZOS)


def save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)
    print(f"  {path.relative_to(ROOT)} ({img.size[0]}px)")


def main() -> None:
    print(f"Rendering icons on {BLUE}...")

    # iOS: single 1024 full-bleed square; iOS applies its own mask.
    ios = render(1024, rounded=False, background=True)
    # Flatten alpha: App Store rejects icons with an alpha channel.
    ios_rgb = Image.new("RGB", ios.size, _hex_to_rgb(BLUE))
    ios_rgb.paste(ios, mask=ios.split()[3])
    save(
        ios_rgb,
        ROOT / "ios/DriversTest/DriversTest/Assets.xcassets/AppIcon.appiconset/icon-1024.png",
    )

    # Android legacy launcher icons (pre-API 26 devices and some launchers).
    for dpi, px in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)):
        res = ROOT / "android/app/src/main/res" / f"mipmap-{dpi}"
        save(render(px, rounded=True, background=True), res / "ic_launcher.png")
        round_img = render(px, rounded=False, background=True)
        mask = Image.new("L", (px, px), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, px - 1, px - 1], fill=255)
        round_img.putalpha(mask)
        save(round_img, res / "ic_launcher_round.png")

    # Play Store listing icon: 512 px, no alpha, full bleed (Play rounds it).
    play = render(512, rounded=False, background=True)
    play_rgb = Image.new("RGB", play.size, _hex_to_rgb(BLUE))
    play_rgb.paste(play, mask=play.split()[3])
    save(play_rgb, ROOT / "docs/app-store/marketing/play-icon-512.png")

    # Web: favicon PNGs, apple-touch-icon, PWA icons.
    web = ROOT / "frontend/public/icons"
    for px in (32, 180, 192, 512):
        save(render(px, rounded=True, background=True), web / f"icon-{px}.png")
    # Maskable: full bleed with the mark inside the 80% safe zone.
    save(
        render(512, rounded=False, background=True, mark_scale=0.8), web / "icon-maskable-512.png"
    )
    print("Done.")


if __name__ == "__main__":
    main()
