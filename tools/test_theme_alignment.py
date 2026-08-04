"""Cross-platform theme alignment: every platform must match data/theme.json.

The canonical tokens live in data/theme.json. Each platform encodes them
differently (Kotlin Color literals, Asset Catalog colorsets, CSS custom
properties in two syntaxes); these tests parse each source and diff against
the canonical values so palette drift fails CI instead of shipping.
"""

import json
import os
import re

import pytest
from _util import ROOT_DIR

THEME_PATH = os.path.join(ROOT_DIR, "data", "theme.json")
ANDROID_THEME = os.path.join(
    ROOT_DIR,
    "android",
    "app",
    "src",
    "main",
    "java",
    "com",
    "drivers",
    "test",
    "theme",
    "Theme.kt",
)
IOS_ASSETS = os.path.join(ROOT_DIR, "ios", "DriversTest", "DriversTest", "Assets.xcassets")
WEB_HTML = os.path.join(ROOT_DIR, "web", "static", "index.html")
FRONTEND_CSS = os.path.join(ROOT_DIR, "frontend", "src", "index.css")

# role name -> per-platform identifiers
ANDROID_NAMES = {
    "blue": "Blue",
    "blueLight": "BlueLight",
    "green": "Green",
    "greenLight": "GreenLight",
    "red": "Red",
    "redLight": "RedLight",
    "orange": "Orange",
    "gray": "Gray",
    "grayLight": "GrayLight",
}
IOS_NAMES = {**ANDROID_NAMES, "onPrimary": "OnPrimary"}
WEB_NAMES = {
    "blue": "blue",
    "blueLight": "blue-light",
    "green": "green",
    "greenLight": "green-light",
    "red": "red",
    "redLight": "red-light",
    "orange": "orange",
    "gray": "gray",
    "grayLight": "gray-light",
    "onPrimary": "on-primary",
}
FRONTEND_NAMES = {
    "blue": "primary",
    "blueLight": "primary-surface",
    "green": "success",
    "greenLight": "success-surface",
    "red": "error",
    "redLight": "error-surface",
    "orange": "warning",
    "gray": "muted",
    "grayLight": "border-subtle",
    "onPrimary": "on-accent",
}


def canonical() -> dict[str, dict[str, str]]:
    with open(THEME_PATH) as f:
        return json.load(f)["tokens"]


def android_tokens() -> dict[str, dict[str, str]]:
    src = open(ANDROID_THEME).read()
    vals = {
        m.group(1): "#" + m.group(2).upper()
        for m in re.finditer(r"val (\w+) = Color\(0xFF([0-9A-Fa-f]{6})\)", src)
    }
    out: dict[str, dict[str, str]] = {}
    for role, name in ANDROID_NAMES.items():
        out[role] = {"light": vals.get(name, "?"), "dark": vals.get(name + "Dark", "?")}
    # onPrimary is defined in the AppColors constructors, not top-level vals.
    light = (
        "#FFFFFF"
        if re.search(r"LightAppColors = AppColors\([^)]*onPrimary = Color\.White", src, re.S)
        else "?"
    )
    m = re.search(
        r"DarkAppColors = AppColors\([^)]*onPrimary = Color\(0xFF([0-9A-Fa-f]{6})\)", src, re.S
    )
    out["onPrimary"] = {"light": light, "dark": "#" + m.group(1).upper() if m else "?"}
    return out


def _ios_component_to_int(v: str | float) -> int:
    if isinstance(v, str) and v.startswith("0x"):
        return int(v, 16)
    f = float(v)
    return round(f * 255) if f <= 1 else int(f)


def ios_tokens() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for role, name in IOS_NAMES.items():
        path = os.path.join(IOS_ASSETS, f"{name}.colorset", "Contents.json")
        with open(path) as f:
            data = json.load(f)
        entry_out = {}
        for entry in data["colors"]:
            mode = "dark" if entry.get("appearances") else "light"
            c = entry["color"]["components"]
            entry_out[mode] = "#{:02X}{:02X}{:02X}".format(
                _ios_component_to_int(c["red"]),
                _ios_component_to_int(c["green"]),
                _ios_component_to_int(c["blue"]),
            )
        out[role] = entry_out
    return out


def _must_search(pattern: str, text: str, what: str) -> re.Match[str]:
    m = re.search(pattern, text, re.S)
    if m is None:
        raise ValueError(f"could not locate {what}")
    return m


def web_tokens() -> dict[str, dict[str, str]]:
    html = open(WEB_HTML).read()
    style = _must_search(r"<style>(.*?)</style>", html, "web <style> block").group(1)
    light_block = _must_search(r":root \{(.*?)\}", style, "web :root block").group(1)
    dark_block = _must_search(
        r"@media \(prefers-color-scheme: dark\) \{\s*:root \{(.*?)\}",
        style,
        "web dark :root block",
    ).group(1)

    def parse(block: str) -> dict[str, str]:
        return {
            m.group(1): "#" + m.group(2).upper()
            for m in re.finditer(r"--([\w-]+):\s*#([0-9A-Fa-f]{6})", block)
        }

    light, dark = parse(light_block), parse(dark_block)
    return {
        role: {"light": light.get(name, "?"), "dark": dark.get(name, "?")}
        for role, name in WEB_NAMES.items()
    }


def frontend_tokens() -> dict[str, dict[str, str]]:
    css = open(FRONTEND_CSS).read()
    light_block = _must_search(r":root \{(.*?)\}", css, "frontend :root block").group(1)
    dark_block = _must_search(r"\.dark \{(.*?)\}", css, "frontend .dark block").group(1)

    def parse(block: str) -> dict[str, str]:
        out = {}
        for m in re.finditer(r"--color-([\w-]+):\s*(\d+)\s+(\d+)\s+(\d+)", block):
            out[m.group(1)] = f"#{int(m.group(2)):02X}{int(m.group(3)):02X}{int(m.group(4)):02X}"
        return out

    light, dark = parse(light_block), parse(dark_block)
    return {
        role: {"light": light.get(name, "?"), "dark": dark.get(name, "?")}
        for role, name in FRONTEND_NAMES.items()
    }


@pytest.mark.parametrize(
    "platform,extract",
    [
        ("android", android_tokens),
        ("ios", ios_tokens),
        ("web", web_tokens),
        ("frontend", frontend_tokens),
    ],
)
def test_platform_matches_canonical_tokens(platform, extract):
    want = canonical()
    got = extract()
    mismatches = []
    for role, modes in want.items():
        for mode, expected in modes.items():
            actual = got.get(role, {}).get(mode, "MISSING")
            if actual.upper() != expected.upper():
                mismatches.append(f"{role}.{mode}: expected {expected}, {platform} has {actual}")
    assert not mismatches, f"{platform} diverges from data/theme.json:\n  " + "\n  ".join(
        mismatches
    )


def test_canonical_file_has_all_roles_and_valid_hex():
    tokens = canonical()
    assert set(tokens) == set(IOS_NAMES), "role set drifted from the documented 10"
    for role, modes in tokens.items():
        for mode in ("light", "dark"):
            assert re.fullmatch(r"#[0-9A-F]{6}", modes[mode].upper()), f"{role}.{mode} not #RRGGBB"
