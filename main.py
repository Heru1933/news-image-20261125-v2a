#!/usr/bin/env python3
"""news-image-20261125 v2 -- "THE BRUSSELS FILE" magazine.

One 1024x1024 PNG summing up Wednesday 25 November 2026: a magazine
front page. Deep-blue masthead, hero story #28 (the EU unveils a
50-billion-euro fund for AI and quantum computing) with a big toon
still, a deck and a small Europe locator map, seven more toon
illustrations in two picture rows, and all 40 verified 25-November
hard-news stories as a three-column numbered list with a source on
every line. Pure Python standard library. Deterministic: two runs
write byte-identical files.

Research: 40 stories, all events of 25 Nov 2026, hard news only:
NEWS25-V2 stories 1-25, 27-38 and 40, plus replacements 41
(Australia passes its online-safety law, Reuters/AP 25 Nov) and 42
(the US shelves its business-deal offer to Russia, Reuters/FT
25 Nov). Stories 26 (a report dated 24 Nov) and 39 (a launch dated
23 Nov) were dropped after date checks. Story 25 is the confirmed
48-hour Hormuz reopening offer only; the unconfirmed MQ-9 claim is
not used. Story 42 is a supporting item, not a headline.

Layout (1024x1024, cream magazine paper, blue / gold / red):
  masthead band, hero headline, hero row (still + deck + locator map),
  "THE DAY IN PICTURES" (4 tiles, then 3 tiles), 40-story
  three-column list, footer naming the date and the sources.
"""
import hashlib
import os
import struct
import zlib

W = 1024
H = 1024
HERE = os.path.dirname(os.path.abspath(__file__))

