"""Generates the Clean Code marketplace banner (media/banner.png).

Run:  python make_banner.py
"""
import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 420
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

VIOLET = (124, 92, 255)
CYAN = (34, 211, 238)
BG_TOP = (11, 13, 18)
BG_BOT = (18, 21, 29)
WHITE = (233, 236, 242)
MUTE = (150, 160, 176)


def font(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_banner() -> Image.Image:
    img = Image.new("RGB", (W, H), BG_TOP)
    d = ImageDraw.Draw(img, "RGBA")

    # Vertical background gradient.
    for y in range(H):
        d.line([(0, y), (W, y)], fill=lerp(BG_TOP, BG_BOT, y / H))

    # Soft violet glow, top-left.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(320, 0, -4):
        a = int(38 * (r / 320))
        gd.ellipse([180 - r, 40 - r, 180 + r, 40 + r], fill=(124, 92, 255, max(0, 38 - a)))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # Faint code lines on the right as texture.
    mono = font("DejaVuSansMono.ttf", 15)
    code = ["def clean(code):", "    return refactor(code)", "// AI-assisted", "class Engineer:", "    ships = True"]
    for i, line in enumerate(code):
        d.text((900, 70 + i * 34), line, font=mono, fill=(255, 255, 255, 16))

    # Hexagon logo (left).
    cx, cy, R = 150, H // 2, 92
    pts = [(cx + R * math.cos(math.radians(60 * i - 90)), cy + R * math.sin(math.radians(60 * i - 90))) for i in range(6)]
    d.polygon(pts, fill=(124, 92, 255, 28))
    n = len(pts)
    minx = min(p[0] for p in pts)
    maxx = max(p[0] for p in pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        for s in range(30):
            t0, t1 = s / 30, (s + 1) / 30
            gx = ((x1 + (x2 - x1) * t0) - minx) / (maxx - minx)
            d.line([x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0, x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1],
                   fill=(*lerp(VIOLET, CYAN, max(0, min(1, gx))), 255), width=6)
    lw = 7
    d.line([cx - 34, cy - 6, cx - 58, cy, cx - 34, cy + 6 + 26], fill=(*VIOLET, 255), width=lw, joint="curve")
    d.line([cx + 34, cy - 6, cx + 58, cy, cx + 34, cy + 6 + 26], fill=(*CYAN, 255), width=lw, joint="curve")
    d.line([cx + 16, cy - 40, cx - 16, cy + 44], fill=(*lerp(VIOLET, CYAN, 0.5), 255), width=lw)

    # Title + subtitle.
    title = font("DejaVuSans-Bold.ttf", 96)
    sub = font("DejaVuSans.ttf", 30)
    tx = 300
    d.text((tx, 118), "Clean", font=title, fill=WHITE)
    cw = d.textlength("Clean ", font=title)
    d.text((tx + cw, 118), "Code", font=title, fill=CYAN)
    d.text((tx + 4, 228), "Assistente de IA para programar no VS Code", font=sub, fill=MUTE)

    # Feature chips.
    chip_font = font("DejaVuSans-Bold.ttf", 20)
    chips = ["Chat", "Autocomplete", "Terminal", "11+ comandos", "Multi-LLM"]
    x = tx + 4
    y = 292
    for c in chips:
        w = d.textlength(c, font=chip_font)
        d.rounded_rectangle([x, y, x + w + 34, y + 44], radius=22, outline=(*lerp(VIOLET, CYAN, 0.5), 255), width=2)
        d.text((x + 17, y + 10), c, font=chip_font, fill=WHITE)
        x += w + 34 + 16

    return img


if __name__ == "__main__":
    draw_banner().save("banner.png")
    print("Wrote banner.png")
