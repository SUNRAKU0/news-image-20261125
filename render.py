#!/usr/bin/env python3
"""Render the news-image-20261125 front page.
PIL + Noto fonts: exact, legible text, no AI generation. Headless Chromium is
blocked in this VM by the Hatch WebGL domain policy.
Layout follows the proven 24 Nov front page (masthead, lead story, 3 + 2 panels,
footer brief strip), with new stories for Wednesday 25 November 2026."""
from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1024, 1024
PAPER = (248, 244, 236)
INK = (20, 20, 20)
MUTED = (90, 84, 72)
NAVY = (26, 42, 74)
GREEN = (18, 110, 60)
RED = (158, 32, 32)
TEAL = (12, 96, 96)
GOLD = (176, 124, 24)

SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_BLK = "/usr/share/fonts/truetype/noto/NotoSerif-Black.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
SANS_BLK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    lh = leading or int(fnt.size * 1.18)
    for ln in wrap(draw, text, fnt, max_w):
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------- frame ----------
d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=3)
d.rectangle([16, 16, W - 17, H - 17], outline=INK, width=1)

# ---------- masthead ----------
cx = W // 2
d.text((cx, 34), "THE WORLD TODAY", font=font(SERIF_BLK, 84), fill=INK, anchor="ma")
d.line([(40, 138), (W - 40, 138)], fill=INK, width=3)
d.line([(40, 144), (W - 40, 144)], fill=INK, width=1)
d.text((cx, 158), "WEDNESDAY,  25  NOVEMBER  2026", font=font(SANS_BLK, 28), fill=NAVY, anchor="ma")
d.text((44, 162), "WORLD NEWS", font=font(SANS_B, 16), fill=MUTED, anchor="la")
d.text((W - 44, 162), "SIX STORIES  •  ONE DAY", font=font(SANS_B, 16), fill=MUTED, anchor="ra")

# ---------- lead story: Putin retaliation ----------
LX, LY, LW, LH = 30, 196, 964, 256
d.rectangle([LX, LY, LX + LW, LY + LH], outline=INK, width=2)
tx = LX + 24
d.text((tx, LY + 14), "RUSSIA  •  UKRAINE", font=font(SANS_B, 17), fill=RED)
d.text((LX + LW - 24, LY + 14), "LEAD STORY", font=font(SANS_B, 17), fill=RED, anchor="ra")
hy = LY + 42
hy = draw_wrapped(d, tx, hy, "Putin vows \u201cinevitable\u201d retaliation for Ukraine\u2019s refinery strikes",
                  font(SERIF_B, 40), 620, leading=46)
draw_wrapped(d, tx, hy + 10,
             "Kyiv keeps hitting Russian refineries despite President Trump\u2019s "
             "request to stop.",
             font(SANS, 21), 620, fill=(50, 48, 44), leading=27)
# lead illustration: explosion starburst on dark red, "RETALIATION" below
ix, iy = 716, LY + 26
d.rounded_rectangle([ix, iy + 28, ix + 200, iy + 168], radius=14, fill=(96, 20, 20))
cx0, cy0 = ix + 100, iy + 98
pts = []
for i in range(16):
    r = 52 if i % 2 == 0 else 24
    a = math.radians(i * 22.5 - 90)
    pts.append((cx0 + r * math.cos(a), cy0 + r * math.sin(a)))
d.polygon(pts, fill=(240, 150, 40))
d.ellipse([cx0 - 14, cy0 - 14, cx0 + 14, cy0 + 14], fill=(255, 210, 90))
d.text((ix + 100, iy + 192), "RETALIATION", font=font(SANS_BLK, 24), fill=RED, anchor="ma")

# ---------- story panels ----------
def panel(x, y, w, h, kicker, kcolor, headline, summary, icon, hsize=24, ssize=17):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    d.text((x + 16, y + 12), kicker, font=font(SANS_B, 15), fill=kcolor)
    icon(x + w - 52, y + 8, 40)
    hy = y + 56
    hy = draw_wrapped(d, x + 16, hy, headline, font(SERIF_B, hsize), w - 32,
                      leading=int(hsize * 1.16))
    end = draw_wrapped(d, x + 16, hy + 6, summary, font(SANS, ssize), w - 32,
                       fill=(50, 48, 44), leading=int(ssize * 1.24))
    if end > y + h - 6:
        print(f"OVERFLOW in panel '{kicker}': text ends at y={end}, panel bottom {y + h}")
    return end

def icon_ship(x, y, s):
    d.rounded_rectangle([x, y, x + s, y + s], radius=7, fill=(214, 232, 240))
    for k in range(3):
        d.arc([x + 2 + k * 12, y + s - 12, x + 14 + k * 12, y + s - 2], 0, 180,
              fill=(40, 110, 160), width=2)
    d.polygon([(x + 5, y + s - 20), (x + s - 5, y + s - 20), (x + s - 9, y + s - 11),
               (x + 9, y + s - 11)], fill=(40, 40, 48))
    d.rectangle([x + 9, y + s - 30, x + 17, y + s - 20], fill=(40, 40, 48))
    d.rectangle([x + 22, y + s - 27, x + 32, y + s - 20], fill=(120, 40, 40))
    mx, my, r = x + s - 11, y + 9, 5
    for a in range(0, 360, 45):
        x1 = mx + int(r * 1.9 * math.cos(math.radians(a)))
        y1 = my + int(r * 1.9 * math.sin(math.radians(a)))
        d.line([(mx, my), (x1, y1)], fill=INK, width=2)
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=INK)

