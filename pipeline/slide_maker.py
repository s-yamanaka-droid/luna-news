"""
Now on AIr — Slide Maker v10 (Codex CLI 主・Playwright fallback)
ChatGPT Plus サブスク経由で Codex CLI を呼び、リッチ図解 PNG を生成。
API課金ゼロ・記事ごとにレイアウト/アイコンが変わる editorial 品質。
Codex 失敗時は slide_maker_playwright.py で安全フォールバック。
"""
from __future__ import annotations
import os
import re
import shutil
import subprocess
from pathlib import Path

BRAND = os.environ.get("NOW_ON_BRAND", "AIr")
PRI = os.environ.get("NOW_ON_PRIMARY_COLOR", "#CE1141")
CODEX_BIN = os.environ.get("CODEX_BIN", "/opt/homebrew/bin/codex")
SLIDE_PROVIDER = os.environ.get("SLIDE_PROVIDER", "codex").lower()  # codex / playwright
CODEX_TIMEOUT = int(os.environ.get("CODEX_SLIDE_TIMEOUT", "600"))   # 内蔵画像生成は3-5分かかる

PROMPT_TEMPLATE = """Use your built-in image generation tool (the one that produces files in ~/.codex/generated_images) to create ONE 1536x1024 magazine-editorial illustrated infographic about the article below. Do NOT use Python PIL. Use the image generation capability and then copy the result to EXACTLY: {output}

ARTICLE:
- Category: {category}
- Title (Japanese, render it on the image): {title}
- Summary (Japanese, render briefly on the image): {summary}
- Source: {source}
- Four key points (each becomes ONE illustrated card with its own scene):
{keypoints}

STYLE — high-end Japanese magazine editorial infographic:
- 1536x1024, pure white background
- THIN solid horizontal bar across the very top in {pri}
- Title in HUGE bold black Japanese type, prominent at top
- Below title: a thin red category pill on the left, brand mark "Now on AIr" on the right
- A thin-bordered summary strip under the title with the Japanese summary
- Lower 60% of the canvas: FOUR illustrated CARDS in a single horizontal row, each card showing:
   * A UNIQUE rich illustration combining 2-4 visual elements that represent that key point (e.g. building + dollar signs + arrows / AI chip + network nodes + person / people in meeting room with charts / growth chart + plants + money stacks)
   * A red number badge "01"/"02"/"03"/"04" in the corner
   * The key point text in BOLD Japanese below the illustration
- Color palette: strictly white background, {pri} red as primary accent, black text, light gray borders
- Japanese characters must render PERFECTLY and crisply — no garbled text, no random shapes
- Editorial / Swiss / magazine feel — refined, NOT amateurish, NOT photorealistic, NOT cartoon
- No gradients, no decorative emoji, no dark backgrounds

After image generation completes, locate the generated file in ~/.codex/generated_images and copy it to: {output}
Then print ONLY the final absolute path. Do not ask questions."""


def _recover_from_codex_output(text: str, output_path: Path) -> bool:
    """Codex の標準出力から '~/.codex/generated_images/.../ig_xxx.png' を抽出して手動コピー"""
    m = re.search(r"(/[\w./\-]*\.codex/generated_images/[\w\-]+/ig_[\w]+\.png)", text)
    if not m:
        return False
    src = Path(m.group(1))
    if src.exists() and src.stat().st_size > 8000:
        try:
            shutil.copyfile(src, output_path)
            print(f"  [codex] 手動コピー回復: {src.name} → {output_path.name}")
            return True
        except Exception as e:
            print(f"  [codex] 手動コピー失敗: {e}")
    return False


def _recover_latest_codex_image(output_path: Path) -> bool:
    """タイムアウト時、最近1分以内の Codex 生成画像を拾う最後の手段"""
    import time
    base = Path.home() / ".codex" / "generated_images"
    if not base.exists():
        return False
    pngs = sorted(base.glob("*/ig_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if pngs and (time.time() - pngs[0].stat().st_mtime) < 600 and pngs[0].stat().st_size > 8000:
        try:
            shutil.copyfile(pngs[0], output_path)
            print(f"  [codex] timeout後回復: {pngs[0].name} → {output_path.name}")
            return True
        except Exception as e:
            print(f"  [codex] timeout後回復失敗: {e}")
    return False


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
    output_path = Path(output_path).resolve()   # ← 絶対パスに強制（cwd=/tmp 罠回避）
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()
    prompt = _build_prompt(title, category, source, summary, keypoints, output_path)
    try:
        # cwd を output_path の親のさらに親（リポルート相当）にして workspace-write の書込許可範囲に含める
        codex_cwd = str(output_path.parent.parent.parent)  # docs/assets/images/<date>/topic_X.png → リポ直下
        proc = subprocess.run(
            [CODEX_BIN, "exec", "--skip-git-repo-check",
             "--sandbox", "workspace-write",
             "--cd", codex_cwd, prompt],
            cwd=codex_cwd, capture_output=True, text=True, timeout=CODEX_TIMEOUT,
        )
        if output_path.exists() and output_path.stat().st_size > 8000:
            return True
        # サンドボックスで Codex がコピー失敗した場合、stdout/stderr から生成画像パスを拾って手動コピー
        if _recover_from_codex_output((proc.stdout or "") + "\n" + (proc.stderr or ""), output_path):
            return True
        print(f"  [codex] 画像未生成 rc={proc.returncode}\n{(proc.stderr or proc.stdout)[-400:]}")
        return False
    except subprocess.TimeoutExpired:
        print(f"  [codex] timeout ({CODEX_TIMEOUT}s) → 直近の生成画像を探す")
        return _recover_latest_codex_image(output_path)
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
