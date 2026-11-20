#!/usr/bin/env python3
"""The Daily Globe — Friday 20 November 2026 in one image.

Renders an editorial newspaper front page for make.fun's
news-image-20261120 competition. Everything (type, rules, charts, flags)
is drawn in code with Pillow; no network, no external images, fully
deterministic: the same bytes on every run.

Stories are the real top world news of 20 November 2026, researched
from live news sources on the day.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

W, H = 1024, 1024

PAPER = (247, 242, 231)      # warm newsprint
INK = (20, 20, 20)           # near-black text
NAVY = (14, 42, 71)          # masthead / callouts
NAVY_SOFT = (226, 232, 240)  # pale navy panel
RED = (176, 30, 36)          # kicker red
GOLD = (201, 162, 39)        # masthead rule
GREY = (107, 107, 107)       # small print
RULE = (60, 60, 60)          # hairlines
LIGHT_LINE = (190, 182, 166) # light dividers


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, fill, max_w, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in wrap(text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def text_h(text, fnt, max_w, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.28)
    return len(wrap(text, fnt, max_w)) * leading


def tracked(draw, cx, y, text, fnt, fill, tracking=6):
    """Draw centred text with letter tracking."""
    widths = [fnt.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def hline(draw, x0, x1, y, fill=RULE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vline(draw, x, y0, y1, fill=LIGHT_LINE, width=1):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


def kicker(draw, x, y, text, size=15):
    draw.text((x, y), text, font=SANS_B(size), fill=RED)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- masthead ----------
    d.rectangle([0, 0, W, 108], fill=NAVY)
    d.rectangle([0, 108, W, 112], fill=GOLD)
    d.text((26, 18), "FRIDAY", font=SANS_B(16), fill=(255, 255, 255))
    d.text((26, 42), "WORLD EDITION", font=SANS(13), fill=(190, 205, 220))
    date_txt = "20 NOVEMBER 2026"
    d.text((W - 26 - SANS_B(16).getlength(date_txt), 18), date_txt,
           font=SANS_B(16), fill=(255, 255, 255))
    d.text((W - 26 - SANS(13).getlength("No. 324 — ONE PAGE"), 42),
           "No. 324 — ONE PAGE", font=SANS(13), fill=(190, 205, 220))
    tracked(d, W // 2, 26, "THE DAILY GLOBE", SERIF_B(56),
            (255, 255, 255), tracking=7)
    d.text((W // 2 - SANS(13).getlength("THE WORLD IN ONE PAGE") // 2, 88),
           "THE WORLD IN ONE PAGE", font=SANS(13), fill=(201, 162, 39))

    # ---------- dateline strip ----------
    d.text((26, 124), "FRIDAY, 20 NOVEMBER 2026", font=SANS_B(14), fill=INK)
    mid = "SUMMING UP THE DAY'S WORLD NEWS"
    d.text((W // 2 - SANS(14).getlength(mid) // 2, 124), mid,
           font=SANS(14), fill=GREY)
    right = "PRICE: ONE PAGE OF NEWS"
    d.text((W - 26 - SANS_B(14).getlength(right), 124), right,
           font=SANS_B(14), fill=INK)
    hline(d, 26, W - 26, 146, fill=INK, width=2)
    hline(d, 26, W - 26, 150, fill=INK, width=1)

    return img, d


def lead_story(img, d):
    x0, x1 = 26, 998
    y = 168
    # kicker + headline
    kicker(d, x0, y, "THE HAGUE  •  WORLD COURT")
    y += 26
    headline = "World Court rules Myanmar committed genocide against the Rohingya"
    y = draw_wrapped(d, x0, y, headline, SERIF_B(38), INK, 700, leading=43)
    y += 8
    deck = ("Nine judges to six find the 2016\u201317 \u201cclearance operations\u201d in "
            "Rakhine State were genocide \u2014 the first ruling of its kind "
            "against a state for the Rohingya.")
    y = draw_wrapped(d, x0, y, deck, SERIF(19), (40, 40, 40), 700, leading=23)
    y += 12
    # two body columns under the headline
    col_w = 342
    body1 = ("THE HAGUE \u2014 The International Court of Justice ruled on "
             "Thursday that Myanmar committed genocide against the Rohingya "
             "during its 2016\u201317 \u201cclearance operations\u201d in Rakhine "
             "State, in the case brought by The Gambia.")
    body2 = ("The court ordered a reparations phase to follow. It is the "
             "first time the court has found a state guilty of genocide "
             "against the Rohingya \u2014 a verdict nine years in the making.")
    y1 = draw_wrapped(d, x0, y, body1, SERIF(15), INK, col_w, leading=17)
    y2 = draw_wrapped(d, x0 + col_w + 16, y, body2, SERIF(15), INK,
                      col_w, leading=17)
    body_bottom = max(y1, y2)

    # verdict callout box, right of the headline
    bx0, bx1 = 762, 998
    by0 = 194
    by1 = 416
    d.rectangle([bx0, by0, bx1, by1], outline=NAVY, width=2)
    d.rectangle([bx0, by0, bx1, by0 + 34], fill=NAVY)
    lbl = "THE VERDICT"
    d.text((bx0 + (bx1 - bx0 - SANS_B(14).getlength(lbl)) // 2, by0 + 9),
           lbl, font=SANS_B(14), fill=(255, 255, 255))
    vote = "9\u20136"
    d.text((bx0 + (bx1 - bx0 - SERIF_B(64).getlength(vote)) // 2, by0 + 44),
           vote, font=SERIF_B(64), fill=NAVY)
    d.text((bx0 + (bx1 - bx0 - SANS(13).getlength("judges to six")) // 2,
            by0 + 116), "judges to six", font=SANS(13), fill=GREY)
    hline(d, bx0 + 18, bx1 - 18, by0 + 142, fill=LIGHT_LINE, width=1)
    note = ("First genocide ruling of its kind. Reparations phase to "
            "follow.")
    draw_wrapped(d, bx0 + 18, by0 + 152, note, SERIF(14), INK,
                 bx1 - bx0 - 36, leading=19)
    return max(body_bottom, by1) + 4


def divider(d, y):
    hline(d, 26, 998, y, fill=INK, width=2)
    hline(d, 26, 998, y + 4, fill=INK, width=1)
    return y + 9


def flag_us(d, x, y, w, h):
    # thirteen stripes + blue canton with a field of dots
    stripe = h / 13
    for i in range(13):
        d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                    fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    cw, ch = w * 0.42, stripe * 7
    d.rectangle([x, y, x + cw, y + ch], fill=(30, 60, 120))
    for r in range(5):
        for c in range(6):
            cx = x + 6 + c * (cw - 12) / 5
            cy = y + 5 + r * (ch - 10) / 4
            d.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5],
                      fill=(255, 255, 255))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    # one big star, four small ones — drawn as 5-point polygons
    def star(cx, cy, r):
        import math
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.42
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.polygon(pts, fill=(255, 222, 0))
    star(x + w * 0.20, y + h * 0.28, h * 0.22)
    for sx, sy in [(0.42, 0.14), (0.52, 0.24), (0.52, 0.44), (0.42, 0.54)]:
        star(x + w * sx, y + h * sy, h * 0.09)


def flag_ru(d, x, y, w, h):
    for i, col in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
        d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=col)


def summit_story(img, d, y):
    x0 = 26
    y0 = y
    kicker(d, x0, y, "SHENZHEN  •  APEC SIDELINES")
    y += 26
    y = draw_wrapped(d, x0, y, "Three leaders, one table", SERIF_B(28),
                     INK, 640, leading=32)
    y += 6
    body = ("Trump, Xi and Putin meet for the first time \u2014 a three-way "
            "summit on the sidelines of APEC that ends with a joint "
            "declaration on peace. Resolving the war in Ukraine tops the "
            "agenda; nuclear disarmament is discussed too.")
    y = draw_wrapped(d, x0, y, body, SERIF(15), INK, 640, leading=19)
    # flags, right side, aligned with the headline
    fx = 700
    fy = y0 + 26
    fw, fh = 88, 58
    for i, (fn, label) in enumerate([(flag_us, "UNITED STATES"),
                                     (flag_cn, "CHINA"),
                                     (flag_ru, "RUSSIA")]):
        xx = fx + i * 100
        d.rectangle([xx - 2, fy - 2, xx + fw + 2, fy + fh + 2],
                    outline=RULE, width=1)
        fn(d, xx, fy, fw, fh)
        d.text((xx + (fw - SANS_B(10).getlength(label)) // 2, fy + fh + 8),
               label, font=SANS_B(10), fill=GREY)
    return y + 6


def markets_strip(img, d, y):
    x0, x1 = 26, 998
    y0 = y
    d.rectangle([x0, y0, x1, y0 + 96], fill=NAVY_SOFT)
    d.rectangle([x0, y0, x0 + 5, y0 + 96], fill=RED)
    d.text((x0 + 20, y0 + 8), "MARKETS", font=SANS_B(14), fill=RED)
    d.text((x0 + 20, y0 + 28),
           "Anthropic soars 17% on Nasdaq debut",
           font=SERIF_B(24), fill=NAVY)
    draw_wrapped(d, x0 + 20, y0 + 58,
                 "Shares close at about $97 on their first day of trading "
                 "\u2014 the biggest AI listing yet.",
                 SERIF(15), (40, 40, 40), 540, leading=18)
    # bar chart: IPO price vs close
    base = y0 + 82
    for i, (lab, val, hgt, col) in enumerate([
            ("IPO", 83, 28, (120, 130, 145)),
            ("CLOSE", 97, 50, NAVY)]):
        bx = 590 + i * 86
        d.rectangle([bx, base - hgt, bx + 56, base], fill=col)
        d.text((bx + 6, base - hgt - 18), f"${val}", font=SANS_B(14),
               fill=INK)
        d.text((bx + 2, base + 2), lab, font=SANS_B(10), fill=GREY)
    # +17% callout, far right
    pct = "+17%"
    d.text((x1 - 24 - SERIF_B(40).getlength(pct), y0 + 8), pct,
           font=SERIF_B(40), fill=RED)
    val = "VALUED AT $1.76 TRILLION"
    d.text((x1 - 24 - SANS_B(13).getlength(val), y0 + 56), val,
           font=SANS_B(13), fill=NAVY)
    return y0 + 96 + 4


def briefs_grid(img, d, y):
    briefs = [
        ("HOUTHIS STRIKE SAUDI",
         "Drones and missiles hit four targets",
         "Riyadh airport and a petrochemical plant among the sites "
         "attacked."),
        ("KYIV UNDER FIRE",
         "Four ballistic missiles hit capital",
         "Ukraine's capital is struck in the latest wave of attacks."),
        ("GENOA GROUNDED",
         "Airport shut for four hours",
         "Flights suspended overnight after drones are spotted."),
        ("CYCLONE AKVAN",
         "80,000 evacuated on India's east coast",
         "The storm bears down on Odisha after weakening over the Bay of "
         "Bengal."),
        ("BANKS BREACHED",
         "JPMorgan, Visa, Mastercard hit",
         "Cyber incidents leak data of thousands of customers."),
        ("MINE IN THE GULF",
         "Tanker ablaze east of Hormuz",
         "The vessel catches fire after striking a mine in the Strait of "
         "Hormuz."),
    ]
    col_w = 308
    gap = 20
    row_h = 82
    for idx, (label, head, body) in enumerate(briefs):
        col = idx % 3
        row = idx // 3
        x = 26 + col * (col_w + gap)
        yy = y + row * row_h
        d.text((x, yy), label, font=SANS_B(12), fill=RED)
        yy = draw_wrapped(d, x, yy + 17, head, SERIF_B(15), INK, col_w,
                          leading=18)
        draw_wrapped(d, x, yy + 2, body, SANS(12), (50, 50, 50), col_w,
                     leading=15)
        if col < 2:
            vline(d, x + col_w + 10, y + row * row_h + 2,
                  y + (row + 1) * row_h - 12)
    return y + 2 * row_h + 4


def footer(img, d, y):
    hline(d, 26, 998, y, fill=INK, width=1)
    ticker = ("ALSO TODAY:  Haiti raid kills 34  \u2022  Bukele seeks a third "
              "term  \u2022  Gaza aid call  \u2022  Eisenkot tapped in Israel  "
              "\u2022  NZ 368 all out in 1st Test")
    y = draw_wrapped(d, 26, y + 10, ticker, SANS_B(12), INK, 972,
                     leading=14)
    y += 2
    src = ("Sources: ICJ \u2022 NYT \u2022 AFP \u2022 BBC \u2022 Reuters \u2022 "
           "AP \u2022 TASS  \u2014  All type, charts and flags drawn in code. "
           "The Daily Globe, 20 November 2026.")
    d.text((26, y), src, font=SANS(11), fill=GREY)


def main():
    img, d = build()
    y = lead_story(img, d)
    y = divider(d, y + 6)
    y = summit_story(img, d, y + 4)
    y = divider(d, y + 6)
    y = markets_strip(img, d, y + 4)
    y = divider(d, y + 6)
    y = briefs_grid(img, d, y + 4)
    footer(img, d, y + 2)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "entry.png")
    img.save(out, format="PNG")
    print(f"wrote {out} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
