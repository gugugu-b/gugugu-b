"""Build contribution and profiler animations with Pillow.

python3 scripts/build_activity.py --fetch  # needs GITHUB_TOKEN
python3 scripts/build_activity.py          # use the saved calendar
"""
import argparse
from datetime import date
import json
import math
import os
from pathlib import Path
import urllib.request
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
DATA = ROOT / "data" / "contributions.json"
BG, PANEL, BORDER = "#0B1220", "#101D2E", "#23364D"
TEXT, MUTED, TEAL, BLUE = "#F1F5F9", "#94A3B8", "#2DD4BF", "#38BDF8"


def font(size, mono=False):
    paths = (["/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
             if mono else ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"])
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def save(frames, name):
    palette = frames[len(frames)//2].quantize(colors=96)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(OUT / f"{name}.gif", save_all=True, append_images=indexed[1:],
                    duration=100, loop=0, disposal=1, optimize=True)
    frames[len(frames)//2].save(OUT / f"{name}.png")
    print(name, (OUT / f"{name}.gif").stat().st_size, "bytes")


def fetch():
    query = 'query { user(login: "gugugu-b") { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } } } }'
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
                 "Content-Type": "application/json", "User-Agent": "gugugu-b-profile"})
    with urllib.request.urlopen(req, timeout=45) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError("GitHub contribution query failed")
    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(calendar, ensure_ascii=False, indent=2) + "\n")


def activity(calendar):
    weeks = calendar["weeks"]
    colors = ["#1C2B3D", "#155E63", "#0D9488", "#2DD4BF", "#A7F3D0"]
    peak = max(day["contributionCount"] for week in weeks for day in week["contributionDays"])
    start = weeks[0]["contributionDays"][0]["date"]
    end = weeks[-1]["contributionDays"][-1]["date"]
    frames = []
    for i in range(64):
        im = Image.new("RGB", (1200, 350), BG)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((1, 1, 1198, 348), radius=18, outline=BORDER)
        d.text((42, 27), "BUILD IN PUBLIC", font=font(28), fill=TEXT)
        d.text((42, 68), f"GUGUGU-B  /  {calendar['totalContributions']} CONTRIBUTIONS  /  {start} — {end}", font=font(13, True), fill=MUTED)
        scan = (i / 64) * len(weeks)
        previous_month = None
        for col, week in enumerate(weeks):
            first = date.fromisoformat(week["contributionDays"][0]["date"])
            if first.month != previous_month:
                d.text((42+col*21, 98), first.strftime("%b"), font=font(11, True), fill=MUTED)
                previous_month = first.month
            for day in week["contributionDays"]:
                row = (date.fromisoformat(day["date"]).weekday()+1) % 7
                count = day["contributionCount"]
                level = 0 if count == 0 else min(4, max(1, math.ceil(count/max(1, peak)*4)))
                x, y = 42+col*21, 123+row*21
                d.rounded_rectangle((x, y, x+16, y+16), radius=3, fill=colors[level])
                if abs(col-scan) < 0.65:
                    d.rounded_rectangle((x-1, y-1, x+17, y+17), radius=4, outline=BLUE)
        d.line((42, 291, 1156, 291), fill=BORDER, width=2)
        x = 42 + (i/64)*1114
        d.line((max(42, x-85), 291, x, 291), fill=TEAL, width=3)
        d.ellipse((x-4, 287, x+4, 295), fill=TEXT)
        d.text((42, 310), "REAL GITHUB ACTIVITY · API SNAPSHOT", font=font(12, True), fill=TEAL)
        d.text((927, 310), "LESS", font=font(11, True), fill=MUTED)
        for j, color in enumerate(colors):
            d.rounded_rectangle((969+j*23, 308, 985+j*23, 324), radius=3, fill=color)
        d.text((1092, 310), "MORE", font=font(11, True), fill=MUTED)
        frames.append(im)
    save(frames, "contribution-heatmap")


def hotspots():
    # BW1100/Qwen3.5-9B baseline trace: cumulative GPU kernel time,
    # 15 decode steps. These are fixed measured proportions, not an E2E chart.
    items = [("GEMM", 41.6, "#38BDF8"), ("GDN", 15.6, "#2DD4BF"),
             ("NONZERO", 12.4, "#FBBF24"), ("ATTENTION", 9.9, "#818CF8"),
             ("INDEXING", 6.6, "#FB7185"), ("CAUSAL CONV", 4.0, "#A78BFA"),
             ("OTHER", 9.9, "#64748B")]
    frames = []
    for i in range(64):
        im = Image.new("RGB", (1200, 420), BG)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((1, 1, 1198, 418), radius=18, outline=BORDER)
        d.text((42, 25), "FOLLOW THE HOTSPOTS", font=font(28), fill=TEXT)
        d.text((42, 67), "BW1100 / QWEN3.5-9B / BASELINE DECODE TRACE", font=font(13, True), fill=MUTED)
        for row, (label, share, color) in enumerate(items):
            y = 108+row*35
            d.text((42, y+2), label, font=font(13, True), fill=MUTED)
            d.rounded_rectangle((203, y, 753, y+20), radius=5, fill=PANEL)
            d.rounded_rectangle((203, y, 203+share/50*550, y+20), radius=5, fill=color)
            d.text((775, y+2), f"{share:4.1f}%", font=font(13, True), fill=TEXT)
        # The moving scan highlights fixed bars; values never change.
        y = 106 + (i/64)*245
        d.line((197, y, 845, y), fill="#E2E8F0", width=1)
        d.rounded_rectangle((873, 104, 1156, 344), radius=12, fill=PANEL, outline=BORDER)
        for step, label in enumerate(["01  PROFILE", "02  LOCATE", "03  FUSE", "04  VERIFY"]):
            active = (i//16) == step
            sy = 125+step*51
            d.ellipse((892, sy+5, 902, sy+15), fill=TEAL if active else BORDER)
            d.text((919, sy), label, font=font(17, True), fill=TEXT if active else MUTED)
        d.text((42, 370), "SHARE OF CUMULATIVE GPU KERNEL TIME · 15 DECODE STEPS · NOT REQUEST LATENCY", font=font(12, True), fill=MUTED)
        frames.append(im)
    save(frames, "operator-hotspots")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    if args.fetch:
        fetch()
    activity(json.loads(DATA.read_text()))
    hotspots()
