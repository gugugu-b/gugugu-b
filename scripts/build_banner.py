"""Generate the profile banner: python3 scripts/build_banner.py.

Requires Pillow. The diagram is decorative, not measured benchmark data.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)
W, H, N = 1200, 380, 80
BG, PANEL, LINE = "#0B1220", "#101D2E", "#23364D"
TEXT, MUTED, TEAL, BLUE, GOLD = "#F1F5F9", "#94A3B8", "#2DD4BF", "#38BDF8", "#FBBF24"


def font(size, mono=False):
    candidates = (
        ["/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
        if mono else
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


TITLE, SMALL, MONO, TINY = font(60), font(14), font(17, True), font(12, True)
nodes = [(858, 142), (1020, 142), (1048, 260), (830, 260)]
edges = list(zip(nodes, nodes[1:] + nodes[:1]))
frames = []
for i in range(N):
    phase = i / N
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for x in range(0, W, 40):
        d.line((x, 0, x, H), fill="#111E2F")
    for y in range(0, H, 40):
        d.line((0, y, W, y), fill="#111E2F")
    d.rectangle((0, 0, W, 3), fill=TEAL)
    d.text((48, 34), "PIONITES / GUGUGU-B", font=SMALL, fill=TEAL)
    d.text((44, 62), "AI Infrastructure", font=TITLE, fill=TEXT)
    d.text((48, 141), "BW150  /  BW1100  /  K100-AI   ·   MODEL OPTIMIZATION", font=SMALL, fill=MUTED)
    d.rounded_rectangle((48, 190, 689, 300), radius=12, fill=PANEL, outline=LINE)
    for j, color in enumerate(["#FB7185", GOLD, TEAL]):
        d.ellipse((65+j*18, 204, 73+j*18, 212), fill=color)
    d.text((137, 202), "performance-lab", font=TINY, fill=MUTED)
    command = "$ profile > fuse > benchmark > verify"
    count = min(len(command), int(phase * 80))
    d.text((66, 230), command[:count], font=MONO, fill=TEXT)
    if i % 12 < 7:
        cursor = d.textlength(command[:count], font=MONO)
        d.rectangle((66+cursor+3, 232, 74+cursor+3, 250), fill=TEAL)
    d.text((66, 266), "observe  >  benchmark  >  tune  >  repeat", font=TINY, fill=TEAL)
    d.text((48, 335), "BUILD SYSTEMS.  UNDERSTAND BOTTLENECKS.", font=SMALL, fill=MUTED)
    d.rounded_rectangle((745, 38, 1151, 337), radius=18, fill=PANEL, outline=LINE)
    d.text((771, 58), "KERNEL TO MODEL PIPELINE", font=SMALL, fill=MUTED)
    for a, b in edges:
        d.line((*a, *b), fill="#2A4B64", width=2)
    for k, (a, b) in enumerate(edges):
        t = (phase*2 + k/4) % 1
        x, y = a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t
        for r, color in [(8, "#164A52"), (4, TEAL), (2, TEXT)]:
            d.ellipse((x-r, y-r, x+r, y+r), fill=color)
    for k, (x, y) in enumerate(nodes):
        d.rounded_rectangle((x-44, y-27, x+44, y+27), radius=9, fill=BG, outline=TEAL, width=2)
        label = ["HIP", "TRITON", "LLM", "TTS"][k]
        width = d.textlength(label, font=MONO)
        d.text((x-width/2, y-10), label, font=MONO, fill=TEXT)
    d.text((893, 189), "HYGON DCU", font=TINY, fill=BLUE)
    d.text((771, 310), "PROFILE / FUSE / VERIFY", font=TINY, fill=MUTED)
    frames.append(im)

# A shared palette prevents colors shifting between frames.
palette = frames[40].quantize(colors=96, method=Image.Quantize.MEDIANCUT)
indexed = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
indexed[0].save(OUT / "cluster-banner.gif", save_all=True, append_images=indexed[1:],
                duration=80, loop=0, optimize=True, disposal=1)
frames[40].save(OUT / "cluster-banner.png")
print(f"Created banner: {N} frames, {N*80/1000:.1f}s loop")
