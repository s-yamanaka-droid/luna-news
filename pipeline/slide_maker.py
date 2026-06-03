"""
Now on AIr — Slide Maker v10 (Codex CLI 主・Playwright fallback)
ChatGPT Plus サブスク経由で Codex CLI を呼び、リッチ図解 PNG を生成。
API課金ゼロ・記事ごとにレイアウト/アイコンが変わる editorial 品質。
Codex 失敗時は slide_maker_playwright.py で安全フォールバック。
"""
from __future__ import annotations
import os
import subprocess
from pathlib import Path

BRAND = os.environ.get("NOW_ON_BRAND", "AIr")
PRI = os.environ.get("NOW_ON_PRIMARY_COLOR", "#CE1141")
CODEX_BIN = os.environ.get("CODEX_BIN", "/opt/homebrew/bin/codex")
SLIDE_PROVIDER = os.environ.get("SLIDE_PROVIDER", "codex").lower()  # codex / playwright
CODEX_TIMEOUT = int(os.environ.get("CODEX_SLIDE_TIMEOUT", "300"))

PROMPT_TEMPLATE = """Generate ONE 1536x1024 editorial infographic PNG using Python PIL/Pillow. Save EXACTLY to: {output}

ARTICLE (render Japanese with a CJK-capable TTF — search /System/Library/Fonts (e.g. ヒラギノ角ゴシック W7.ttc, ヒラギノ角ゴ ProN W6.ttc) or /System/Library/Fonts/Supplemental for Noto / Hiragino. Try multiple until one works):
- Category: {category}
- Title: {title}
- Summary: {summary}
- Source: {source}
- Four key points (each = 1 card):
{keypoints}

DESIGN SPEC (follow precisely — be deterministic, no AI-randomness):
- 1536x1024, pure white background (#FFFFFF)
- TOP: solid 5px horizontal bar across the very top in {pri}
- TOP-LEFT (x=80, y=70): a ROUNDED PILL filled {pri} 38px tall, padding-x 22px, contains the category in BOLD WHITE Hiragino 18px
- TOP-RIGHT (right-aligned at x=1456, y=78): brand mark "Now on AIr" — render "Now on " in gray 22px, "AI" in {pri} BOLD 28px, "r" in gray 18px
- CENTER-UPPER (x=80, y=190): TITLE in Hiragino BOLD #111 size 64px, wrap to MAX 2 lines, max width 1376px, line spacing 1.15
- BELOW TITLE (x=80, y=410): SUMMARY box — light gray rounded rectangle (fill #F4F4F6, no border, radius 8px, height 86px, width 1376px, padding 24px), Japanese 22px #333 inside, single line truncated if too long
- LOWER HALF — exactly FOUR cards in one horizontal row:
    * Each card: 320x420 px, white fill, 1px gray border #DDDDDD, top 4px solid bar in {pri}
    * Row positioned: cards x = 80, 416, 752, 1088 ; y = 560
    * Card padding 22px
    * Number badge in top-right corner of each card: filled {pri} rectangle 56x32, white BOLD monospace "01"/"02"/"03"/"04" centered
    * Center of card: A SIMPLE FLAT VECTOR ICON drawn with PIL primitives in {pri} (40x40 area centered at x=card_left+160, y=card_top+150). Each card MUST use a DIFFERENT icon shape; pick from: shield-with-check, three connected nodes (network), bar-chart, padlock, gear, cloud, document, rocket, target, lightbulb. Use thick strokes (3-4px) and clean geometry.
    * Below icon (y=card_top+220): the key point text in Hiragino BOLD #111 22px, centered, wrap to 2-3 lines max, ellipsis if longer
- BOTTOM-LEFT (x=80, y=970): "NOW ON AIR // EDITORIAL" monospace 14px #888 (uppercase)
- BOTTOM-RIGHT (right-aligned at x=1456, y=970): "SOURCE: {source}" monospace 14px #444 (truncate source if too long)

STYLE RULES:
- Strictly limited palette: white background, {pri} accents, black/dark gray for text, light gray for borders
- No gradients, no shadows, no photos, no decorative emoji
- Japanese characters MUST render correctly — fall back through multiple CJK fonts if first fails
- Numbers/English in monospace where specified
- Refined, magazine editorial / Swiss design feel

OUTPUT: After saving, verify the file exists and print ONLY the absolute file path. Do not ask questions, do not stop for confirmation. If a font load fails, retry with another CJK font automatically."""


def _build_prompt(title, category, source, summary, keypoints, output_path):
    kp_text = "\n".join(f"   {i+1}. {k}" for i, k in enumerate((keypoints or [])[:4]))
    return PROMPT_TEMPLATE.format(
        output=str(output_path),
        category=(category or "AI")[:12],
        title=(title or "")[:80],
        summary=(summary or "")[:160],
        source=(source or "")[:32],
        keypoints=kp_text,
        pri=PRI,
    )


def _codex_generate(title, category, source, summary, keypoints, output_path):
    """Codex CLI 経由で PIL/Python コード生成 → PNG 保存"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()
    prompt = _build_prompt(title, category, source, summary, keypoints, output_path)
    try:
        proc = subprocess.run(
            [CODEX_BIN, "exec", "--skip-git-repo-check",
             "--sandbox", "workspace-write", prompt],
            cwd="/tmp", capture_output=True, text=True, timeout=CODEX_TIMEOUT,
        )
        if output_path.exists() and output_path.stat().st_size > 8000:
            return True
        print(f"  [codex] 画像未生成 rc={proc.returncode}\n{(proc.stderr or proc.stdout)[-400:]}")
        return False
    except subprocess.TimeoutExpired:
        print(f"  [codex] timeout ({CODEX_TIMEOUT}s)")
        return output_path.exists() and output_path.stat().st_size > 8000
    except Exception as e:
        print(f"  [codex] error: {e}")
        return False


def _playwright_fallback(title, category, source, summary, keypoints, output_path):
    """Playwright HTML→PNG（高速・確実）にフォールバック"""
    try:
        from slide_maker_playwright import generate_slide as _pw
        return _pw(title, category, source, summary, keypoints, output_path)
    except Exception as e:
        print(f"  [fallback playwright] 失敗: {e}")
        return False


def generate_slide(title, category, source, summary, keypoints, output_path, size="1536x1024"):
    """主：Codex CLI / 副：Playwright（Codex 失敗時の安全網）"""
    output_path = Path(output_path)
    if SLIDE_PROVIDER == "playwright":
        return _playwright_fallback(title, category, source, summary, keypoints, output_path)
    # Codex 主
    ok = _codex_generate(title, category, source, summary, keypoints, output_path)
    if ok:
        return True
    print("  [slide_maker] Codex 失敗 → Playwright fallback")
    return _playwright_fallback(title, category, source, summary, keypoints, output_path)


if __name__ == "__main__":
    out = Path("/tmp/test_slide_codex_v10.png")
    ok = generate_slide(
        title="OpenAI、企業向けAI導入子会社「DeployCo」を立ち上げ──40億ドル調達",
        category="業界動向",
        source="OpenAI Blog",
        summary="OpenAI傘下のDeployCo、企業向けAI導入コンサルを開始。40億ドル超調達、Palantir流現地駐在型展開。",
        keypoints=[
            "巨額投資で設立 TPG主導で40億ドル超調達",
            "現地駐在型導入 顧客データとAIを統合",
            "統合が競争力 ワークフロー設計で差別化",
            "戦略的フィードバック 現場知見をモデル開発へ",
        ],
        output_path=out,
    )
    print(f"生成: {ok} → {out}")
