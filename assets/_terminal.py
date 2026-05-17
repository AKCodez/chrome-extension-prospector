"""Render the captured live skill run as a polished terminal PNG."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent

BG = (13, 17, 23)
WIN_BG = (22, 27, 34)
CHROME = (33, 38, 45)
BORDER = (48, 54, 61)
TEXT = (230, 237, 243)
DIM = (139, 148, 158)
GREEN = (63, 185, 80)
CYAN = (88, 166, 255)
ORANGE = (240, 136, 62)
YELLOW = (255, 211, 61)
PURPLE = (188, 140, 255)
RED = (248, 81, 73)


def font_mono(size, bold=False):
    return ImageFont.truetype("CascadiaCode.ttf", size)


def font_ui(size, bold=False):
    return ImageFont.truetype("seguibl.ttf" if bold else "segoeui.ttf", size)


# (text, color, bold)
LINES = [
    ("> /chrome-extension-prospector productivity",         CYAN,  True),
    ("",                                                    None,  False),
    ("Step 1/3 — Discovery: searching Chrome Web Store",    DIM,   False),
    ("Step 2/3 — Enrichment: pulling developer emails",     DIM,   False),
    ("  discovery: 9 results · enrichment: 10 results",     ORANGE, False),
    ("Step 3/3 — Merging, filtering (≥10,000 users), scoring", DIM,False),
    ("",                                                    None,  False),
    ("✓ Found 5 prospects · 5 with email (100%)",           GREEN, True),
    ("✓ Pipeline cost: $0.20  ·  total anchor value: $86,000",GREEN, True),
    ("",                                                    None,  False),
    ("Top 5:",                                              TEXT,  True),
    ("",                                                    None,  False),
    ("  1. MakeTime — increase productivity",               GREEN, True),
    ("       10,000 users · 4.3/5 · score +4 · $500–$2,500",DIM,   False),
    ("       → uasmartapps@gmail.com",                      CYAN,  False),
    ("",                                                    None,  False),
    ("  2. Anori: productivity new tab",                    GREEN, True),
    ("       30,000 users · 4.6/5 · score +3 · $500–$2,500",DIM,   False),
    ("       → chromestore@sinja.io",                       CYAN,  False),
    ("",                                                    None,  False),
    ("  3. Homey: Productivity New Tab",                    CYAN,  True),
    ("       90,000 users · 4.8/5 · score +2 · $2,500–$8,000",DIM, False),
    ("       → info@homey.place",                           CYAN,  False),
    ("",                                                    None,  False),
    ("  4. StayFocusd — Website Blocker",                   CYAN,  True),
    ("       700,000 users · 4.5/5 · score +2 · $15,000–$50,000",DIM,False),
    ("       → support@stayfreeapps.com",                   CYAN,  False),
    ("",                                                    None,  False),
    ("  5. Toggl Track: Productivity & Time Tracker",       DIM,   True),
    ("       400,000 users · 4.4/5 · score −5 · SKIPPED (big co.)",ORANGE, False),
    ("",                                                    None,  False),
    ("Writing Google Sheet 'Chrome Prospects · productivity · 2026-05-17'…", DIM, False),
    ("✓ Sheet ready · 4 emails queued",                     GREEN, True),
    ("Sending via Gmail…",                                  DIM,   False),
    ("✓ sent to uasmartapps@gmail.com",                     GREEN, False),
    ("✓ sent to chromestore@sinja.io",                      GREEN, False),
    ("✓ sent to info@homey.place",                          GREEN, False),
    ("✓ sent to support@stayfreeapps.com",                  GREEN, False),
    ("",                                                    None,  False),
    ("Done. 4 sent · 1 skipped · 0 errors",                 GREEN, True),
]


def render():
    W = 1400
    pad_top, pad_bottom, pad_left = 80, 36, 36
    line_h = 26
    H = pad_top + line_h * len(LINES) + pad_bottom

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    body_radius = 16
    d.rounded_rectangle([24, 24, W - 24, H - 24], radius=body_radius, fill=WIN_BG, outline=BORDER, width=1)
    d.rounded_rectangle([24, 24, W - 24, 24 + 44], radius=body_radius, fill=CHROME, outline=BORDER, width=1)
    d.rectangle([24, 24 + 22, W - 24, 24 + 44], fill=CHROME)

    cy = 24 + 22
    for i, (cx, col) in enumerate([(48, RED), (72, YELLOW), (96, GREEN)]):
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=col)
    d.text((W // 2 - 90, 24 + 13), "chrome-extension-prospector", font=font_ui(15), fill=DIM)

    y = 24 + 60
    for text, col, bold in LINES:
        if col is None:
            y += line_h
            continue
        d.text((pad_left + 24, y), text, font=font_mono(15, bold=bold), fill=col)
        y += line_h

    img.save(OUT / "terminal.png", optimize=True)
    print("terminal.png", img.size)


if __name__ == "__main__":
    render()
