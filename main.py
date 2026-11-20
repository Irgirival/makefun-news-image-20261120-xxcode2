#!/usr/bin/env python3
"""The Daily Globe — Friday 20 November 2026 in one image.

Renders an editorial newspaper front page for make.fun's
news-image-20261120 competition. Everything (type, rules, charts, flags)
is drawn in code; no network, no external images, fully deterministic:
the same bytes on every run.

Pure Python standard library only (os, struct, zlib). No third-party
packages: the grader runs the entry in a stock python:3.13-slim image
with no Pillow installed, so all rendering is done here — a hand-built
5x7 bitmap font, a scanline polygon filler, and a hand-written PNG
encoder. The page is rendered at 2x and box-downsampled to 1024x1024
for smooth edges.

Stories are the real top world news of 20 November 2026, researched
from live news sources on the day.
"""

import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

W, H = 1024, 1024
S = 2  # supersampling factor: render at 2048, downsample to 1024

PAPER = (247, 242, 231)      # warm newsprint
INK = (20, 20, 20)           # near-black text
NAVY = (14, 42, 71)          # masthead / callouts
NAVY_SOFT = (226, 232, 240)  # pale navy panel
RED = (176, 30, 36)          # kicker red
GOLD = (201, 162, 39)        # masthead rule
GREY = (107, 107, 107)       # small print
RULE = (60, 60, 60)          # hairlines
LIGHT_LINE = (190, 182, 166)  # light dividers

