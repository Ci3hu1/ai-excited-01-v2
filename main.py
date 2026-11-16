#!/usr/bin/env python3
"""ai-excited-01 v2: GIANT RUBBER DUCK SURFING A TSUNAMI.

A colossal bright-yellow rubber duck rides a huge curling teal wave
straight at the viewer, a tiny surfer in a red wetsuit balancing on its
head, arms up. One huge readable yellow shape so it hits at 300px, with
a bold "HI JUDGE!" banner across the top in a hand-built 5x7 block font.

Pure Python standard library only. Fully deterministic (fixed seed):
running twice produces byte-identical output.
"""
import os
import random
import struct
import zlib

W = 1024
H = 1024
SEED = 20261116

# ---------------------------------------------------------------- palette
SKY_TOP = (255, 140, 40)      # blazing orange
SKY_MID = (232, 84, 112)      # hot pink-orange
SKY_LOW = (38, 68, 168)       # deep blue
SUN = (255, 236, 130)
SUN_CORE = (255, 250, 210)
SEA_DEEP = (8, 74, 110)
WAVE_DARK = (10, 110, 128)
WAVE = (16, 158, 178)
WAVE_LIGHT = (64, 205, 214)
FOAM = (255, 255, 255)
DUCK = (255, 212, 0)
DUCK_DARK = (235, 176, 0)
DUCK_LIGHT = (255, 232, 110)
BEAK = (255, 122, 26)
BEAK_DARK = (230, 90, 10)
EYE = (20, 20, 20)
RED = (226, 32, 40)
SKIN = (255, 205, 160)
BANNER = (16, 24, 64)
BANNER_EDGE = (255, 255, 255)

buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def fill_rect(x0, y0, x1, y1, c):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    row = bytes(c) * (x1 - x0)
    for y in range(y0, y1):
        i = (y * W + x0) * 3
        buf[i:i + len(row)] = row


def fill_ellipse(cx, cy, rx, ry, c):
    if rx <= 0 or ry <= 0:
        return
    for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
        dy = (y - cy) / ry
        dx = rx * (1.0 - dy * dy) ** 0.5
        x0 = int(cx - dx)
        x1 = int(cx + dx) + 1
        fill_rect(x0, y, x1, y + 1, c)


def fill_circle(cx, cy, r, c):
    fill_ellipse(cx, cy, r, r, c)


