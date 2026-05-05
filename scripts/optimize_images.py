"""One-shot: compress project screenshots to WebP and generate og.png.

Run:  python3 scripts/optimize_images.py
"""
import os, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT / "projects"
PROJECTS_JSON = ROOT / "projects.json"
OG_OUT = ROOT / "og.png"

# ---------- 1. PNG → WebP for project screenshots ----------
def to_webp(quality=82):
    converted = []
    for png in sorted(PROJECTS_DIR.glob("*.png")):
        webp = png.with_suffix(".webp")
        with Image.open(png) as im:
            im = im.convert("RGB")
            im.save(webp, "WEBP", quality=quality, method=6)
        old_kb = png.stat().st_size // 1024
        new_kb = webp.stat().st_size // 1024
        pct = round(100 * (1 - new_kb / max(old_kb, 1)))
        print(f"  {png.name:36s}  {old_kb:>5d} KB  →  {webp.name:36s}  {new_kb:>5d} KB  (-{pct}%)")
        converted.append((png, webp))
    return converted

def update_json(converted):
    data = json.loads(PROJECTS_JSON.read_text())
    for entry in data:
        if entry["image"].endswith(".png"):
            entry["image"] = entry["image"][:-4] + ".webp"
    PROJECTS_JSON.write_text(json.dumps(data, indent=2) + "\n")
    print(f"  updated {PROJECTS_JSON.name}")

def remove_originals(converted):
    for png, _ in converted:
        png.unlink()
    print(f"  removed {len(converted)} original PNGs")

# ---------- 2. Generate og.png ----------
def generate_og():
    W, H = 1200, 630
    BG = (8, 8, 15)            # --bg-0 dark
    ACCENT = (79, 70, 229)     # --accent
    NEON = (6, 214, 160)       # --neon
    TEXT = (240, 240, 250)     # --text-0 dark
    MUTED = (160, 160, 200)

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle radial-ish glow using gradient circles
    glow = Image.new("RGB", (W, H), BG)
    glow_draw = ImageDraw.Draw(glow)
    for r, alpha in [(420, 30), (340, 45), (260, 60), (180, 80)]:
        glow_draw.ellipse((W - r, -r//2, W + r, r + r//2),
                          fill=tuple(min(255, c + alpha) for c in ACCENT))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.blend(img, glow, 0.55)
    draw = ImageDraw.Draw(img)

    # Try to find a system font
    candidate_fonts = [
        "/System/Library/Fonts/Supplemental/Futura.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    def font(size):
        for f in candidate_fonts:
            if os.path.exists(f):
                try: return ImageFont.truetype(f, size)
                except Exception: continue
        return ImageFont.load_default()

    f_brand = font(120)
    f_tag = font(44)
    f_sub = font(28)
    f_url = font(26)

    # Brand wordmark: "waslyy."
    pad = 80
    y = 180
    brand = "waslyy"
    draw.text((pad, y), brand, font=f_brand, fill=TEXT)
    bx = draw.textlength(brand, font=f_brand)
    draw.text((pad + bx, y), ".", font=f_brand, fill=ACCENT)

    # Neon dot accent
    draw.ellipse((pad + bx + 70, y + 35, pad + bx + 110, y + 75), fill=NEON)

    # Tagline
    draw.text((pad, y + 170), "Software, AI Agents & Web Development", font=f_tag, fill=TEXT)
    draw.text((pad, y + 230), "Custom software shipped — remote-first, worldwide.", font=f_sub, fill=MUTED)

    # Bottom URL bar
    draw.line((pad, H - 90, W - pad, H - 90), fill=(40, 40, 70), width=2)
    draw.text((pad, H - 70), "waslyysolutions.com", font=f_url, fill=ACCENT)
    draw.text((W - pad - 360, H - 70), "contact@waslyysolutions.com", font=f_url, fill=MUTED)

    img.save(OG_OUT, "PNG", optimize=True)
    print(f"  wrote {OG_OUT.relative_to(ROOT)}  ({OG_OUT.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    print("[1/3] Converting project PNGs → WebP")
    converted = to_webp()
    print("\n[2/3] Updating projects.json")
    update_json(converted)
    print("\n[3/3] Generating og.png")
    generate_og()
    print("\n[4] Removing original PNGs")
    remove_originals(converted)
    print("\nDone.")