# ---------------------------------------------------------------- font
# Hand-built 5x7 bitmap font, one tuple of 7 rows per glyph.
# '#' is on, '.' is off. Written for this entry from scratch.
FONT = {
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '$': ("..#..", ".####.", "#.#...", ".###..", "..#.#.", ".####.", "..#.."),
    '%': ("##..#", "##.#..", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '&': (".###.", "#...#", "#...#", ".#.#.", "#.#..", "#..#.", ".##.#"),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '*': (".....", "#...#", ".###.", "#####", ".###.", "#...#", "....."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    ',': (".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.#.#", "#....", ".###."),
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    '\\': ("#....", "#....", ".#...", "..#..", "...#.", "...#.", "....#"),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    '^': ("..#..", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '`': (".#...", ".#...", "..#..", ".....", ".....", ".....", "....."),
}
FONT.update({
    'a': (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".###.", "#....", "#....", "#...#", ".###."),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", ".###."),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", ".###."),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '{': ("..##.", ".#...", ".#...", ".##..", ".#...", ".#...", "..##."),
    '|': ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    '}': (".##..", "...#.", "...#.", "..##.", "...#.", "...#.", ".##.."),
    '~': (".....", ".....", ".##.#", "#.#.#", ".....", ".....", "....."),
    # extra glyphs for characters used in the copy
    '\u2022': (".....", "..#..", ".###.", ".###.", ".###.", "..#..", "....."),
    '\u2014': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '\u2013': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '\u2018': ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '\u2019': ("..#..", "..#..", "...#.", ".....", ".....", ".....", "....."),
    '\u201c': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '\u201d': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
})

UNKNOWN = FONT['?']


def normalize(text):
    """Fold characters we carry no glyph for to plain ASCII."""
    return text.replace('\u2026', '...').replace('\u00a0', ' ')


# ---------------------------------------------------------------- canvas
# All layout coordinates are in final 1024x1024 pixels; the framebuffer
# is 2x (2048x2048) and box-downsampled at the end.
CW = W * S
CH = H * S


class Canvas:
    def __init__(self):
        self.px = bytearray(CW * CH * 3)

    def _off(self, x, y):
        return (y * CW + x) * 3

    def plot(self, x, y, color):
        """Plot one supersampled pixel; x, y are canvas coordinates."""
        if 0 <= x < CW and 0 <= y < CH:
            o = self._off(x, y)
            self.px[o] = color[0]
            self.px[o + 1] = color[1]
            self.px[o + 2] = color[2]

    def fill_rect(self, x0, y0, x1, y1, color):
        """Fill a rectangle; coordinates are FINAL pixels, x1/y1 exclusive."""
        ax0, ay0 = max(0, x0 * S), max(0, y0 * S)
        ax1, ay1 = min(CW, x1 * S), min(CH, y1 * S)
        r, g, b = color
        for y in range(ay0, ay1):
            o = (y * CW + ax0) * 3
            for x in range(ax0, ax1):
                self.px[o] = r
                self.px[o + 1] = g
                self.px[o + 2] = b
                o += 3

    def hline(self, x0, x1, y, color, width=1):
        for w in range(width):
            yy = y * S + w
            for x in range(x0 * S, x1 * S):
                self.plot(x, yy, color)

    def vline(self, x, y0, y1, color, width=1):
        for w in range(width):
            xx = x * S + w
            for y in range(y0 * S, y1 * S):
                self.plot(xx, y, color)

    def rect_outline(self, x0, y0, x1, y1, color, width=1):
        self.fill_rect(x0, y0, x1, y0 + width, color)
        self.fill_rect(x0, y1 - width, x1, y1, color)
        self.fill_rect(x0, y0, x0 + width, y1, color)
        self.fill_rect(x1 - width, y0, x1, y1, color)

    def disc(self, cx, cy, r, color):
        """Filled disc; cx, cy, r are FINAL pixels (r may be fractional)."""
        ccx, ccy, rr = cx * S, cy * S, r * S
        x0 = int(ccx - rr)
        x1 = int(ccx + rr) + 1
        y0 = int(ccy - rr)
        y1 = int(ccy + rr) + 1
        for y in range(y0, y1):
            dy = y + 0.5 - ccy
            dx = (rr * rr - dy * dy) ** 0.5 if rr * rr - dy * dy > 0 else 0
            for x in range(max(x0, int(ccx - dx)), min(x1, int(ccx + dx) + 1)):
                self.plot(x, y, color)

    def polygon(self, pts, color):
        """Scanline even-odd fill; pts are (x, y) in FINAL pixels."""
        if len(pts) < 3:
            return
        cpts = [(x * S, y * S) for x, y in pts]
        ys = [p[1] for p in cpts]
        y0, y1 = int(min(ys)), int(max(ys)) + 1
        for y in range(y0, y1):
            yc = y + 0.5
            xs = []
            n = len(cpts)
            for i in range(n):
                x0, y0p = cpts[i]
                x1, y1p = cpts[(i + 1) % n]
                if (y0p <= yc < y1p) or (y1p <= yc < y0p):
                    if y1p != y0p:
                        xs.append(x0 + (yc - y0p) * (x1 - x0) / (y1p - y0p))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.plot(x, y, color)


def star_points(cx, cy, r):
    """Five-point star vertices; cx, cy, r in FINAL pixels."""
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return pts

# ---------------------------------------------------------------- text
# A glyph at font scale s occupies 5*s canvas px wide and 7*s tall;
# advance is 6*s canvas px (5 + 1 spacing). In FINAL pixels that is
# 2.5*s wide, 3.5*s tall, 3*s advance. fs() picks s for a target
# final-pixel cap height.


def fs(px):
    """Font scale for a target final-pixel text height."""
    return max(1, round(px * 2 / 7))


def glyph(ch):
    return FONT.get(ch, UNKNOWN)


def text_w(text, s, tracking=0):
    """Width of text in FINAL pixels at font scale s."""
    n = len(text)
    if n == 0:
        return 0
    # advance per char is 6*s canvas px = 3*s final px; tracking is extra
    # final px between chars (not after the last one).
    return 3 * s * n + tracking * (n - 1)


def wrap(text, s, max_w, tracking=0):
    """Greedy word wrap; returns a list of lines fitting max_w (final px)."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(trial, s, tracking) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text(c, x, y, text, s, color, tracking=0):
    """Draw text at final coords (x, y = top-left); returns width used."""
    cx = x * S
    cy = y * S
    adv = 6 * s
    trk = tracking * S  # tracking is in final px; convert to canvas px
    for i, ch in enumerate(text):
        g = glyph(ch)
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == '#':
                    for dy in range(s):
                        for dx in range(s):
                            c.plot(cx + col * s + dx, cy + row * s + dy, color)
        cx += adv
        if i < len(text) - 1:
            cx += trk
    return (cx - x * S) // S


def text_h(text, s, max_w, leading=None):
    if leading is None:
        leading = int(7 * s * 1.28) // S
    return len(wrap(text, s, max_w)) * leading


def draw_wrapped(c, x, y, text, s, color, max_w, leading=None, tracking=0):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(7 * s * 1.28) // S
    for line in wrap(text, s, max_w, tracking):
        draw_text(c, x, y, line, s, color, tracking)
        y += leading
    return y


def tracked(c, cx, y, text, s, color, tracking=6):
    """Draw centred text with letter tracking; cx is the centre (final px)."""
    w = text_w(text, s, tracking)
    draw_text(c, cx - w // 2, y, text, s, color, tracking)


# ---------------------------------------------------------------- png
def encode_png(rgb, w, h):
    """Encode raw RGB bytes as a PNG; deterministic (zlib level 9)."""
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(ctype, data):
        out = struct.pack(">I", len(data)) + ctype + data
        return out + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def downsample(fb):
    """Box-average the 2x framebuffer down to 1024x1024 RGB bytes."""
    out = bytearray(W * H * 3)
    for y in range(H):
        for x in range(W):
            o = (y * W + x) * 3
            acc = [0, 0, 0]
            for dy in range(S):
                for dx in range(S):
                    so = (((y * S + dy) * CW) + (x * S + dx)) * 3
                    acc[0] += fb[so]
                    acc[1] += fb[so + 1]
                    acc[2] += fb[so + 2]
            out[o] = (acc[0] + 2) // 4
            out[o + 1] = (acc[1] + 2) // 4
            out[o + 2] = (acc[2] + 2) // 4
    return bytes(out)

# ---------------------------------------------------------------- sections
def kicker(c, x, y, text):
    draw_text(c, x, y, normalize(text), fs(15), RED)


def divider(c, y):
    c.hline(26, 998, y, INK, 2)
    c.hline(26, 998, y + 4, INK, 1)
    return y + 9


def build(c):
    c.fill_rect(0, 0, W, H, PAPER)
    # masthead
    c.fill_rect(0, 0, W, 100, NAVY)
    c.fill_rect(0, 100, W, 104, GOLD)
    draw_text(c, 26, 18, "FRIDAY", fs(13), (255, 255, 255))
    draw_text(c, 26, 42, "WORLD EDITION", fs(13), (190, 205, 220))
    date_txt = "20 NOVEMBER 2026"
    draw_text(c, W - 26 - text_w(date_txt, fs(13)), 18, date_txt,
              fs(13), (255, 255, 255))
    tracked(c, W // 2, 26, "THE DAILY GLOBE", fs(42), (255, 255, 255),
            tracking=2)
    mid = "THE WORLD IN ONE PAGE"
    draw_text(c, W // 2 - text_w(mid, fs(13)) // 2, 84, mid, fs(13),
              (201, 162, 39))
    draw_text(c, W - 26 - text_w("No. 324 - ONE PAGE", fs(13)), 84,
              "No. 324 - ONE PAGE", fs(13), (190, 205, 220))
    # dateline strip
    draw_text(c, 26, 116, "FRIDAY, 20 NOVEMBER 2026", fs(14), INK)
    mid = "SUMMING UP THE DAY'S WORLD NEWS"
    draw_text(c, W // 2 - text_w(mid, fs(14)) // 2, 116, mid, fs(14), GREY)
    right = "PRICE: ONE PAGE OF NEWS"
    draw_text(c, W - 26 - text_w(right, fs(14)), 116, right, fs(14), INK)
    c.hline(26, W - 26, 138, INK, 2)
    c.hline(26, W - 26, 142, INK, 1)


def lead_story(c):
    x0, x1 = 26, 998
    y = 160
    kicker(c, x0, y, "THE HAGUE  \u2022  WORLD COURT")
    y += 22
    headline = "World Court rules Myanmar committed genocide against the Rohingya"
    y = draw_wrapped(c, x0, y, normalize(headline), fs(35), INK, 700,
                     leading=38)
    y += 6
    deck = ("Nine judges to six find the 2016-17 \u201cclearance operations\u201d in "
            "Rakhine State were genocide \u2014 the first ruling of its kind "
            "against a state for the Rohingya.")
    y = draw_wrapped(c, x0, y, normalize(deck), fs(14), (40, 40, 40), 700,
                     leading=16)
    y += 8
    col_w = 342
    body1 = ("THE HAGUE \u2014 The International Court of Justice ruled on "
             "Thursday that Myanmar committed genocide against the Rohingya "
             "during its 2016-17 \u201cclearance operations\u201d in Rakhine "
             "State.")
    body2 = ("The court ordered a reparations phase to follow. It is the "
             "first time the court has found a state guilty of genocide "
             "against the Rohingya \u2014 a verdict nine years in the making.")
    y1 = draw_wrapped(c, x0, y, normalize(body1), fs(15), INK, col_w,
                      leading=17)
    y2 = draw_wrapped(c, x0 + col_w + 16, y, normalize(body2), fs(15), INK,
                      col_w, leading=17)
    body_bottom = max(y1, y2)
    # verdict callout box, right of the headline
    bx0, bx1 = 762, 998
    by0 = 186
    by1 = 408
    c.rect_outline(bx0, by0, bx1, by1, NAVY, 2)
    c.fill_rect(bx0, by0, bx1, by0 + 34, NAVY)
    lbl = "THE VERDICT"
    draw_text(c, bx0 + (bx1 - bx0 - text_w(lbl, fs(14))) // 2, by0 + 9,
              lbl, fs(14), (255, 255, 255))
    vote = "9-6"
    draw_text(c, bx0 + (bx1 - bx0 - text_w(vote, fs(64))) // 2, by0 + 44,
              vote, fs(64), NAVY)
    draw_text(c, bx0 + (bx1 - bx0 - text_w("judges to six", fs(13))) // 2,
              by0 + 116, "judges to six", fs(13), GREY)
    c.hline(bx0 + 18, bx1 - 18, by0 + 142, LIGHT_LINE, 1)
    note = ("First genocide ruling of its kind. Reparations phase to "
            "follow.")
    draw_wrapped(c, bx0 + 18, by0 + 152, normalize(note), fs(11), INK,
                 bx1 - bx0 - 36, leading=13)
    return max(body_bottom, by1) + 4


def flag_us(c, x, y, w, h):
    stripe = h / 13
    for i in range(13):
        c.fill_rect(x, int(y + i * stripe), x + w,
                    int(y + (i + 1) * stripe),
                    (178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    cw, ch = w * 0.42, stripe * 7
    c.fill_rect(x, y, int(x + cw), int(y + ch), (30, 60, 120))
    for r in range(5):
        for cc in range(6):
            cx = x + 6 + cc * (cw - 12) / 5
            cy = y + 5 + r * (ch - 10) / 4
            c.disc(cx, cy, 1.5, (255, 255, 255))


def flag_cn(c, x, y, w, h):
    c.fill_rect(x, y, x + w, y + h, (222, 41, 16))
    c.polygon(star_points(x + w * 0.20, y + h * 0.28, h * 0.22),
              (255, 222, 0))
    for sx, sy in [(0.42, 0.14), (0.52, 0.24), (0.52, 0.44), (0.42, 0.54)]:
        c.polygon(star_points(x + w * sx, y + h * sy, h * 0.09),
                  (255, 222, 0))


def flag_ru(c, x, y, w, h):
    for i, col in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
        c.fill_rect(x, int(y + i * h / 3), x + w,
                    int(y + (i + 1) * h / 3), col)


def summit_story(c, y):
    x0 = 26
    y0 = y
    kicker(c, x0, y, "SHENZHEN  \u2022  APEC SIDELINES")
    y += 22
    y = draw_wrapped(c, x0, y, "Three leaders, one table", fs(28),
                     INK, 640, leading=32)
    y += 4
    body = ("Trump, Xi and Putin meet for the first time \u2014 a three-way "
            "summit on the sidelines of APEC that ends with a joint "
            "declaration on peace. Resolving the war in Ukraine tops the "
            "agenda; nuclear disarmament is discussed too.")
    y = draw_wrapped(c, x0, y, normalize(body), fs(15), INK, 640,
                     leading=19)
    fx = 700
    fy = y0 + 26
    fw, fh = 88, 58
    for i, (fn, label) in enumerate([(flag_us, "UNITED STATES"),
                                     (flag_cn, "CHINA"),
                                     (flag_ru, "RUSSIA")]):
        xx = fx + i * 100
        c.rect_outline(xx - 2, fy - 2, xx + fw + 2, fy + fh + 2, RULE, 1)
        fn(c, xx, fy, fw, fh)
        draw_text(c, xx + (fw - text_w(label, fs(10))) // 2, fy + fh + 8,
                  label, fs(10), GREY)
    return y + 6


def markets_strip(c, y):
    x0, x1 = 26, 998
    y0 = y
    c.fill_rect(x0, y0, x1, y0 + 90, NAVY_SOFT)
    c.fill_rect(x0, y0, x0 + 5, y0 + 90, RED)
    draw_text(c, x0 + 20, y0 + 8, "MARKETS", fs(14), RED)
    draw_text(c, x0 + 20, y0 + 26,
              "Anthropic soars 17% on Nasdaq debut",
              fs(18), NAVY)
    draw_wrapped(c, x0 + 20, y0 + 52,
                 "Shares close at about $97 on their first day of trading "
                 "\u2014 the biggest AI listing yet.",
                 fs(15), (40, 40, 40), 540, leading=18)
    base = y0 + 78
    for i, (lab, val, hgt, col) in enumerate([
            ("IPO", 83, 28, (120, 130, 145)),
            ("CLOSE", 97, 50, NAVY)]):
        bx = 590 + i * 86
        c.fill_rect(bx, base - hgt, bx + 56, base, col)
        draw_text(c, bx + 6, base - hgt - 18, "$%d" % val, fs(14), INK)
        draw_text(c, bx + 2, base + 2, lab, fs(10), GREY)
    pct = "+17%"
    draw_text(c, x1 - 24 - text_w(pct, fs(40)), y0 + 8, pct, fs(40), RED)
    val = "VALUED AT $1.76 TRILLION"
    draw_text(c, x1 - 24 - text_w(val, fs(11)), y0 + 56, val, fs(11), NAVY)
    return y0 + 90 + 4


def briefs_grid(c, y):
    briefs = [
        ("HOUTHIS STRIKE SAUDI",
         "Drones hit four targets",
         "Riyadh airport and a petrochemical plant hit."),
        ("KYIV UNDER FIRE",
         "Four missiles hit capital",
         "Ukraine's capital is struck in the latest attacks."),
        ("GENOA GROUNDED",
         "Airport shut four hours",
         "Flights suspended overnight after drones spotted."),
        ("CYCLONE AKVAN",
         "80,000 evacuated",
         "Storm bears down on Odisha after weakening."),
        ("BANKS BREACHED",
         "Banks hit in data breach",
         "Cyber incidents leak data of thousands."),
        ("MINE IN THE GULF",
         "Tanker ablaze off Hormuz",
         "Vessel catches fire after striking a mine."),
    ]
    col_w = 308
    gap = 20
    row_h = 72
    for idx, (label, head, body) in enumerate(briefs):
        col = idx % 3
        row = idx // 3
        x = 26 + col * (col_w + gap)
        yy = y + row * row_h
        draw_text(c, x, yy, normalize(label), fs(12), RED)
        yy = draw_wrapped(c, x, yy + 14, normalize(head), fs(15), INK,
                          col_w, leading=18)
        draw_wrapped(c, x, yy + 1, normalize(body), fs(12), (50, 50, 50),
                     col_w, leading=13)
        if col < 2:
            c.vline(x + col_w + 10, y + row * row_h + 2,
                    y + (row + 1) * row_h - 12, LIGHT_LINE, 1)
    return y + 2 * row_h + 4


def footer(c, y):
    c.hline(26, 998, y, INK, 1)
    ticker = ("ALSO TODAY:  Haiti raid kills 34  \u2022  Bukele seeks third "
              "term  \u2022  Gaza aid call  \u2022  Eisenkot tapped  \u2022  "
              "NZ 368 all out")
    y = draw_wrapped(c, 26, y + 10, normalize(ticker), fs(12), INK, 972,
                     leading=14)
    y += 2
    src = ("Sources: ICJ \u2022 NYT \u2022 AFP \u2022 BBC \u2022 Reuters \u2022 "
           "AP \u2022 TASS  \u2014  All type, charts and flags drawn in code.")
    draw_text(c, 26, y, normalize(src), fs(11), GREY)
    return y


def main():
    c = Canvas()
    build(c)
    y = lead_story(c)
    y = divider(c, y + 4)
    y = summit_story(c, y + 4)
    y = divider(c, y + 4)
    y = markets_strip(c, y + 4)
    y = divider(c, y + 4)
    y = briefs_grid(c, y + 4)
    y = footer(c, y)
    print("content bottom y=%d (page height %d)" % (y, H))
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "entry.png")
    with open(out, "wb") as f:
        f.write(encode_png(downsample(c.px), W, H))
    print("wrote %s (%dx%d)" % (out, W, H))


if __name__ == "__main__":
    main()
