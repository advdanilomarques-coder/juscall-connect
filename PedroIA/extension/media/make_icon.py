"""Generates the PedroIA extension icon (PNG) — hexagon + neural 'AI' mark
with a violet→cyan gradient on a dark rounded background.

Run:  python make_icon.py
Produces: icon.png (128x128) and icon@256.png (256x256).
"""
import math

from PIL import Image, ImageDraw


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_icon(size: int) -> Image.Image:
    S = size * 4  # supersample for smooth edges
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Rounded dark background.
    bg = (13, 16, 24)
    radius = int(S * 0.22)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius, fill=bg)

    violet = (124, 92, 255)
    cyan = (34, 211, 238)

    cx, cy = S / 2, S / 2
    R = S * 0.30  # hexagon radius

    # Hexagon vertices (flat-top).
    pts = []
    for i in range(6):
        ang = math.radians(60 * i - 90)
        pts.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))

    # Faint gradient fill inside hexagon (horizontal bands).
    minx, maxx = min(p[0] for p in pts), max(p[0] for p in pts)
    hexmask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(hexmask).polygon(pts, fill=255)
    grad = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for x in range(int(minx), int(maxx) + 1):
        t = (x - minx) / max(1, (maxx - minx))
        c = lerp(violet, cyan, t)
        gd.line([(x, 0), (x, S)], fill=(*c, 40))
    img.paste(grad, (0, 0), Image.composite(grad.split()[3], Image.new("L", (S, S), 0), hexmask))

    # Hexagon border with gradient (draw many short segments).
    lw = max(2, int(S * 0.018))
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        steps = 40
        for s in range(steps):
            t0 = s / steps
            t1 = (s + 1) / steps
            gx = ((x1 + (x2 - x1) * t0) - minx) / max(1, (maxx - minx))
            c = lerp(violet, cyan, min(1, max(0, gx)))
            d.line(
                [x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0, x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1],
                fill=(*c, 255),
                width=lw,
            )

    # Neural 'AI' mark: < / > brackets + a central slash, styled like code.
    def gline(p1, p2, color, w):
        d.line([p1[0], p1[1], p2[0], p2[1]], fill=(*color, 255), width=w)

    w = max(3, int(S * 0.022))
    off = S * 0.13
    midy = cy
    # left bracket  <
    gline((cx - off, midy - S * 0.02), (cx - off - S * 0.09, midy), violet, w)
    gline((cx - off - S * 0.09, midy), (cx - off, midy + S * 0.02 + S * 0.11), violet, w)
    # right bracket  >
    gline((cx + off, midy - S * 0.02), (cx + off + S * 0.09, midy), cyan, w)
    gline((cx + off + S * 0.09, midy), (cx + off, midy + S * 0.02 + S * 0.11), cyan, w)
    # central slash (the 'I' / spark)
    gline((cx + S * 0.05, cy - S * 0.14), (cx - S * 0.05, cy + S * 0.16), lerp(violet, cyan, 0.5), w)

    # Downsample.
    return img.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    draw_icon(128).save("icon.png")
    draw_icon(256).save("icon@256.png")
    print("Wrote icon.png (128) and icon@256.png (256)")
