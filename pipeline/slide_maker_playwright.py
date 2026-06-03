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

# Lucide風 SVGアイコン（stroke=currentColor で色追従）
ICONS = {
    "ai":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="10" r="1.5"/><circle cx="15" cy="10" r="1.5"/><path d="M8 15h8"/></svg>',
    "robot":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>',
    "shield":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>',
    "network":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M12 7l-7 12M12 7l7 12"/></svg>',
    "chart":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="20" x2="20" y2="20"/><rect x="6" y="11" width="3" height="9"/><rect x="11" y="6" width="3" height="14"/><rect x="16" y="14" width="3" height="6"/></svg>',
    "money":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="22"/><path d="M17 6H9a3 3 0 0 0 0 6h6a3 3 0 0 1 0 6H6"/></svg>',
    "handshake": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 17l-5-5 5-5M13 7l5 5-5 5M9 12h6"/></svg>',
    "lock":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    "cloud":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>',
    "device":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12" y2="18"/></svg>',
    "users":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "rocket":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09zM12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2zM9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>',
    "search":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "bolt":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "bulb":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12c1 1 2 2 2 4h4c0-2 1-3 2-4a7 7 0 0 0-4-12z"/></svg>',
    "target":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "globe":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "settings":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3h0a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5h0a1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8v0a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>',
    "document":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/></svg>',
    "calendar":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "leaf":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19.2 2.96a1 1 0 0 1 1.8.61 17 17 0 0 1-3.9 12.43C13.4 19.1 8 21 5 21M2 21c0-3 1.85-5.36 5.08-6"/></svg>',
    "building":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/></svg>',
}

# キーワードマッチ（記事/keypoint テキスト → 適切なアイコン）
ICON_KEYWORDS = [
    (r"AI|エージェント|GPT|Claude|Codex|Cursor|Copilot|LLM|モデル", "ai"),
    (r"自動|自律|代行|アシスタント|スカウト|ボット", "robot"),
    (r"セキュリティ|安全|保護|防御|脅威|権限|プライバシー", "shield"),
    (r"統合|連携|API|プラットフォーム|エコシステム|接続|ネットワーク", "network"),
    (r"成長|拡大|増加|急増|シェア|分析|統計|データ|グラフ|指標", "chart"),
    (r"資金|調達|投資|億ドル|億円|料金|価格|コスト|月額", "money"),
    (r"提携|契約|合意|協業|パートナーシップ|買収|M&A", "handshake"),
    (r"認証|暗号|鍵|ロック|施錠|プライベート|機密", "lock"),
    (r"クラウド|SaaS|オンライン|Web|サーバ", "cloud"),
    (r"スマホ|モバイル|アプリ|デバイス|端末|iPhone|Android", "device"),
    (r"採用|人材|チーム|ユーザー|顧客|従業員|社員|労働", "users"),
    (r"発表|登場|ローンチ|公開|リリース|展開|始動", "rocket"),
    (r"研究|調査|分析|発見|論文|レポート", "search"),
    (r"高速|効率|生産性|短縮|スピード|加速|パフォーマンス", "bolt"),
    (r"新機能|新サービス|新製品|新規|ヒント|アイデア|戦略|提案", "bulb"),
    (r"目標|狙い|集客|ターゲット|マーケティング", "target"),
    (r"海外|グローバル|国際|世界|外国|多言語", "globe"),
    (r"設定|構成|管理|運用|ワークフロー|プロセス", "settings"),
    (r"資料|文書|書類|記事|レポート|プレゼン|ドキュメント", "document"),
    (r"会議|スケジュール|予定|期間|時間|日|月|年", "calendar"),
    (r"環境|エコ|サステナ|脱炭素|再生|エネルギー", "leaf"),
    (r"企業|ビジネス|オフィス|建物|本社|拠点", "building"),
]
DEFAULT_ICONS = ["bulb", "rocket", "chart", "bolt", "target", "globe"]


def _pick_icons(keypoints: list[str]) -> list[str]:
    """重複しない4アイコンを選ぶ"""
    import re
    picked = []
    used = set()
    for kp in keypoints[:4]:
        match = None
        for pattern, key in ICON_KEYWORDS:
            if re.search(pattern, kp):
                if key not in used:
                    match = key; used.add(key); break
        picked.append(match)
    # 未割当を default で補完
    rotation = [k for k in DEFAULT_ICONS if k not in used]
    for i, k in enumerate(picked):
        if k is None:
            if rotation:
                picked[i] = rotation.pop(0); used.add(picked[i])
            else:
                picked[i] = DEFAULT_ICONS[i % len(DEFAULT_ICONS)]
    return picked


def _html(title: str, category: str, source: str, summary: str,
          keypoints: list[str]) -> str:
    t = html.escape(title)
    cat = html.escape(category or "AI")
    src = html.escape(source or "")
    summ = html.escape(summary or "")
    kps = (keypoints or ["—"])[:4]
    icons = _pick_icons(kps)

    kp_html = ""
    for i, kp in enumerate(kps):
        parts = kp.split(None, 1) if len(kp) > 6 else [kp]
        kp_t = html.escape(parts[0])
        kp_d = html.escape(parts[1]) if len(parts) > 1 else ""
        c = CARD_COLORS[i % len(CARD_COLORS)]
        ic = ICONS.get(icons[i], ICONS["bulb"])
        kp_html += f"""
        <div class="card" style="--c:{c}">
          <div class="card-num" style="color:{c}">{i+1:02d}</div>
          <div class="card-icon" style="color:{c}">{ic}</div>
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

  .card-icon {{
    width: 48px;
    height: 48px;
    margin-bottom: 14px;
  }}
  .card-icon svg {{ width: 100%; height: 100%; display: block; }}

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
