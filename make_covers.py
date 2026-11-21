"""Rebuild collection folder covers from whatever is currently #1 in each folder.

Usage: python3 make_covers.py [--dry-run]
Reads covers.json, writes covers/<file>, records picks in covers/state.json.
Each folder gets the highest-ranked title (walking its sources in order) that has
backdrop art and isn't already used by another folder this run.
"""
import io, json, sys, urllib.parse, urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "fonts"
OUT = ROOT / "covers"
W, H = 1920, 1080
UA = {"User-Agent": "aiostreams-art/1.0"}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def get_image(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


GENRE_ALIASES = {"Sci-Fi & Fantasy": {"Sci-Fi & Fantasy", "Science Fiction"}}


def primary_ok(src, meta):
    """With "primary": true, only accept titles whose first-listed genre is the folder's genre,
    so e.g. Godzilla Minus One (Science Fiction, Horror, Action) can't be the Horror cover."""
    if not (src.get("primary") and src.get("genre")):
        return True
    genres = meta.get("genres") or []
    return bool(genres) and genres[0] in GENRE_ALIASES.get(src["genre"], {src["genre"]})


def candidates(addon, src, limit=25):
    path = f"{addon}/catalog/{src['type']}/{src['id']}"
    if src.get("genre"):
        path += "/genre=" + urllib.parse.quote(src["genre"], safe="")
    metas = get_json(path + ".json").get("metas", [])[:limit]
    for m in metas:
        yield src["type"], m


def backdrop(addon, typ, meta):
    bg = meta.get("background")
    if not bg:
        try:
            full = get_json(f"{addon}/meta/{typ}/{urllib.parse.quote(meta['id'], safe='')}.json")["meta"]
            bg = full.get("background")
        except Exception:
            bg = None
    return bg


def render(bg, title, subtitle, accent):
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1), Image.LANCZOS)
    l, t = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((l, t, l + W, t + H))
    if not title:  # hero backdrop: the app adds its own logo and shading
        return bg
    # Darken the bottom (and bottom-left, behind the text) so white text always reads.
    mask = Image.new("L", (W, H), 0)
    px = mask.load()
    for y in range(H):
        v = 235 * max(0.0, (y - H * 0.35) / (H * 0.65)) ** 1.3
        side = max(0.0, (y - H * 0.45) / (H * 0.55))
        for x in range(W):
            h = 110 * max(0.0, 1 - x / (W * 0.6)) * side
            px[x, y] = min(255, int(v + h))
    img = Image.composite(Image.new("RGB", (W, H), (8, 8, 12)), bg, mask)
    d = ImageDraw.Draw(img)
    k = W / 2560
    ft = ImageFont.truetype(str(FONTS / "Montserrat-Black.ttf"), int(205 * k))
    fs = ImageFont.truetype(str(FONTS / "Montserrat-SemiBold.ttf"), int(60 * k))
    x0, ty = int(140 * k), int(1215 * k)
    sy = ty + int(100 * k)
    d.text((x0, ty), title, font=ft, fill=(255, 255, 255), anchor="ls")
    x = x0 + int(8 * k)
    for ch in subtitle:
        d.text((x, sy), ch, font=fs, fill=(205, 212, 228), anchor="ls")
        x += d.textlength(ch, font=fs) + 6 * k
    d.rectangle((x0 - int(42 * k), ty - int(150 * k), x0 - int(32 * k), sy + int(8 * k)), fill=tuple(accent))
    return img


def main():
    dry = "--dry-run" in sys.argv
    cfg = json.loads((ROOT / "covers.json").read_text())
    # The addon URL contains Romulo's AIOMetadata UUID, so it lives in a local, untracked file.
    addon = (ROOT / "addon.url").read_text().strip().rstrip("/")
    state_path = OUT / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    used, changed, report = set(), [], []
    # Heroes run after covers, so a platform's hero never repeats one of its folder covers.
    for c in cfg["covers"] + cfg.get("heroes", []):
        pick = None
        for src in c["sources"]:
            try:
                for typ, m in candidates(addon, src):
                    if m["id"] in used or not primary_ok(src, m):
                        continue
                    bg = backdrop(addon, typ, m)
                    if bg:
                        pick = (typ, m, bg)
                        break
            except Exception as e:  # one dead source shouldn't kill the folder
                report.append(f"  ! {c['file']}: source {src['id']} failed: {e}")
            if pick:
                break
        if not pick:
            report.append(f"  ! {c['file']}: no usable title, keeping previous cover")
            continue
        typ, m, bg_url = pick
        used.add(m["id"])
        prev = state.get(c["file"], {})
        report.append(f"  {c['file']}: {m['name']} ({typ})")
        if prev.get("id") == m["id"] and prev.get("background") == bg_url and (OUT / c["file"]).exists():
            continue
        if not dry:
            img = render(get_image(bg_url), c.get("title", ""), c.get("subtitle", ""), c.get("accent", (0, 0, 0)))
            dest = OUT / c["file"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            img.save(dest, quality=86, optimize=True, progressive=True)
            state[c["file"]] = {"id": m["id"], "name": m["name"], "type": typ, "background": bg_url}
        changed.append(c["file"])
    if not dry:
        OUT.mkdir(exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    print("\n".join(report))
    print(f"changed: {len(changed)} {changed}")


if __name__ == "__main__":
    main()
