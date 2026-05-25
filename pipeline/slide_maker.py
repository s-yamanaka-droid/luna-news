"""
Now on REALm — Slide Maker (HTML → PNG レンダ版 v2)
Lucide風SVGアイコン・magazine editorialデザイン・日本語完璧。
"""
import os
import re
from datetime import date
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).parent / "templates"
BRAND_NAME = os.environ.get("NOW_ON_BRAND", "AIr")
BRAND_MAIN = BRAND_NAME[:-1]
BRAND_SUB = BRAND_NAME[-1]
PRIMARY_COLOR = os.environ.get("NOW_ON_PRIMARY_COLOR", "#CE1141")

# ── Lucide風 SVGアイコン辞書 ──
ICONS = {
    "ai":         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="10" r="1.5"/><circle cx="15" cy="10" r="1.5"/><path d="M8 15h8"/></svg>',
    "money":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "chart-up":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "chart-down": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>',
    "handshake":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 17l-5-5 5-5"/><path d="M13 7l5 5-5 5"/><path d="M9 12h6"/></svg>',
    "scale":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><path d="M5 8l-3 6h6z"/><path d="M19 8l-3 6h6z"/><path d="M3 20h18"/></svg>',
    "building":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="8" y2="6"/><line x1="12" y1="6" x2="12" y2="6"/><line x1="16" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="8" y2="10"/><line x1="12" y1="10" x2="12" y2="10"/><line x1="16" y1="10" x2="16" y2="10"/><line x1="8" y1="14" x2="8" y2="14"/><line x1="12" y1="14" x2="12" y2="14"/><line x1="16" y1="14" x2="16" y2="14"/><path d="M10 22v-4h4v4"/></svg>',
    "home":       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "construct":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/><line x1="12" y1="11" x2="12" y2="17"/></svg>',
    "users":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "shield":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "cloud":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>',
    "smartphone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12" y2="18"/></svg>',
    "leaf":       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19.2 2.96a1 1 0 0 1 1.8.61 17 17 0 0 1-3.9 12.43C13.4 19.1 8 21 5 21"/><path d="M2 21c0-3 1.85-5.36 5.08-6"/></svg>',
    "map":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>',
    "rocket":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>',
    "search":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "zap":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "bulb":       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12c1 1 2 2 2 4h4c0-2 1-3 2-4a7 7 0 0 0-4-12z"/></svg>',
    "target":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "globe":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "calendar":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
}

ICON_KEYWORDS = [
    (r"AI|エージェント|GPT|Claude|Codex|Cursor|LLM", "ai"),
    (r"建設|建築|新築|工務店|職人|大工|設備|施工", "construct"),
    (r"物件|マンション|戸建|アパート|賃貸|オフィス|店舗|住宅", "building"),
    (r"家|ハウス|住み|居住|引越し", "home"),
    (r"金利|REIT|投資|利回り|配当|証券|株", "chart-up"),
    (r"低下|減少|縮小|撤退|下落|赤字", "chart-down"),
    (r"価格|料金|コスト|値上げ|値下げ|円|ドル|円安|高騰", "money"),
    (r"契約|提携|買収|出資|M&A|合意|協業", "handshake"),
    (r"政策|法律|規制|税|国会|金融庁|宅建|条例", "scale"),
    (r"採用|人材|求人|応募|面接|新卒|中途|労働|職員", "users"),
    (r"防犯|セキュリティ|安全|警備|施錠|盗難", "shield"),
    (r"クラウド|データ|サーバ|API|システム|オンライン|SaaS", "cloud"),
    (r"スマホ|アプリ|モバイル|デジタル", "smartphone"),
    (r"環境|脱炭素|ESG|サステナ|再生|エネルギー", "leaf"),
    (r"人口|高齢|世帯|都市|地域|エリア|地方|圏", "map"),
    (r"成長|拡大|増加|急増|シェア|拡張|展開|採用", "rocket"),
    (r"研究|調査|レポート|統計|分析|データ", "search"),
    (r"自動|効率|生産性|短縮|高速|スピード", "zap"),
    (r"アイデア|提案|新しい|ヒント|戦略", "bulb"),
    (r"目標|狙い|集客|顧客|ターゲット", "target"),
    (r"海外|グローバル|国際|世界|外国", "globe"),
    (r"年|月|日|期間|スケジュール|時期", "calendar"),
]
DEFAULT_ROTATION = ["bulb", "target", "search", "zap", "rocket", "globe"]


def pick_icon(text: str) -> str:
    for pattern, key in ICON_KEYWORDS:
        if re.search(pattern, text):
            return key
    return ""


def pick_icons(keypoints: list[str]) -> list[str]:
    """重複排除しながら4つ選ぶ"""
    picked = []
    used = set()
    for kp in keypoints:
        key = pick_icon(kp)
        if key and key not in used:
            picked.append(key)
            used.add(key)
        else:
            picked.append(None)  # 後で埋める
    # 埋め
    rotation = [k for k in DEFAULT_ROTATION if k not in used]
    for i, k in enumerate(picked):
        if k is None:
            if rotation:
                picked[i] = rotation.pop(0)
                used.add(picked[i])
            else:
                picked[i] = DEFAULT_ROTATION[i % len(DEFAULT_ROTATION)]
    return [ICONS.get(k, ICONS["bulb"]) for k in picked]


def _truncate(s: str, n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[:n-1] + "…"


def generate_slide(
    title: str,
    category: str,
    source: str,
    summary: str,
    keypoints: list[str],
    output_path: Path,
    size: str = "2K",
) -> bool:
    from playwright.sync_api import sync_playwright

    kps = [_truncate(k, 38) for k in (keypoints or [])][:4]
    if not kps:
        kps = [_truncate(summary, 38) or _truncate(title, 38)]

    icons = pick_icons(kps)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    tmpl = env.get_template("slide.html.j2")
    html = tmpl.render(
        title=_truncate(title, 55),
        category=_truncate(category or "NEWS", 12),
        source=_truncate(source, 28),
        lede=_truncate(summary, 110),
        keypoints=kps,
        icons=icons,
        brand_main=BRAND_MAIN,
        brand_sub=BRAND_SUB,
        primary_color=PRIMARY_COLOR,
        today=date.today().strftime("%Y.%m.%d"),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1536, "height": 1024}, device_scale_factor=1)
            page = ctx.new_page()
            page.set_content(html, wait_until="networkidle")
            page.wait_for_timeout(800)
            page.screenshot(path=str(output_path), clip={"x": 0, "y": 0, "width": 1536, "height": 1024})
            browser.close()
        return True
    except Exception as e:
        print(f"  [slide-html] error: {e}")
        return False


if __name__ == "__main__":
    out = Path("/tmp/test_slide_v2.png")
    ok = generate_slide(
        title="OpenAI、Gartnerが評価する企業向けコーディングエージェントのリーダーに",
        category="業界動向",
        source="OpenAI Blog",
        summary="OpenAIは、Gartnerの2026年企業向けAIコーディングエージェントのマジック・クアドラントにて、リーダーに選出されました。",
        keypoints=[
            "Codexが企業での利用拡大を実現",
            "週に400万人以上がCodexを使用",
            "GPT-5.5で生産性向上",
            "企業ソフトウェア開発の強化",
        ],
        output_path=out,
    )
    print(f"生成: {ok} → {out}")
