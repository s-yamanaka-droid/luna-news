"""
Now on AIr — トップ記事のキャラクター場面（Racco・むちむち猫・アザラシ）
Codex CLI の内蔵画像生成で、記事ごとにコラム風の場面を1枚つくる。
Racco が大きく反応し、むちむち猫が素朴に聞き、アザラシは聞いていないふりで聞いている。
記事の事実や数字は画像に描かず、本文の HTML で示す。

単体実行: python pipeline/cast_kv.py 2026-10-15   # その号のトップ記事に場面を付けて index を再生成
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_DIR / "docs"
REF_DIR = Path(__file__).resolve().parent / "cast_refs"
REFS = [REF_DIR / "racco.png", REF_DIR / "muchimuchi-cat.png", REF_DIR / "seal.png"]
# slide_maker.py と同じく PATH 上の codex を優先する
CODEX_BIN = os.environ.get("CODEX_BIN") or shutil.which("codex") or str(Path.home() / "Mark6-Work" / "bin" / "codex")
CODEX_TIMEOUT = int(os.environ.get("CODEX_CAST_TIMEOUT", "600"))
CREDIT = "編集イメージ / AI生成（Racco・むちむち猫・アザラシ）"

PROMPT_TEMPLATE = """Generate ONE image with your built-in image generation tool, then copy the PNG to EXACTLY: {output}
Do not draw it with code. Then write ONE Japanese sentence (under 90 characters) describing the image for screen readers to EXACTLY: {alt_output}

CHARACTERS (keep them on-model with the attached references, in this order):
- Racco (reference 1): brown otter, thick black round glasses, light grey hoodie.
- Muchimuchi cat (reference 2): chubby orange tabby, blue cardigan over a white T-shirt.
- Seal (reference 3): chubby grey harbor seal with darker spots, cream chunky knit sweater.

ARTICLE (Japanese) — read it and invent a column-style scene that hints at its topic:
- Category: {category}
- Title: {title}
- Summary: {lede}
- Key points:
{keypoints}

SCENE RULES:
- Racco reacts strongly and comically to the news (e.g. a sudden "BANG!" shock, wide eyes, manga-style radial speed lines in brick red).
- The cat leans in and asks a naive question with its gesture (head tilt, raised paw, pointing).
- The seal pretends not to listen (back turned, reading, headphones, napping) but one eye or ear is clearly turned toward them.
- Show the topic only through props (a paper, laptop screen, calendar, whiteboard) using abstract shapes or simple charts.
- Landscape 3:2, 1536x1024. Soft 3D plush render, warm natural light, warm off-white and wood tones with small brick-red (#b4382b) accents.
- No text, letters, numbers, logos or watermarks anywhere in the image. No real company logos or product screens.

Print ONLY the final absolute path of the image. Do not ask questions."""


def _build_prompt(article: dict, output: Path, alt_output: Path) -> str:
    keypoints = "\n".join(f"   - {k}" for k in (article.get("keypoints") or [])[:4]) or "   - (none)"
    return PROMPT_TEMPLATE.format(
        output=str(output), alt_output=str(alt_output),
        category=(article.get("category") or "AI")[:20],
        title=(article.get("title") or "")[:100],
        lede=(article.get("lede") or "")[:200],
        keypoints=keypoints,
    )


def _recover_latest(output: Path, started_at: float) -> bool:
    """Codex がコピーに失敗したとき、起動後に生成された最新の画像を拾う"""
    base = Path.home() / ".codex" / "generated_images"
    if not base.exists():
        return False
    pngs = [p for p in base.glob("*/*.png") if p.stat().st_mtime >= started_at - 5 and p.stat().st_size > 8000]
    if not pngs:
        return False
    src = max(pngs, key=lambda p: p.stat().st_mtime)
    shutil.copyfile(src, output)
    print(f"  [cast] 生成画像を回復: {src.name}")
    return True


def _to_web(png: Path, stem: Path) -> Path:
    """PIL があれば WebP、なければ macOS の sips で JPEG にして軽くする"""
    try:
        from PIL import Image
        dst = stem.with_suffix(".webp")
        Image.open(png).convert("RGB").save(dst, "WEBP", quality=82, method=6)
        return dst
    except ImportError:
        pass
    dst = stem.with_suffix(".jpg")
    proc = subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82", str(png), "--out", str(dst)],
                          capture_output=True, text=True)
    return dst if proc.returncode == 0 and dst.exists() else png


def generate_cast_kv(article: dict, date_str: str, number: int = 1) -> bool:
    """記事に場面画像を付ける。成功すると article の hero_image / alt / credit を書き換える"""
    out_dir = SITE_DIR / "assets" / "illustrations"
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / f"{date_str}-story-{number}-cast"
    tmp_dir = REPO_DIR / ".cast-tmp"
    tmp_dir.mkdir(exist_ok=True)
    png, alt_txt = tmp_dir / f"{stem.name}.png", tmp_dir / f"{stem.name}.alt.txt"
    for p in (png, alt_txt):
        p.unlink(missing_ok=True)
    prompt = _build_prompt(article, png, alt_txt)
    cmd = [CODEX_BIN, "exec", "--skip-git-repo-check", "--sandbox", "workspace-write", "--cd", str(REPO_DIR)]
    for ref in REFS:
        cmd += ["-i", str(ref)]
    started_at = time.time()
    try:
        # -i は複数値を取るので、プロンプトは標準入力で渡す
        subprocess.run(cmd, input=prompt, cwd=REPO_DIR, capture_output=True, text=True, timeout=CODEX_TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"  [cast] timeout ({CODEX_TIMEOUT}s) → 直近の生成画像を探す")
    except Exception as e:
        print(f"  [cast] error: {e}")
        return False
    if not (png.exists() and png.stat().st_size > 8000) and not _recover_latest(png, started_at):
        print("  [cast] 画像未生成。既存の hero_image のまま")
        return False
    web = _to_web(png, stem)
    if web == png:
        web = stem.with_suffix(".png")
        shutil.copyfile(png, web)
    alt = alt_txt.read_text(encoding="utf-8").strip() if alt_txt.exists() else ""
    article["hero_image"] = "/assets/illustrations/" + web.name
    article["hero_image_alt"] = alt or "記事の話題に驚くラッコのRaccoと、のぞき込むむちむち猫、聞いていないふりのアザラシ。"
    article["hero_image_credit"] = CREDIT
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"  [cast] {web.relative_to(REPO_DIR)}")
    return True


def main(date_str: str) -> int:
    """その号のトップ記事に場面を付け、articles.json とトップページを更新する"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from html_builder import build_index
    path = SITE_DIR / "news" / date_str / "articles.json"
    articles = json.loads(path.read_text(encoding="utf-8"))
    if not articles or not generate_cast_kv(articles[0], date_str):
        return 1
    path.write_text(json.dumps(articles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dates = sorted(d.name for d in (SITE_DIR / "news").iterdir() if (d / "articles.json").exists())
    if dates and dates[-1] == date_str:
        print(f"  [cast] {build_index(dates, articles, date_str)}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python pipeline/cast_kv.py YYYY-MM-DD")
    sys.exit(main(sys.argv[1]))