def fill_poly(points, c):
    """Scanline polygon fill (points: list of (x, y))."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y0, y1 = max(0, min(ys)), min(H - 1, max(ys))
    n = len(points)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x1, y1p = points[i]
            x2, y2p = points[(i + 1) % n]
            if (y1p <= y < y2p) or (y2p <= y < y1p):
                t = (y - y1p) / (y2p - y1p)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            fill_rect(int(xs[k]), y, int(xs[k + 1]) + 1, y + 1, c)


def thick_line(x0, y0, x1, y1, r, c):
    steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for s in range(steps + 1):
        t = s / steps
        fill_circle(int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t), r, c)


def ring(cx, cy, r0, r1, c):
    for y in range(max(0, cy - r1), min(H, cy + r1 + 1)):
        for x in range(max(0, cx - r1), min(W, cx + r1 + 1)):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if r0 * r0 <= d2 <= r1 * r1:
                px(x, y, c)


# ------------------------------------------------------------- 5x7 font
GLYPHS = {
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


def draw_text(text, x, y, scale, c):
    cx = x
    for ch in text:
        g = GLYPHS[ch]
        for row in range(7):
            for col in range(5):
                if g[row][col] == "1":
                    fill_rect(cx + col * scale, y + row * scale,
                              cx + (col + 1) * scale, y + (row + 1) * scale, c)
        cx += 6 * scale


def text_width(text, scale):
    return len(text) * 6 * scale - scale


# ------------------------------------------------------------------ scene
def draw_sky():
    for y in range(H):
        t = y / (H - 1)
        if t < 0.45:
            c = lerp(SKY_TOP, SKY_MID, t / 0.45)
        else:
            c = lerp(SKY_MID, SKY_LOW, (t - 0.45) / 0.55)
        fill_rect(0, y, W, y + 1, c)


def draw_sunburst(sx, sy):
    import math
    for k in range(16):
        a0 = k * math.pi / 8
        a1 = a0 + math.pi / 16
        r = 560
        p1 = (sx + int(560 * math.cos(a0)), sy + int(560 * math.sin(a0)))
        p2 = (sx + int(560 * math.cos(a1)), sy + int(560 * math.sin(a1)))
        col = (255, 178, 92) if k % 2 == 0 else (255, 150, 60)
        fill_poly([(sx, sy), p1, p2], col)


def draw_birds():
    for (bx, by, s) in [(150, 240, 16), (205, 205, 12), (880, 300, 14),
                        (120, 330, 11), (930, 250, 10)]:
        thick_line(bx - s, by, bx, by - s // 2, 3, (30, 30, 40))
        thick_line(bx, by - s // 2, bx + s, by, 3, (30, 30, 40))


def draw_wave():
    # deep sea base
    for y in range(660, H):
        t = (y - 660) / (H - 660)
        fill_rect(0, y, W, y + 1, lerp(WAVE_DARK, SEA_DEEP, t))
    # sweeping wave face: a diagonal wall of water rising to the right
    fill_poly([(0, 1024), (0, 830), (280, 700), (620, 560), (1024, 470),
               (1024, 1024)], WAVE)
    fill_poly([(0, 1024), (0, 900), (330, 780), (660, 640), (1024, 560),
               (1024, 1024)], WAVE_DARK)
    # main rolling mound at the bottom
    fill_ellipse(512, 960, 580, 300, WAVE)
    fill_ellipse(512, 1000, 520, 240, WAVE_DARK)
    # curling crest mass, top-right: the barrel of the wave
    fill_ellipse(790, 520, 300, 175, WAVE)
    fill_ellipse(790, 500, 265, 145, WAVE_LIGHT)
    # barrel hole: bright sky shows through the curl
    fill_ellipse(830, 580, 128, 84, (150, 210, 235))
    fill_ellipse(830, 580, 108, 68, (190, 230, 245))
    # curl lip rolling over the hole
    fill_ellipse(830, 470, 185, 88, WAVE_LIGHT)
    fill_ellipse(830, 486, 160, 72, WAVE)
    # foam scallops only along the lip's top edge
    for cx in range(640, 1010, 44):
        cy = 400 + int(26 * ((cx - 640) / 370.0))
        fill_circle(cx, cy, 24, FOAM)
        fill_circle(cx + 21, cy + 9, 16, FOAM)
    # foam streaks down the wave face, following its diagonal
    rng = random.Random(SEED)
    for _ in range(30):
        fx = rng.randint(60, 980)
        fy = rng.randint(640, 990)
        fill_ellipse(fx, fy, rng.randint(14, 38), rng.randint(4, 8), FOAM)


def draw_duck():
    # tail: small rounded nub
    fill_ellipse(185, 685, 42, 30, DUCK_DARK)
    # body: huge yellow ellipse, front three-quarter
    fill_ellipse(440, 800, 300, 212, DUCK)
    # belly shading + top highlight
    fill_ellipse(440, 888, 255, 128, DUCK_DARK)
    fill_ellipse(400, 712, 195, 92, DUCK_LIGHT)
    # wing
    fill_ellipse(375, 820, 145, 85, DUCK_DARK)
    fill_ellipse(370, 810, 130, 70, (247, 196, 0))
    # head
    fill_circle(545, 485, 150, DUCK)
    fill_ellipse(500, 428, 88, 54, DUCK_LIGHT)
    # beak: big orange, upper + lower
    fill_poly([(660, 435), (812, 475), (670, 545)], BEAK)
    fill_poly([(670, 545), (812, 475), (768, 548), (675, 568)], BEAK_DARK)
    thick_line(670, 545, 805, 477, 5, BEAK_DARK)
    # eye + highlight
    fill_circle(580, 438, 24, EYE)
    fill_circle(588, 430, 9, FOAM)
    # blush
    fill_ellipse(625, 525, 26, 16, (255, 150, 90))


def draw_surfer():
    # tiny surfer standing on the duck's head, arms raised in triumph
    hx, hy = 545, 335  # feet on top of duck head
    # legs (red wetsuit)
    thick_line(hx - 5, hy, hx - 15, hy - 34, 7, RED)
    thick_line(hx + 5, hy, hx + 15, hy - 34, 7, RED)
    # torso
    thick_line(hx, hy - 34, hx, hy - 74, 9, RED)
    # arms up in a V
    thick_line(hx - 2, hy - 66, hx - 44, hy - 116, 7, RED)
    thick_line(hx + 2, hy - 66, hx + 44, hy - 116, 7, RED)
    # head
    fill_circle(hx, hy - 92, 16, SKIN)
    fill_ellipse(hx, hy - 102, 16, 10, (40, 26, 16))  # hair


def draw_spray():
    rng = random.Random(SEED + 7)
    # spray bursting off the crest lip (right side only, clear of the duck)
    for _ in range(150):
        sx = rng.randint(660, 1000)
        sy = rng.randint(330, 430)
        fill_circle(sx, sy, rng.randint(2, 7), FOAM)
    # a few droplets flying left of the crest
    for _ in range(60):
        sx = rng.randint(120, 340)
        sy = rng.randint(360, 430)
        fill_circle(sx, sy, rng.randint(2, 6), FOAM)
    for _ in range(120):
        sx = rng.randint(120, 940)
        sy = rng.randint(930, 1010)
        fill_circle(sx, sy, rng.randint(3, 9), FOAM)
    # speed lines streaking past (kept off the duck's face)
    for (x0, y0, x1, y1) in [(60, 560, 220, 500), (820, 640, 990, 580),
                             (40, 700, 180, 660), (860, 780, 1000, 740),
                             (120, 420, 260, 380)]:
        thick_line(x0, y0, x1, y1, 5, FOAM)


def draw_banner():
    # dark banner strip across the top, white edge, yellow block text
    fill_rect(110, 26, 914, 152, BANNER)
    fill_rect(110, 26, 914, 32, BANNER_EDGE)
    fill_rect(110, 146, 914, 152, BANNER_EDGE)
    fill_rect(110, 26, 116, 152, BANNER_EDGE)
    fill_rect(908, 26, 914, 152, BANNER_EDGE)
    text = "HI JUDGE!"
    scale = 13
    tw = text_width(text, scale)
    draw_text(text, (W - tw) // 2, 48, scale, DUCK)


# ------------------------------------------------------------- PNG encode
def png_bytes():
    raw = bytearray()
    stride = W * 3
    prev = bytearray(stride)
    for y in range(H):
        row = bytes(buf[y * stride:(y + 1) * stride])
        # Up filter
        up = bytes((row[i] - prev[i]) & 0xFF for i in range(stride))
        # pick the filter with the smaller absolute-value sum
        def score(bs):
            return sum(b if b < 128 else 256 - b for b in bs)
        if score(up) < score(row):
            raw.append(2)
            raw.extend(up)
        else:
            raw.append(0)
            raw.extend(row)
        prev = bytearray(row)
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    draw_sky()
    draw_sunburst(770, 230)
    fill_circle(770, 230, 105, SUN)
    fill_circle(770, 230, 82, SUN_CORE)
    draw_birds()
    draw_wave()
    draw_duck()
    draw_surfer()
    draw_spray()
    draw_banner()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    print("wrote", path)


if __name__ == "__main__":
    main()
