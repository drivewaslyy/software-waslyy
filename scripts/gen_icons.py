"""Generate square PWA/favicon icons."""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ACCENT = (79, 70, 229)
NEON = (6, 214, 160)
TEXT = (240, 240, 250)

candidate_fonts = [
    "/System/Library/Fonts/Supplemental/Futura.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
]
def font(size):
    for f in candidate_fonts:
        if os.path.exists(f):
            try: return ImageFont.truetype(f, size)
            except Exception: continue
    return ImageFont.load_default()

def make_icon(size, out_path):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = max(2, size // 16)
    radius = size // 5
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=ACCENT)
    f = font(int(size * 0.55))
    tw = draw.textlength("W", font=f)
    draw.text(((size - tw) / 2, size * 0.18), "W", font=f, fill=TEXT)
    dot_r = max(4, size // 18)
    cx, cy = size - pad - dot_r * 2, size - pad - dot_r * 2
    draw.ellipse((cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r), fill=NEON)
    img.save(out_path, "PNG", optimize=True)
    print(f"  {out_path.relative_to(ROOT)}  ({out_path.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    make_icon(192, ROOT / "icon-192.png")
    make_icon(512, ROOT / "icon-512.png")
    make_icon(180, ROOT / "apple-touch-icon.png")
    make_icon(32, ROOT / "favicon-32.png")
    print("Done.")
