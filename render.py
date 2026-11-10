#!/usr/bin/env python3
"""Render a calendar template to a 1264x1680, 24-bit RGB PNG (Kobo Libra Colour).

Usage:  python render.py [--template template-simple.html] [--out out/today.png]
Set PW_CHANNEL=msedge (or chrome) to use an installed browser instead of Playwright's Chromium.
"""
import argparse
import os
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

W, H = 1264, 1680
HERE = Path(__file__).resolve().parent


def render(template: str, out: str) -> None:
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    raw = out_path.with_suffix(".raw.png")
    with sync_playwright() as p:
        channel = os.environ.get("PW_CHANNEL")
        browser = p.chromium.launch(channel=channel) if channel else p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        page.goto((HERE / template).resolve().as_uri())
        page.wait_for_load_state("load")
        page.evaluate("document.fonts.ready.then(() => true)")  # wait for the web font
        print("fonts:", page.evaluate("[...document.fonts].map(f => f.family + ':' + f.status).join(', ')"))
        page.screenshot(path=str(raw))
        browser.close()
    img = Image.open(raw).convert("RGB")  # drop any alpha channel
    if img.size != (W, H):
        raise SystemExit(f"unexpected screenshot size {img.size}, wanted {(W, H)}")
    img.save(out_path, optimize=True)
    raw.unlink()
    print(f"wrote {out_path} {img.size}, {out_path.stat().st_size} bytes")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="template-simple.html")
    ap.add_argument("--out", default="out/today.png")
    a = ap.parse_args()
    render(a.template, a.out)
