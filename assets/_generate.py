"""Generates all README assets. Run once: python _generate.py"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).parent

BG = (13, 17, 23)
CARD = (22, 27, 34)
CARD_HI = (33, 38, 45)
BORDER = (48, 54, 61)
TEXT = (230, 237, 243)
DIM = (139, 148, 158)
GREEN = (63, 185, 80)
CYAN = (88, 166, 255)
ORANGE = (240, 136, 62)
RED = (248, 81, 73)
PURPLE = (188, 140, 255)
YELLOW = (255, 211, 61)


def font(name, size):
    return ImageFont.truetype(name, size)


F_BOLD = lambda s: font("seguibl.ttf", s)
F_SEMI = lambda s: font("seguisb.ttf", s)
F_REG = lambda s: font("segoeui.ttf", s)
F_MONO = lambda s: font("consola.ttf", s)


def rounded(draw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def measure(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def banner():
    W, H = 1400, 420
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(13 + (28 - 13) * t)
        g = int(17 + (22 - 17) * t)
        b = int(23 + (40 - 23) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))

    for i, (cx, cy, cr, col) in enumerate([
        (160, 80, 260, (63, 185, 80, 35)),
        (1240, 360, 320, (88, 166, 255, 30)),
        (760, 60, 180, (240, 136, 62, 25)),
    ]):
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=col)
        img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"))

    d = ImageDraw.Draw(img)
    chip_x, chip_y = 60, 50
    chip_text = "A  CLAUDE  CODE  SKILL"
    chip_font = font("arialbd.ttf", 14)
    tw, th = measure(d, chip_text, chip_font)
    chip_h = th + 22
    rounded(d, [chip_x, chip_y, chip_x + tw + 36, chip_y + chip_h], 18,
            fill=(20, 50, 30), outline=GREEN, width=1)
    d.text((chip_x + 18, chip_y + (chip_h - th) // 2 - 3), chip_text, font=chip_font, fill=GREEN)

    d.text((60, 110), "chrome-extension", font=F_BOLD(76), fill=TEXT)
    d.text((60, 188), "prospector", font=F_BOLD(76), fill=GREEN)

    tag1 = "Find Chrome extensions worth money to acquire."
    tag2 = "Pull dev emails. Lowball them. Auto-send the offer."
    d.text((62, 290), tag1, font=F_REG(28), fill=DIM)
    d.text((62, 326), tag2, font=F_REG(28), fill=DIM)

    bx = W - 460
    by = 50
    bw = 400
    bh = 320
    rounded(d, [bx, by, bx + bw, by + bh], 16, fill=CARD, outline=BORDER, width=1)
    d.text((bx + 28, by + 28), "One command.", font=F_SEMI(20), fill=DIM)
    rounded(d, [bx + 28, by + 70, bx + bw - 28, by + 130], 10,
            fill=CARD_HI, outline=BORDER)
    d.text((bx + 42, by + 86), "$ /chrome-extension-prospector", font=F_MONO(15), fill=CYAN)
    d.text((bx + 42, by + 106), "    productivity", font=F_MONO(15), fill=ORANGE)

    rows = [
        ("Discover", "262K+ extensions", GREEN),
        ("Filter", "users ≥ 10,000", CYAN),
        ("Enrich", "developer emails (100%)", ORANGE),
        ("Send", "Gmail · CAN-SPAM ready", PURPLE),
    ]
    ry = by + 152
    for label, val, col in rows:
        d.ellipse([bx + 28, ry + 6, bx + 40, ry + 18], fill=col)
        d.text((bx + 52, ry), label, font=F_SEMI(16), fill=TEXT)
        d.text((bx + 152, ry), val, font=F_REG(15), fill=DIM)
        ry += 32

    img.save(OUT / "banner.png", optimize=True)


def flow():
    W, H = 1400, 380
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((60, 40), "How it works", font=F_BOLD(40), fill=TEXT)
    d.text((60, 96), "From keyword to inbox in one shot.", font=F_REG(20), fill=DIM)

    steps = [
        ("1", "Discover", "Scan the Chrome\nWeb Store for your\nniche", GREEN),
        ("2", "Filter", "Keep only those\nwith 10,000+ users", CYAN),
        ("3", "Get email", "Pull each developer's\ncontact info", ORANGE),
        ("4", "Lowball", "Compute an\nanchor offer", YELLOW),
        ("5", "Send", "Personalized\nGmail outreach", PURPLE),
    ]
    bw, bh = 220, 180
    gap = 30
    total = len(steps) * bw + (len(steps) - 1) * gap
    start_x = (W - total) // 2
    y0 = 160
    for i, (n, title, desc, col) in enumerate(steps):
        x = start_x + i * (bw + gap)
        rounded(d, [x, y0, x + bw, y0 + bh], 16, fill=CARD, outline=BORDER, width=1)
        d.ellipse([x + 20, y0 + 18, x + 56, y0 + 54], fill=col)
        d.text((x + 31, y0 + 22), n, font=F_BOLD(22), fill=BG)
        d.text((x + 20, y0 + 70), title, font=F_BOLD(22), fill=TEXT)
        for j, line in enumerate(desc.split("\n")):
            d.text((x + 20, y0 + 108 + j * 22), line, font=F_REG(15), fill=DIM)
        if i < len(steps) - 1:
            ax = x + bw + 5
            ay = y0 + bh // 2
            d.line([(ax, ay), (ax + gap - 10, ay)], fill=BORDER, width=2)
            d.polygon([(ax + gap - 10, ay - 6), (ax + gap - 4, ay), (ax + gap - 10, ay + 6)], fill=BORDER)

    img.save(OUT / "flow.png", optimize=True)


def prospects_card():
    W, H = 1400, 560
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((60, 40), "What you actually get", font=F_BOLD(40), fill=TEXT)
    d.text((60, 96), "Real output from running the skill on \"productivity\".",
           font=F_REG(20), fill=DIM)

    cx, cy = 60, 150
    cw, ch = W - 120, 360
    rounded(d, [cx, cy, cx + cw, cy + ch], 16, fill=CARD, outline=BORDER, width=1)

    headers = ["Extension", "Users", "Rating", "Lowball anchor", "Developer email"]
    col_x = [cx + 24, cx + 470, cx + 620, cx + 760, cx + 990]
    hy = cy + 24
    for h, x in zip(headers, col_x):
        d.text((x, hy), h.upper(), font=F_SEMI(13), fill=DIM)
    d.line([(cx + 20, hy + 30), (cx + cw - 20, hy + 30)], fill=BORDER)

    rows = [
        ("MakeTime — increase productivity", "10,000", "4.3", "$500 – $2,500", "uasmartapps@gmail.com", GREEN, "TOP"),
        ("Anori: productivity new tab", "30,000", "4.6", "$500 – $2,500", "chromestore@sinja.io", GREEN, "GOOD"),
        ("Homey: Productivity New Tab", "90,000", "4.8", "$2,500 – $8,000", "info@homey.place", CYAN, "GOOD"),
        ("StayFocusd — Website Blocker", "700,000", "4.5", "$15,000 – $50,000", "support@stayfreeapps.com", CYAN, "WHALE"),
        ("Toggl Track: Productivity & Time…", "400,000", "4.4", "(skipped — big co.)", "support@toggl.com", DIM, "SKIP"),
    ]
    ry = hy + 50
    for name, users, rating, offer, email, name_col, badge in rows:
        d.text((col_x[0], ry), name, font=F_SEMI(17), fill=name_col if badge != "SKIP" else DIM)
        d.text((col_x[1], ry), users, font=F_MONO(17), fill=TEXT if badge != "SKIP" else DIM)
        d.text((col_x[2], ry), rating + " / 5", font=F_SEMI(15), fill=YELLOW if badge != "SKIP" else DIM)
        offer_col = ORANGE if badge != "SKIP" else DIM
        d.text((col_x[3], ry), offer, font=F_BOLD(17), fill=offer_col)
        d.text((col_x[4], ry), email, font=F_MONO(15), fill=DIM)
        ry += 56

    fy = cy + ch + 20
    d.text((60, fy), "5 prospects · 100% had emails · pipeline cost: $0.20 · total anchor value: $86,000",
           font=F_REG(17), fill=DIM)

    img.save(OUT / "prospects.png", optimize=True)


def email_card():
    W, H = 1400, 780
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((60, 40), "What lands in their inbox", font=F_BOLD(40), fill=TEXT)
    d.text((60, 96), "Personalized per prospect. CAN-SPAM compliant. Sent via your Gmail.",
           font=F_REG(20), fill=DIM)

    cx, cy = 60, 156
    cw, ch = W - 120, 600
    rounded(d, [cx, cy, cx + cw, cy + ch], 16, fill=CARD, outline=BORDER, width=1)

    rounded(d, [cx, cy, cx + cw, cy + 56], 16, fill=CARD_HI, outline=BORDER, width=1)
    d.rectangle([cx, cy + 30, cx + cw, cy + 56], fill=CARD_HI)
    d.ellipse([cx + 16, cy + 16, cx + 30, cy + 30], fill=RED)
    d.ellipse([cx + 36, cy + 16, cx + 50, cy + 30], fill=YELLOW)
    d.ellipse([cx + 56, cy + 16, cx + 70, cy + 30], fill=GREEN)
    d.text((cx + 96, cy + 16), "Gmail · New Message", font=F_SEMI(15), fill=DIM)

    px, py = cx + 28, cy + 80
    d.text((px, py), "To:", font=F_SEMI(15), fill=DIM)
    d.text((px + 56, py), "uasmartapps@gmail.com", font=F_MONO(16), fill=CYAN)
    py += 28
    d.text((px, py), "From:", font=F_SEMI(15), fill=DIM)
    d.text((px + 56, py), "you@yourdomain.com", font=F_MONO(16), fill=TEXT)
    py += 28
    d.text((px, py), "Subject:", font=F_SEMI(15), fill=DIM)
    d.text((px + 80, py), "Acquiring MakeTime?", font=F_BOLD(17), fill=TEXT)
    py += 40
    d.line([(cx + 24, py), (cx + cw - 24, py)], fill=BORDER)
    py += 20

    body_lines = [
        ("Hi there,", TEXT),
        ("", TEXT),
        ("Came across MakeTime on the Chrome Web Store ", TEXT),
        ("(10,000+ users, 4.3 stars) — clean little productivity tool.", TEXT),
        ("", TEXT),
        ("I run a small studio that picks up browser extensions from solo", TEXT),
        ("devs who've moved on. If MakeTime is no longer a priority for", TEXT),
        ("you, we'd offer in the range of $500–$2,500 for the listing +", ORANGE),
        ("repo. Cash, fast close (under 2 weeks), no earnouts.", TEXT),
        ("", TEXT),
        ("Fair warning — that's a modest number. Open to a counter.", DIM),
        ("", TEXT),
        ("Worth a 15-min call?", TEXT),
        ("", TEXT),
        ("— You", TEXT),
    ]
    for line, col in body_lines:
        d.text((px, py), line, font=F_REG(17), fill=col)
        py += 22

    img.save(OUT / "email.png", optimize=True)


def offers_chart():
    W, H = 1400, 540
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((60, 40), "The lowball ladder", font=F_BOLD(40), fill=TEXT)
    d.text((60, 96), "Severely below market — designed to anchor low and bait a counter-offer.",
           font=F_REG(20), fill=DIM)

    tiers = [
        ("10k – 50k users", "$500 – $2,500", "side-project exit cash", GREEN),
        ("50k – 100k users", "$2,500 – $8,000", "fair lowball", CYAN),
        ("100k – 500k users", "$5,000 – $20,000", "real conversation starter", ORANGE),
        ("500k – 1M users", "$15,000 – $50,000", "they'll counter at 5x", YELLOW),
        ("1M+ users", "$25,000 – $100,000", "whales — custom approach", PURPLE),
    ]
    y0 = 160
    row_h = 70
    cx = 60
    cw = W - 120
    for i, (users, offer, note, col) in enumerate(tiers):
        y = y0 + i * row_h
        rounded(d, [cx, y, cx + cw, y + row_h - 8], 12, fill=CARD, outline=BORDER, width=1)
        d.rectangle([cx, y, cx + 6, y + row_h - 8], fill=col)
        d.text((cx + 32, y + 18), users, font=F_SEMI(20), fill=TEXT)
        d.text((cx + 380, y + 18), offer, font=F_BOLD(22), fill=col)
        d.text((cx + 720, y + 20), note, font=F_REG(18), fill=DIM)
        rounded(d, [cx + cw - 200, y + 16, cx + cw - 24, y + 44], 6, fill=BG, outline=BORDER)
        d.text((cx + cw - 184, y + 21), "anchor offer", font=F_SEMI(13), fill=DIM)

    img.save(OUT / "offers.png", optimize=True)


def cost_card():
    W, H = 1400, 320
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((60, 40), "What it costs", font=F_BOLD(40), fill=TEXT)
    d.text((60, 96), "Cheaper than a coffee per campaign.", font=F_REG(20), fill=DIM)

    cards = [
        ("$0.20", "Per niche scan", "100 extensions → ~5–15 qualified prospects", GREEN),
        ("$0.0075", "Per prospect", "discovery + email enrichment via Apify", CYAN),
        ("Free", "To send", "Gmail rate-limits handle the rest", ORANGE),
    ]
    cw = (W - 120 - 40) // 3
    y = 160
    for i, (big, label, sub, col) in enumerate(cards):
        x = 60 + i * (cw + 20)
        rounded(d, [x, y, x + cw, y + 130], 16, fill=CARD, outline=BORDER, width=1)
        d.text((x + 24, y + 18), big, font=F_BOLD(48), fill=col)
        d.text((x + 24, y + 76), label, font=F_SEMI(18), fill=TEXT)
        d.text((x + 24, y + 100), sub, font=F_REG(14), fill=DIM)

    img.save(OUT / "cost.png", optimize=True)


def setup_card():
    W, H = 1400, 360
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((60, 40), "Three commands", font=F_BOLD(40), fill=TEXT)
    d.text((60, 96), "Then it just works.", font=F_REG(20), fill=DIM)

    cmds = [
        ("01", "/plugin marketplace add akcodez/chrome-extension-prospector", "Add this marketplace"),
        ("02", "/plugin install chrome-extension-prospector", "Install the skill"),
        ("03", "/chrome-extension-prospector productivity", "Run it"),
    ]
    cw = W - 120
    rh = 60
    y = 156
    for i, (n, cmd, note) in enumerate(cmds):
        rounded(d, [60, y, 60 + cw, y + rh - 8], 10, fill=CARD, outline=BORDER, width=1)
        d.text((80, y + 14), n, font=F_BOLD(22), fill=GREEN)
        d.text((130, y + 16), cmd, font=F_MONO(18), fill=TEXT)
        d.text((60 + cw - 24 - 240, y + 20), note, font=F_REG(15), fill=DIM)
        y += rh


    img.save(OUT / "setup.png", optimize=True)


if __name__ == "__main__":
    banner()
    flow()
    prospects_card()
    email_card()
    offers_chart()
    cost_card()
    setup_card()
    print("All assets written to", OUT)
