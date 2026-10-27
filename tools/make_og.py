#!/usr/bin/env python3
"""Draw the link-preview cards (the picture a phone shows when a link is texted).
Run by hand when the branding changes: python3 tools/make_og.py"""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CARDS = {
    "newsstand":      ("The Newsstand", "BAY AREA EVENTS · WORLD FOOTBALL · ARSENAL", "#1a1713"),
    "bay-weekender":  ("The Bay Weekender", "SAN FRANCISCO & THE BAY AREA · EVERY OTHER MONDAY", "#b8860b"),
    "soccer-digest":  ("The Weekly Soccer Digest", "WORLD FOOTBALL · WEDNESDAYS", "#0f7a4e"),
    "arsenal-digest": ("The Weekly Arsenal Digest", "ONE CLUB, COVERED PROPERLY · TUESDAYS", "#EF0107"),
}
W, H = 1200, 630
for slug, (title, sub, accent) in CARDS.items():
    im = Image.new("RGB", (W, H), "#f3efe6")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 18], fill=accent)
    size = 92
    while True:
        f = ImageFont.truetype(SERIF, size)
        if d.textlength(title, font=f) < W - 140 or size < 40: break
        size -= 4
    tw = d.textlength(title, font=f)
    d.text(((W - tw) / 2, 230), title, font=f, fill="#12100d")
    y = 230 + size + 40
    d.line([120, y, W - 120, y], fill="#1a1713", width=2)
    d.line([120, y + 8, W - 120, y + 8], fill="#1a1713", width=5)
    fs = ImageFont.truetype(SANS, 24)
    sw = d.textlength(sub, font=fs)
    d.text(((W - sw) / 2, y + 36), sub, font=fs, fill="#5b5344")
    fk = ImageFont.truetype(SANS, 20)
    k = "EVANAGRIBBEN.GITHUB.IO"
    d.text(((W - d.textlength(k, font=fk)) / 2, H - 70), k, font=fk, fill="#8f8571")
    im.save(os.path.join(ROOT, "img", f"og-{slug}.png"), optimize=True)
    print("wrote", slug)
