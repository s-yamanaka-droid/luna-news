"""
号の4役の画像（トップ・PC図解・mobile図解・OG）を記事データから揃える。
既にある画像はそのまま使い、足りないものだけを作る。

- トップ: pipeline/cast_kv.py（Racco・むちむち猫・アザラシの場面 / Codex CLI）
- 図解: editorial_diagram.examples（なければ keypoints）の3項目をHTMLで組み、Chromeで書き出す
- OG: 見出しとトップ画像を1200x630に組む

使い方: python scripts/issue_images.py YYYY-MM-DD
"""
from __future__ import annotations
import html
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs"
sys.path.insert(0, str(ROOT / "pipeline"))
from cast_kv import generate_cast_kv  # noqa: E402

CHROME = os.environ.get("CHROME_BIN", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;800;900'
         '&family=Noto+Serif+JP:wght@600&display=swap" rel="stylesheet">')
ACCENT = "#821c32"


def esc(value) -> str:
    return html.escape(str(value or ""))


def exists(ref) -> bool:
    return bool(ref) and isinstance(ref, str) and (SITE / ref.lstrip("/")).is_file()


def shoot(markup: str, width: int, height: int, out_png: Path) -> None:
    """HTMLをChromeでPNGに書き出す（フォント読込のため仮想時間を待つ）"""
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(markup, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--allow-file-access-from-files",
                        "--virtual-time-budget=8000", f"--window-size={width},{height}",
                        f"--screenshot={out_png}", page.as_uri()],
                       capture_output=True, timeout=120, check=False)
    if not out_png.exists() or out_png.stat().st_size < 5000:
        raise RuntimeError(f"render failed: {out_png.name}")


def to_webp(png: Path, dst: Path) -> None:
    from PIL import Image
    Image.open(png).convert("RGB").save(dst, "WEBP", quality=82, method=6)


def panels(article: dict) -> list[tuple[str, str]]:
    diagram = article.get("editorial_diagram") or {}
    items = [tuple(x[:2]) for x in (diagram.get("examples") or []) if isinstance(x, (list, tuple)) and len(x) >= 2]
    if not items:
        items = [(f"ポイント{i}", k) for i, k in enumerate(article.get("keypoints") or [], 1)]
    return [(str(h), str(t)) for h, t in items[:3]]


def diagram_html(article: dict, layout: str) -> str:
    diagram = article.get("editorial_diagram") or {}
    cards = "".join(f'<section class="panel"><div class="step">{"①②③"[i]} {esc(h)}</div><p>{esc(t)}</p></section>'
                    for i, (h, t) in enumerate(panels(article)))
    mobile = layout == "mobile"
    size = "width:1024px;height:1536px;grid-template-columns:1fr;grid-template-rows:auto repeat(3,1fr) auto" if mobile \
        else "width:2172px;height:724px;grid-template-columns:repeat(3,1fr);grid-template-rows:auto 1fr auto"
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">{FONTS}<style>
*{{box-sizing:border-box}}html,body{{margin:0}}
body{{font-family:"Noto Sans JP","Hiragino Sans",sans-serif;color:#171719;background:#fbf8f1}}
.board{{display:grid;gap:{26 if mobile else 34}px;padding:{"44px 52px" if mobile else "40px 56px"};{size}}}
header{{grid-column:1/-1}}.kicker{{font-size:{22 if mobile else 22}px;font-weight:800;color:{ACCENT};letter-spacing:.06em}}
h1{{font-family:"Noto Serif JP",serif;font-weight:600;font-size:{46 if mobile else 50}px;line-height:1.3;margin:8px 0 0;letter-spacing:-.02em}}
.panel{{background:#fffdf7;border:3px solid #1b1b1d;border-radius:10px;padding:{"26px 32px" if mobile else "30px 36px"};box-shadow:10px 10px 0 #ece6d8;overflow:hidden;display:flex;flex-direction:column;justify-content:center}}
.step{{font-size:{34 if mobile else 34}px;font-weight:900;color:{ACCENT};margin-bottom:12px}}
.panel p{{font-size:{34 if mobile else 33}px;line-height:1.6;font-weight:700;margin:0}}
.note{{grid-column:1/-1;font-size:19px;color:#53545a;margin:0;line-height:1.5}}
</style></head><body><div class="board"><header><div class="kicker">{esc(diagram.get("kicker") or article.get("category"))}</div>
<h1>{esc(diagram.get("title") or article.get("title"))}</h1></header>{cards}
<p class="note">{esc(diagram.get("note") or "原典の記載から編集部が図にしたもの。図は模式表現です。")}</p></div></body></html>'''


def social_html(article: dict, hero: Path | None) -> str:
    art = f'<img src="{hero.as_uri()}" alt="">' if hero and hero.exists() else ""
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">{FONTS}<style>
*{{box-sizing:border-box}}html,body{{margin:0}}body{{width:1200px;height:630px;background:#fbf8f1;font-family:"Noto Sans JP",sans-serif;color:#171719}}
.card{{display:grid;grid-template-columns:1fr 520px;height:630px}}.text{{padding:54px 48px;display:flex;flex-direction:column}}
.bar{{height:8px;background:{ACCENT};position:absolute;top:0;left:0;right:0}}
.cat{{font-size:22px;font-weight:800;color:{ACCENT}}}h1{{font-size:46px;line-height:1.35;font-weight:900;margin:18px 0 auto;letter-spacing:-.02em;word-break:auto-phrase}}
.brand{{font-size:28px;font-weight:800;letter-spacing:-.03em}}.brand small{{font-size:16px;color:#53545a;font-weight:500;margin-left:12px}}
img{{width:520px;height:630px;object-fit:cover;object-position:30% 50%;display:block}}
</style></head><body><div class="bar"></div><div class="card"><div class="text"><div class="cat">{esc(article.get("category"))}</div>
<h1>{esc(article.get("title"))}</h1><div class="brand">now on air<small>by Lakkan</small></div></div>{art}</div></body></html>'''


def fill(date_str: str) -> int:
    path = SITE / "news" / date_str / "articles.json"
    raw = path.read_text(encoding="utf-8")
    articles = json.loads(raw)
    (SITE / "assets" / "illustrations").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "og").mkdir(parents=True, exist_ok=True)
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for number, article in enumerate(articles, 1):
            stem = f"{date_str}-story-{number}"
            if not exists(article.get("hero_image")):
                if not generate_cast_kv(article, date_str, number):
                    failed += 1
            diagram = article.setdefault("editorial_diagram", {})
            for layout, size in (("wide", (2172, 724)), ("mobile", (1024, 1536))):
                if not exists(diagram.get(layout)):
                    png = tmp / f"{stem}-{layout}.png"
                    shoot(diagram_html(article, layout), *size, png)
                    to_webp(png, SITE / "assets" / "illustrations" / f"{stem}-diagram-{layout}.webp")
                    diagram[layout] = f"/assets/illustrations/{stem}-diagram-{layout}.webp"
            if not diagram.get("alt"):
                diagram["alt"] = "、".join(f"{h}：{t}" for h, t in panels(article))[:200]
            if not exists(article.get("social_image")):
                hero = SITE / str(article.get("hero_image") or "").lstrip("/") if article.get("hero_image") else None
                out = SITE / "assets" / "og" / f"{stem}.png"
                shoot(social_html(article, hero), 1200, 630, out)
                article["social_image"] = f"/assets/og/{stem}.png"
            print(f"  [images] story-{number} ok")
    path.write_text(json.dumps(articles, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else ""),
                    encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/issue_images.py YYYY-MM-DD")
    sys.exit(fill(sys.argv[1]))
