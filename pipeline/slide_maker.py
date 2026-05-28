"""
Now on AIr — Slide Maker (Codex CLI 版)
ChatGPT Plus サブスク経由で Codex CLI を呼び、PILで日本語完璧な図解PNGを生成。
API課金ゼロ・文字化けゼロ・editorial品質。
"""
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

BRAND_NAME = os.environ.get("NOW_ON_BRAND", "AIr")
PRIMARY_COLOR = os.environ.get("NOW_ON_PRIMARY_COLOR", "#CE1141")
CODEX_BIN = os.environ.get("CODEX_BIN", "/opt/homebrew/bin/codex")

PROMPT_TEMPLATE = """Write and run a Python script (using PIL/Pillow) that renders ONE 1536x1024 PNG infographic and saves it to exactly this path: {output_path}

This is a Japanese editorial news-card infographic for the media brand "Now on {brand}".

ARTICLE DATA (use this text EXACTLY, render Japanese perfectly with a CJK font like Hiragino Sans / Noto Sans CJK):
- Category label: {category}
- Title: {title}
- Summary: {summary}
- Source: {source}
- Four key points (each becomes one card):
{keypoints}

DESIGN SPEC (follow precisely):
- Pure white background (#FFFFFF)
- Primary accent color: {primary_color}
- Thin horizontal accent line across the very top (4px, in {primary_color})
- Top-left: small SOLID PILL filled with {primary_color}, white bold text = the category label
- Top-right: brand mark "Now on {brand_main}{brand_sub}" — "{brand_main}" in {primary_color} bold, "{brand_sub}" smaller gray
- Center-upper: the TITLE in large bold black Japanese (use a large font size, wrap to max 2 lines)
- Below title: the SUMMARY in a light gray rounded box, smaller black Japanese text
- Lower half: FOUR cards in a horizontal row (or 2x2 grid), each card:
   * thin light-gray border, a {primary_color} top accent line
   * a number badge 01/02/03/04 in a corner ({primary_color} bg, white)
   * a SIMPLE FLAT VECTOR-STYLE ICON drawn with PIL primitives (each card a DIFFERENT icon: shield, network nodes, bar chart, lock, gear, cloud, document, rocket, etc.) in {primary_color}
   * the key point's Japanese text below the icon, bold black, wrapped
- Bottom corners: tiny monospace footer marks (gray)
- Style: refined Swiss / magazine editorial, generous whitespace, NO gradients, NO photos, only white/black/{primary_color}/gray
- MUST find and use an installed Japanese-capable TTF font (search /System/Library/Fonts and /Library/Fonts; Hiragino, Noto, or similar). Render all Japanese crisply — no tofu/boxes.

After saving, verify the file exists and print ONLY the absolute file path. Do not ask questions. Do not stop for confirmation."""


def _build_prompt(title, category, source, summary, keypoints, output_path):
    kp_text = "\n".join(f"   {i+1}. {k}" for i, k in enumerate(keypoints[:4]))
    return PROMPT_TEMPLATE.format(
        title=title, category=category, source=source,
        summary=summary[:160], keypoints=kp_text,
        primary_color=PRIMARY_COLOR,
        brand=BRAND_NAME,
        brand_main=BRAND_NAME[:-1],
        brand_sub=BRAND_NAME[-1],
        output_path=str(output_path),
    )


def generate_slide(
    title: str,
    category: str,
    source: str,
    summary: str,
    keypoints: list[str],
    output_path: Path,
    size: str = "1536x1024",
) -> bool:
    """Codex CLI 経由で 1536x1024 の図解PNGを生成（ChatGPT Plus課金・API課金ゼロ）"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    # Codex のサンドボックスは /tmp 配下しか書けないので、tmp に生成→移動
    tmp_out = Path(tempfile.gettempdir()) / f"nowonair_slide_{uuid.uuid4().hex}.png"
    prompt = _build_prompt(title, category, source, summary, keypoints, tmp_out)
    try:
        proc = subprocess.run(
            [CODEX_BIN, "exec", "--skip-git-repo-check",
             "--sandbox", "workspace-write", prompt],
            cwd=tempfile.gettempdir(),
            capture_output=True, text=True, timeout=420,
        )
        if tmp_out.exists() and tmp_out.stat().st_size > 5000:
            shutil.move(str(tmp_out), str(output_path))
            return True
        print(f"  [codex] 画像未生成 rc={proc.returncode}\n{proc.stdout[-400:]}\n{proc.stderr[-200:]}")
        return False
    except subprocess.TimeoutExpired:
        if tmp_out.exists() and tmp_out.stat().st_size > 5000:
            shutil.move(str(tmp_out), str(output_path))
            return True
        print("  [codex] タイムアウト(420s)")
        return False
    except Exception as e:
        print(f"  [codex] error: {e}")
        return False


if __name__ == "__main__":
    out = Path("/tmp/test_slide_codex.png")
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