def icon_tower(x, y, s):
    d.rounded_rectangle([x, y, x + s, y + s], radius=7, fill=(240, 226, 210))
    cx0 = x + s // 2
    d.rectangle([cx0 - 6, y + 12, cx0 + 6, y + s - 6], fill=(70, 60, 55))
    for wy in range(y + 16, y + s - 8, 7):
        d.line([(cx0 - 6, wy), (cx0 + 6, wy)], fill=(240, 226, 210), width=1)
    d.polygon([(cx0 - 3, y + 2), (cx0 + 3, y + 2), (cx0, y + 12)], fill=(70, 60, 55))
    bx, by = x + s - 13, y + 6
    pts = []
    for i in range(12):
        r = 9 if i % 2 == 0 else 4
        a = math.radians(i * 30 - 90)
        pts.append((bx + r * math.cos(a), by + r * math.sin(a)))
    d.polygon(pts, fill=(230, 110, 30))

def icon_shop(x, y, s):
    d.rounded_rectangle([x, y, x + s, y + s], radius=7, fill=(232, 240, 232))
    d.rectangle([x + 5, y + 14, x + s - 5, y + s - 5], fill=(250, 250, 250), outline=INK, width=1)
    for k in range(5):
        d.rectangle([x + 5 + k * 6, y + 8, x + 10 + k * 6, y + 14],
                    fill=RED if k % 2 == 0 else (250, 250, 250))
    d.rectangle([x + 14, y + 22, x + s - 14, y + s - 5], fill=(90, 90, 90))

def icon_office(x, y, s):
    d.rounded_rectangle([x, y, x + s, y + s], radius=7, fill=(226, 232, 240))
    d.rectangle([x + 10, y + 14, x + s - 10, y + s - 5], fill=(120, 130, 150))
    for wy in range(y + 18, y + s - 8, 8):
        d.line([(x + 13, wy), (x + s - 13, wy)], fill=(220, 230, 240), width=2)
    d.rectangle([x + s - 16, y + 3, x + s - 3, y + 16], fill=(200, 30, 30))
    d.rectangle([x + s - 12, y + 8, x + s - 7, y + 11], fill=(255, 255, 255))
    d.rectangle([x + s - 11, y + 6, x + s - 8, y + 13], fill=(255, 255, 255))

def icon_satellite(x, y, s):
    d.rounded_rectangle([x, y, x + s, y + s], radius=7, fill=(222, 228, 244))
    cx0, cy0 = x + s // 2, y + s // 2
    d.ellipse([cx0 - 18, cy0 - 18, cx0 + 18, cy0 + 18], outline=NAVY, width=2)
    d.rectangle([cx0 - 5, cy0 - 4, cx0 + 5, cy0 + 4], fill=NAVY)
    d.rectangle([cx0 - 15, cy0 - 3, cx0 - 6, cy0 + 3], fill=(90, 120, 200))
    d.rectangle([cx0 + 6, cy0 - 3, cx0 + 15, cy0 + 3], fill=(90, 120, 200))
    d.line([(cx0, cy0 - 4), (cx0 + 4, cy0 - 12)], fill=NAVY, width=2)
    d.ellipse([cx0 + 2, cy0 - 14, cx0 + 6, cy0 - 10], fill=GOLD)

# row B: three panels (taller)
BY, BH = 468, 236
PW = 312
panel(30, BY, PW, BH, "UKRAINE  •  BALTIC", NAVY,
      "Zelenskiy confirms Baltic strike on Russian cargo ship Sparta II",
      "Ukraine hit the Sparta II in the Gulf of Finland; Norway urges caution.",
      icon_ship)
panel(356, BY, PW, BH, "MIDDLE EAST", RED,
      "Houthi strike on Riyadh\u2019s tallest tower wounds 11",
      "Houthis threaten Saudi Red Sea ports after the attack on the capital.",
      icon_tower)
panel(682, BY, PW, BH, "LATIN AMERICA", TEAL,
      "Gunmen seize Cartagena supermarket, hold at least 30 hostage",
      "Armed men took hostages after a failed cash-truck robbery; five elderly women freed.",
      icon_shop)

# row C: two panels
CY, CH = 716, 208
CW = 474
panel(30, CY, CW, CH, "ASIA  •  DIPLOMACY", TEAL,
      "Kim Yo-jong threatens to close Switzerland\u2019s office in Pyongyang",
      "North Korea threatens the Swiss diplomatic office over sanctions on a youth camp.",
      icon_office, hsize=26, ssize=18)
panel(520, CY, CW, CH, "DEFENSE  •  SPACE", NAVY,
      "NATO vows to defend space as Russia readies nuclear-armed satellite",
      "The alliance pledges space defense amid reports of a possible Russian launch in December 2026.",
      icon_satellite, hsize=26, ssize=18)

# ---------- footer strip (two lines of briefs) ----------
FY = 932
d.rectangle([30, FY, 994, FY + 64], fill=NAVY)
d.text((48, FY + 20), "ALSO TODAY", font=font(SANS_BLK, 17), fill=(255, 210, 90))
line1 = ("Sarkozy case ordered to trial  \u2022  S. Korea minister quits over exam cheating  "
         "\u2022  Australia\u2013Solomons pact signed")
line2 = ("Dutch climate targets binding, court rules  \u2022  Asian tech shares slide  "
         "\u2022  Trump pardons turkeys Freedom and Feathers")
for i, ln in enumerate((line1, line2)):
    fsize = 15
    while d.textlength(ln, font=font(SANS, fsize)) > 994 - 180 - 16 and fsize > 11:
        fsize -= 1
    d.text((180, FY + 8 + i * 26), ln, font=font(SANS, fsize), fill=(255, 255, 255))
    print("footer line", i + 1, "font", fsize)

img.save("/home/hatch/workspace/makefun-news-image-20261125/work/entry.png")
print("saved entry.png")