PAPER = (250, 246, 236)   # warm magazine cream
INK = (20, 20, 26)
BLUE = (13, 42, 106)      # masthead blue
GOLD = (232, 185, 59)
RED = (178, 34, 34)
GREY = (96, 96, 100)
FAINT = (122, 118, 110)
RULE = (150, 140, 122)
SEA = (186, 214, 228)
LAND = (206, 188, 142)
LANDLINE = (150, 130, 88)
PIN = (178, 34, 34)
WHITE = (255, 255, 255)


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x0, y0, x1, y1, c):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        row = bytes(c) * (x1 - x0)
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            self.px[base:base + (x1 - x0) * 3] = row

    def hline(self, x0, x1, y, c, thick=1):
        self.rect(x0, y, x1, y + thick, c)

    def vline(self, x, y0, y1, c, thick=1):
        self.rect(x, y0, x + thick, y1, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if fill:
                    if d2 <= r * r:
                        self.set(x, y, c)
                elif r * r - 2 * r <= d2 <= r * r:
                    self.set(x, y, c)

    def fill_poly(self, pts, c):
        """Even-odd scanline fill of a screen-space polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(int(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(max(0, xs[i]), min(self.w, xs[i + 1] + 1)):
                    self.set(x, y, c)

    def poly_outline(self, pts, c):
        n = len(pts)
        for i in range(n):
            self.line(pts[i][0], pts[i][1], pts[(i + 1) % n][0],
                      pts[(i + 1) % n][1], c)

    def png_bytes(self):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * stride:(y + 1) * stride]

        def chunk(tag, data):
            out = struct.pack(">I", len(data)) + tag + data
            out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
                chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
                chunk(b"IEND", b""))


# ------------------------------------------------------------------ fonts
class Font:
    """Bitmap font in BF1 format (see genfont.py, outside the repo).

    magic b"BF1", cell u8, ascent u16, then 95 records for chars 32..126:
    advance u8, ink-top u8, ink-height u8, then ink-height rows of
    ceil(advance/8) bytes, MSB-first. Ink-top is measured from the
    ascender line, so punctuation lands at its true row.
    """

    def __init__(self, size):
        with open(os.path.join(HERE, "f%d.bin" % size), "rb") as fh:
            raw = fh.read()
        if raw[:3] != b"BF1":
            raise ValueError("bad font magic for size %d" % size)
        self.cell = raw[3]
        self.ascent = struct.unpack(">H", raw[4:6])[0]
        self.glyphs = {}
        pos = 6
        for code in range(32, 127):
            adv = raw[pos]
            top = raw[pos + 1]
            height = raw[pos + 2]
            pos += 3
            rowbytes = (adv + 7) // 8
            data = raw[pos:pos + height * rowbytes]
            pos += height * rowbytes
            self.glyphs[chr(code)] = (adv, top, height, rowbytes, data)

    def width(self, text):
        return sum(self.glyphs[ch][0] for ch in text)

    def draw(self, cv, x, y_base, text, color):
        for ch in text:
            adv, top, height, rowbytes, data = self.glyphs[ch]
            for row in range(height):
                bits = data[row * rowbytes:(row + 1) * rowbytes]
                for col in range(adv):
                    if bits[col // 8] & (0x80 >> (col % 8)):
                        cv.set(x + col, y_base - self.ascent + top + row, color)
            x += adv
        return x

    def draw_center(self, cv, cx, y_base, text, color):
        return self.draw(cv, cx - self.width(text) // 2, y_base, text, color)


def wrap(font, text, width):
    lines = []
    cur = ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if font.width(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


F8 = Font(8)
F9 = Font(9)
F11 = Font(11)
F14 = Font(14)
F18 = Font(18)
F26 = Font(26)
F40 = Font(40)


# ------------------------------------------------------------------ stills
STILL_W = 600
STILL_H = 450


def blit_still(cv, name, x0, y0, w, h):
    """Paste a toon still, centre-cropped to the target aspect, scaled with
    nearest neighbour, with a 2px ink frame. Wide targets crop the height
    with a small top bias, so the scene's sign board (near the top of the
    frame) stays in view."""
    with open(os.path.join(HERE, "stills", name + ".rgb"), "rb") as fh:
        raw = fh.read()
    if len(raw) != STILL_W * STILL_H * 3:
        raise ValueError("bad still size: %s" % name)
    target_aspect = w / h
    src_aspect = STILL_W / STILL_H
    if src_aspect > target_aspect:
        crop_w = int(STILL_H * target_aspect)
        sx0 = (STILL_W - crop_w) // 2
        sy0, crop_h = 0, STILL_H
    else:
        crop_h = int(STILL_W / target_aspect)
        sy0 = (STILL_H - crop_h) // 6
        sx0, crop_w = 0, STILL_W
    for dy in range(h):
        sy = sy0 + dy * crop_h // h
        for dx in range(w):
            sx = sx0 + dx * crop_w // w
            i = (sy * STILL_W + sx) * 3
            cv.set(x0 + dx, y0 + dy, tuple(raw[i:i + 3]))
    cv.rect(x0 - 2, y0 - 2, x0 + w + 2, y0, INK)
    cv.rect(x0 - 2, y0 + h, x0 + w + 2, y0 + h + 2, INK)
    cv.rect(x0 - 2, y0, x0, y0 + h, INK)
    cv.rect(x0 + w, y0, x0 + w + 2, y0 + h, INK)


# ------------------------------------------------------------------ maps
# Stylised Europe outlines (lon, lat), drawn by hand for a locator map.
EUROPE = [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
          (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
          (33, 69), (38, 68), (50, 68), (55, 68), (55, 62), (53, 58),
          (51, 53), (44, 51), (40, 52), (36, 50), (32, 47), (30, 45),
          (22, 40), (19, 42), (16, 40), (14, 42), (12, 44), (8, 44),
          (6, 43), (3, 43), (-1, 38), (-6, 36), (-9, 37)]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (-1, 55), (0, 52),
           (1, 51), (-2, 50)]
SCANDINAVIA = [(5, 58), (10, 59), (14, 60), (18, 62), (21, 64),
               (24, 66), (28, 68), (30, 70), (28, 71), (24, 70),
               (20, 68), (16, 66), (12, 63), (8, 61), (5, 60)]
REGIONS = [EUROPE, BRITAIN, SCANDINAVIA]


def draw_map(cv, x0, y0, w, h, lon0, lon1, lat0, lat1, pins):
    """Equirectangular map in the given rect; pins are (lon, lat, label)."""
    cv.rect(x0, y0, x0 + w, y0 + h, SEA)
    cv.rect(x0, y0, x0 + w, y0 + 1, INK)
    cv.rect(x0, y0 + h - 1, x0 + w, y0 + h, INK)
    cv.rect(x0, y0, x0 + 1, y0 + h, INK)
    cv.rect(x0 + w - 1, y0, x0 + w, y0 + h, INK)

    def proj(lon, lat):
        return (x0 + int((lon - lon0) / (lon1 - lon0) * w),
                y0 + int((lat1 - lat) / (lat1 - lat0) * h))

    for poly in REGIONS:
        pts = [proj(lon, lat) for lon, lat in poly]
        cv.fill_poly(pts, LAND)
        cv.poly_outline(pts, LANDLINE)
    for lon, lat, label in pins:
        px, py = proj(lon, lat)
        if label:
            cv.circle(px, py, 7, PIN)
            cv.circle(px, py, 7, INK, fill=False)
            F8.draw_center(cv, px, py + 3, label, WHITE)
        else:
            cv.circle(px, py, 2, PIN)


# ------------------------------------------------------------------ content
# (number, headline, source) -- every headline is ASCII only.
STORIES = [
    (1, "Two tankers hit mines, burn in Hormuz", "REUTERS"),
    (2, "Houthis claim Ras Tanura refinery hit", "REUTERS"),
    (3, "Trump unveils tariffs on 14 partners", "REUTERS"),
    (4, "Russian strikes cut power in five regions", "REUTERS"),
    (5, "Ukraine hits Savasleyka base, 5 jets hurt", "REUTERS"),
    (6, "Israel kills Hamas security chief in Gaza", "REUTERS"),
    (7, "RSF drone strike kills 19 in Blue Nile", "REUTERS"),
    (8, "Colombia frees 20 hostages in Cartagena", "AL JAZEERA"),
    (9, "Australia, Solomons sign security pact", "NYT"),
    (10, "Merz: Russia wants more than Ukraine", "REUTERS"),
    (11, "Knesset backs Oct 7 inquiry, first vote", "REUTERS"),
    (12, "Knesset backs eight-year PM term limit", "REUTERS"),
    (13, "Murmansk governor held in graft probe", "REUTERS"),
    (14, "US economy grows 4.3%, PCE inflation 3.8%", "REUTERS"),
    (15, "Australia inflation jumps to 4.9%", "REUTERS"),
    (16, "Bangladesh garment wage up 36%", "TBS"),
    (17, "North Korea expels Swiss diplomat", "REUTERS"),
    (18, "Poundland collapses, 11,000 jobs at risk", "BBC"),
    (19, "UK energy cap to rise 26% in January", "OFGEM"),
    (20, "Bogor mine toll hits 9, 17 still trapped", "REUTERS"),
    (21, "US Army blows up 5 tons of lead azide", "AP"),
    (22, "Ukraine drones torch two Rosneft refineries", "REUTERS"),
    (23, "Poland plans no-fly zone on eastern border", "REUTERS"),
    (24, "Court voids Phala Phala, Ramaphosa safe", "AL JAZEERA"),
    (25, "Iran offers Hormuz reopening in 48 hours", "REUTERS"),
    (27, "Pope Leo rues failure of COP31 talks", "AP"),
    (28, "EU proposes 50bn-euro tech, quantum fund", "REUTERS"),
    (29, "EU delays Tesla self-driving decision", "REUTERS"),
    (30, "Nor'easter threatens US East Coast", "NWS"),
    (31, "Iraq court backs federal troops at borders", "REUTERS"),
    (32, "Leaked data: 490,334 Russian troops dead", "BBC"),
    (33, "Libyan army vows revenge on Ukraine", "AP"),
    (34, "Tech stocks plunge worldwide on AI doubt", "BBC"),
    (35, "German officials meet on US troop pullout", "POLITICO"),
    (36, "US weekly jobless claims 189,000", "REUTERS"),
    (37, "Saudi jets strike Hodeidah port", "REUTERS"),
    (38, "Iran VP shrugs off US naval blockade", "REUTERS"),
    (40, "UN rights chief warns on Palestinian peril", "UN NEWS"),
    (41, "Australia passes online safety law", "REUTERS"),
    (42, "US shelves business-deal offer to Russia", "REUTERS"),
]

# Toon features: (story no, still file, tile caption, tile sub-line).
FEATURES_A = [
    (1, "hormuz", "HORMUZ BURNS", "Two tankers hit mines - REUTERS"),
    (2, "rastanura", "RAS TANURA HIT", "Houthis claim refinery strike - REUTERS"),
    (3, "tariffs", "TARIFF SALVO", "Trump targets 14 partners - REUTERS"),
    (4, "blackout", "POWER OUT", "Strikes black out five regions - REUTERS"),
]
FEATURES_B = [
    (14, "gdp", "4.3% GROWTH", "US GDP surges, inflation 3.8% - REUTERS"),
    (20, "bogor", "MINE FLOOD", "Bogor toll 9, 17 trapped - REUTERS"),
    (30, "noreaster", "NOR'EASTER", "Storm bears down on East Coast - NWS"),
]

HERO_DECK = (
    "The European Union unveiled a fund of up to 50 billion euro for "
    "AI and quantum computing on Wednesday, in a push to cut dependence "
    "on the US and China.")
# Europe locator pins: (lon, lat, numbered label or "").
EUROPE_PINS = [
    (4.35, 50.85, "28"), (30.5, 50.4, "4"), (50.1, 53.2, "22"),
    (21.0, 52.2, "23"), (-0.1, 51.5, "18"), (33.1, 69.0, "13"),
    (13.4, 52.5, "10"), (37.6, 55.7, "32"),
]


# ------------------------------------------------------------------ layout
def build():
    cv = Canvas(W, H, PAPER)
    if len(STORIES) != 40:
        raise ValueError("need 40 stories, got %d" % len(STORIES))
    if [n for n, _, _ in STORIES] != (
            list(range(1, 26)) + list(range(27, 39)) + [40, 41, 42]):
        raise ValueError("story numbers are not the final 40")
    for n, head, src in STORIES:
        if len(head) > 43:
            raise ValueError("headline too long: %d %r" % (n, head))
        if F9.width("%d. %s" % (n, head)) + F8.width(src) + 8 > 328:
            raise ValueError("list line overflows: %d" % n)

    # Masthead band
    cv.rect(0, 0, W, 72, BLUE)
    F40.draw_center(cv, W // 2, 46, "THE BRUSSELS FILE", WHITE)
    cv.rect(0, 72, W, 74, GOLD)
    F9.draw_center(cv, W // 2, 66,
                   "WEDNESDAY, 25 NOVEMBER 2026  |  40 STORIES  |  EVERY STORY SOURCED",
                   GOLD)

    # Hero headline (two lines, centred)
    hero_lines = wrap(F26, "EU BETS 50 BILLION EURO ON AI AND QUANTUM", 1008)
    if len(hero_lines) > 2:
        raise ValueError("hero headline wraps to %d lines" % len(hero_lines))
    y = 106
    for line in hero_lines:
        F26.draw_center(cv, W // 2, y, line, INK)
        y += 30
    cv.hline(8, 1016, 140, INK, 2)

    # Hero row: still + deck + Europe locator map
    blit_still(cv, "eufund", 8, 148, 460, 180)
    F11.draw(cv, 482, 168, "HERO  |  #28  |  TRADE / POLITICS", RED)
    deck = wrap(F14, HERO_DECK, 288)
    y = 190
    for line in deck:
        F14.draw(cv, 482, y, line, INK)
        y += 17
    if y > 300:
        raise ValueError("hero deck overflows: ends at %d" % y)
    F11.draw(cv, 482, 312, "SOURCE: REUTERS, 25 NOV 2026", GREY)
    F9.draw(cv, 786, 168, "EUROPE - WHERE THE NEWS HAPPENED", INK)
    draw_map(cv, 786, 176, 230, 128, -10, 55, 36, 70, EUROPE_PINS)
    F8.draw(cv, 786, 318, "NUMBERED PINS = PICTURED STORIES", BLUE)
    cv.hline(8, 1016, 336, INK, 2)

    # Picture rows
    F18.draw(cv, 8, 360, "THE DAY IN PICTURES", INK)
    cv.hline(8, 1016, 366, INK, 1)
    x = 8
    for num, still, cap, sub in FEATURES_A:
        blit_still(cv, still, x, 372, 244, 132)
        F11.draw(cv, x, 518, "%d. %s" % (num, cap), INK)
        F8.draw(cv, x, 530, sub, GREY)
        x += 254
    x = 8
    for num, still, cap, sub in FEATURES_B:
        blit_still(cv, still, x, 540, 328, 140)
        F11.draw(cv, x, 694, "%d. %s" % (num, cap), INK)
        F8.draw(cv, x, 706, sub, GREY)
        x += 340

    # 40-story list, three columns
    F14.draw(cv, 8, 730, "ALL 40 STORIES - THE REST OF THE DAY", INK)
    F9.draw(cv, 1016 - F9.width("WEDNESDAY 25 NOVEMBER 2026"), 730,
            "WEDNESDAY 25 NOVEMBER 2026", BLUE)
    cv.hline(8, 1016, 736, INK, 1)
    cols = [STORIES[0:14], STORIES[14:27], STORIES[27:40]]
    col_x = [8, 348, 688]
    for ci, col in enumerate(cols):
        y = 750
        for n, head, src in col:
            F9.draw(cv, col_x[ci], y, "%d. %s" % (n, head), INK)
            F8.draw(cv, col_x[ci] + 328 - F8.width(src), y, src, GREY)
            y += 13
        if y > 940:
            raise ValueError("list column %d overflows: ends at %d" % (ci, y))

    # Footer
    cv.hline(8, 1016, 946, INK, 1)
    F9.draw_center(cv, W // 2, 962,
                   "SOURCES: REUTERS, AP, BBC, AL JAZEERA, NYT, NWS, OFGEM, POLITICO, UN NEWS",
                   GREY)
    F8.draw_center(cv, W // 2, 978,
                   "ALL 40 STORIES ARE EVENTS OF WEDNESDAY 25 NOVEMBER 2026, VERIFIED AGAINST THEIR SOURCES.",
                   FAINT)
    F8.draw_center(cv, W // 2, 992,
                   "THE BRUSSELS FILE - ONE DAY, ONE PICTURE.",
                   FAINT)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if outdir:
        outpath = os.path.join(outdir, "entry.png")
    else:
        outpath = os.path.join(HERE, "..", "output", "entry.png")
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    cv = build()
    data = cv.png_bytes()
    with open(outpath, "wb") as fh:
        fh.write(data)
    print("wrote %s %d bytes sha256=%s" % (
        outpath, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
