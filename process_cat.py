#!/usr/bin/env python3
"""Turn Gemini cat images (cat on a plain white background) into transparent calendar cutouts."""
import argparse
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
INBOX, ASSETS = HERE / "inbox", HERE / "assets"


def cutout(img: Image.Image, tol: int = 28) -> Image.Image:
    rgb = img.convert("RGB")
    w, h = rgb.size
    near_white = rgb.convert("L").point(lambda v: 255 if v >= 255 - tol else 0)

    flood = near_white.copy()
    border = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    for pt in border:
        if flood.getpixel(pt) == 255:
            ImageDraw.floodfill(flood, pt, 128)
    background = flood.point(lambda v: 255 if v == 128 else 0)

    alpha = ImageChops.invert(background)
    alpha = alpha.filter(ImageFilter.MinFilter(3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))
    alpha = alpha.point(lambda v: 0 if v < 64 else (255 if v > 192 else int((v - 64) * 255 / 128)))

    out = rgb.copy()
    out.putalpha(alpha)
    return out


def process(src: Path, dst: Path, max_h: int, boost: float) -> None:
    out = cutout(Image.open(src))
    bbox = out.getchannel("A").getbbox()
    if not bbox:
        raise SystemExit(f"{src.name}: nothing left after removing the background")
    pad = 4
    bbox = (max(bbox[0] - pad, 0), max(bbox[1] - pad, 0),
            min(bbox[2] + pad, out.width), min(bbox[3] + pad, out.height))
    out = out.crop(bbox)

    if boost != 1.0:
        r, g, b, a = out.split()
        rgb = ImageEnhance.Color(Image.merge("RGB", (r, g, b))).enhance(boost)
        out = Image.merge("RGBA", (*rgb.split(), a))
    if out.height > max_h:
        out = out.resize((round(out.width * max_h / out.height), max_h), Image.LANCZOS)

    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst, optimize=True)

    if HERE in dst.parents:
        INBOX.mkdir(exist_ok=True)
        card = Image.new("RGBA", (out.width + 40, out.height + 40), (228, 38, 27, 255))
        card.alpha_composite(out, (20, 20))
        card.convert("RGB").save(INBOX / f"preview-{dst.stem}.png")
    shown = dst.relative_to(HERE) if HERE in dst.parents else dst
    print(f"{src.name} -> {shown}  {out.size}, {dst.stat().st_size // 1024} KB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="images to process (default: everything in inbox/)")
    ap.add_argument("--height", type=int, default=700)
    ap.add_argument("--boost", type=float, default=1.0)
    a = ap.parse_args()
    files = [Path(f) for f in a.files] or sorted(p for p in INBOX.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and not p.name.startswith("preview-"))
    if not files:
        print(f"No new images to process in {INBOX}.")
        raise SystemExit(0)
    for f in files:
        process(f, ASSETS / f"cat-{f.stem.lower().removeprefix('cat-')}.png", a.height, a.boost)
