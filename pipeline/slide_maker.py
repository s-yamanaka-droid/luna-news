"""
Now on AIr — Slide Maker v9 (HTML/CSS → Playwright)
60:40 split — ダークヘッダー + ホワイトカードグリッド。コスト $0。
"""
from __future__ import annotations
import os, html
from pathlib import Path

BRAND = os.environ.get("NOW_ON_BRAND", "AIr")
PRI = os.environ.get("NOW_ON_PRIMARY_COLOR", "#CE1141")

W, H = 1536, 1024
HEADER_H = 560
CARD_H = H - HEADER_H

CARD_COLORS = ["#CE1141", "#2563EB", "#059669", "#7C3AED"]


def _html(title: str, category: str, source: str, summary: str,
          keypoints: list[str]) -> str:
    t = html.escape(title)
    cat = html.escape(category or "AI")
    src = html.escape(source or "")
    summ = html.escape(summary or "")
    kps = (keypoints or ["—"])[:4]

    kp_html = ""
    for i, kp in enumerate(kps):
        parts = kp.split(None, 1) if len(kp) > 6 else [kp]
        kp_t = html.escape(parts[0])
        kp_d = html.escape(parts[1]) if len(parts) > 1 else ""
        c = CARD_COLORS[i % len(CARD_COLORS)]
        kp_html += f"""
        <div class="card" style="--c:{c}">
          <div class="card-num" style="color:{c}">{i+1:02d}</div>
          <div class="card-title">{kp_t}</div>
          <div class="card-desc">{kp_d}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: {W}px; height: {H}px;
    font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans CJK JP', sans-serif;
    overflow: hidden;
  }}

  /* ===== ダークヘッダー ===== */
  .header {{
    width: {W}px;
    height: {HEADER_H}px;
    background: linear-gradient(160deg, #0d0d1a 0%, #1a1a2e 50%, #16213e 100%);
    padding: 0 80px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding-bottom: 40px;
    position: relative;
    overflow: hidden;
  }}
  .header::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 5px;
    background: linear-gradient(90deg, {PRI}, #ff6b6b);
  }}
  .header::after {{
    content: '';
    position: absolute;
    top: -80px; right: -60px;
    width: 320px; height: 320px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(206,17,65,0.08) 0%, transparent 70%);
  }}

  .top-row {{
    position: absolute;
    top: 32px; left: 80px; right: 80px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .brand {{
    font-size: 15px; color: #6a6a7e;
  }}
  .brand strong {{
    font-size: 20px; font-weight: 900; color: {PRI};
  }}
  .category {{
    background: rgba(206,17,65,0.15);
    border: 1px solid rgba(206,17,65,0.3);
    color: {PRI};
    font-size: 11px; font-weight: 700;
    padding: 5px 18px;
    border-radius: 100px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }}

  .title {{
    font-size: 42px;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.35;
    letter-spacing: -0.5px;
    margin-bottom: 20px;
    position: relative; z-index: 1;
  }}

  .summary-wrap {{
    display: flex; gap: 14px;
    position: relative; z-index: 1;
  }}
  .summary-bar {{
    width: 3px;
    background: linear-gradient(180deg, {PRI}, rgba(206,17,65,0.2));
    border-radius: 2px; flex-shrink: 0;
  }}
  .summary {{
    font-size: 17px;
    color: #8a8aa0;
    line-height: 1.7;
  }}

  /* ===== カードグリッド ===== */
  .cards {{
    width: {W}px;
    height: {CARD_H}px;
    background: #f5f5f7;
    padding: 24px 80px 20px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 14px;
  }}

  .card {{
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 1px 8px rgba(0,0,0,0.04), 0 0 1px rgba(0,0,0,0.06);
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-top: 3px solid var(--c);
    overflow: hidden;
  }}

  .card-num {{
    font-size: 13px;
    font-weight: 900;
    margin-bottom: 8px;
    letter-spacing: 1px;
  }}

  .card-title {{
    font-size: 20px;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.4;
    margin-bottom: 6px;
  }}

  .card-desc {{
    font-size: 15px;
    color: #6b6b80;
    line-height: 1.5;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }}

  .footer {{
    position: absolute;
    bottom: 8px; left: 80px; right: 80px;
    display: flex;
    justify-content: space-between;
  }}
  .footer span {{
    font-size: 11px; color: #c0c0c8;
  }}
</style>
</head>
<body>

<div class="header">
  <div class="top-row">
    <div class="brand">Now on <strong>{BRAND}</strong></div>
    <div class="category">{cat}</div>
  </div>
  <div class="title">{t}</div>
  <div class="summary-wrap">
    <div class="summary-bar"></div>
    <div class="summary">{summ}</div>
  </div>
</div>

<div class="cards" style="position:relative">{kp_html}
  <div class="footer">
    <span>Now on {BRAND}</span>
    <span>Source: {src}</span>
  </div>
</div>

</body></html>"""


def generate_slide(
    title: str, category: str, source: str, summary: str,
    keypoints: list[str], output_path: Path, size: str = "1536x1024",
) -> bool:
    try:
        from playwright.sync_api import sync_playwright
        from PIL import Image as PILImage

        page_html = _html(title, category, source, summary, keypoints)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": W, "height": H})
            page.set_content(page_html, wait_until="load")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            body = page.query_selector("body")
            body.screenshot(path=str(output_path), type="png")
            browser.close()

        # 正確に 1536x1024 に合わせる
        img = PILImage.open(str(output_path))
        if img.size != (W, H):
            canvas = PILImage.new("RGB", (W, H), (245, 245, 247))
            canvas.paste(img, (0, 0))
            canvas.save(str(output_path), "PNG")

        return True
    except Exception as e:
        print(f"  [slide_maker] error: {e}")
        import traceback; traceback.print_exc()
        return False


if __name__ == "__main__":
    out = Path("/tmp/test_slide_pillow.png")
    ok = generate_slide(
        title="OpenAI、企業向けAI導入子会社「DeployCo」を立ち上げ──40億ドル調達",
        category="業界動向", source="OpenAI Blog",
        summary="OpenAI傘下のDeployCo、企業向けAI導入コンサルを開始。40億ドル超調達、Palantir流現地駐在型展開。Fortune 500企業を中心にパイロット契約を複数獲得済み。",
        keypoints=["巨額投資で設立 TPG主導で40億ドル超調達", "現地駐在型導入 顧客データとAIを統合",
                   "統合が競争力 ワークフロー設計で差別化", "戦略的フィードバック 現場知見をモデル開発へ"],
        output_path=out,
    )
    if ok:
        print(f"Generated: {out}")
        import subprocess; subprocess.run(["open", str(out)])
