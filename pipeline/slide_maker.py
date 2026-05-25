"""
Now on REALm — Slide Maker (HTML → PNG レンダ版)
HTMLテンプレに記事データを流し込み、Playwright で 16:9 PNG として保存。
完全無料・日本語文字化けゼロ・スタイル100%統一。
"""
import os
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).parent / "templates"
BRAND_NAME = os.environ.get("NOW_ON_BRAND", "AIr")  # "AIr" or "REALm" etc.
# 1文字目以外（"AI"+"r", "REAL"+"m"）の分割: 末尾1文字を small に
BRAND_MAIN = BRAND_NAME[:-1]
BRAND_SUB = BRAND_NAME[-1]
PRIMARY_COLOR = os.environ.get("NOW_ON_PRIMARY_COLOR", "#CE1141")  # AIr: red

# キーポイントの内容からカテゴリ別アイコンを選ぶ簡易ヒューリスティック
ICON_KEYWORDS = [
    (r"AI|エージェント|GPT|Claude|Codex|Cursor", "🤖"),
    (r"価格|料金|コスト|値上げ|値下げ|円|ドル|円安|赤字", "💰"),
    (r"金利|REIT|投資|利回り|配当", "📈"),
    (r"契約|提携|買収|出資|M&A", "🤝"),
    (r"政策|法律|規制|税|国会|総務省|金融庁|宅建", "⚖️"),
    (r"建設|建築|住宅|新築|工務店|職人|大工", "🏗"),
    (r"物件|マンション|戸建|アパート|賃貸|オフィス|店舗", "🏢"),
    (r"採用|人材|求人|応募|面接|新卒|中途", "👥"),
    (r"クラウド|データ|サーバ|セキュリティ|API|システム", "🔒"),
    (r"スマホ|アプリ|サイト|オンライン|SaaS|プラットフォーム", "📱"),
    (r"環境|脱炭素|ESG|サステナ", "🌱"),
    (r"人口|高齢|世帯|都市|地域|エリア", "🗺"),
    (r"成長|拡大|増加|急増|シェア", "🚀"),
    (r"低下|減少|縮小|撤退", "📉"),
    (r"研究|調査|レポート|統計|分析", "📊"),
    (r"自動|効率|生産性|短縮|高速", "⚡"),
]
DEFAULT_ICONS = ["⭐", "🔍", "💡", "🎯"]


def pick_icon(text: str, fallback_idx: int) -> str:
    for pattern, icon in ICON_KEYWORDS:
        if re.search(pattern, text):
            return icon
    return DEFAULT_ICONS[fallback_idx % len(DEFAULT_ICONS)]


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
    size: str = "2K",  # 互換用、未使用
) -> bool:
    """HTML → PNG レンダリングで 1536x1024 のスライド画像を生成"""
    from playwright.sync_api import sync_playwright

    # 最大4つに絞り、長すぎる文字列はトリム
    kps = [_truncate(k, 40) for k in (keypoints or [])][:4]
    if not kps:
        kps = [_truncate(summary, 40) or _truncate(title, 40)]

    icons = [pick_icon(k, i) for i, k in enumerate(kps)]

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    tmpl = env.get_template("slide.html.j2")
    html = tmpl.render(
        title=_truncate(title, 60),
        category=_truncate(category or "NEWS", 12),
        source=_truncate(source, 28),
        lede=_truncate(summary, 110),
        keypoints=kps,
        icons=icons,
        brand_main=BRAND_MAIN,
        brand_sub=BRAND_SUB,
        primary_color=PRIMARY_COLOR,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1536, "height": 1024}, device_scale_factor=1)
            page = ctx.new_page()
            page.set_content(html, wait_until="networkidle")
            # フォントロード完了待ち（Web Font）
            page.wait_for_timeout(800)
            page.screenshot(path=str(output_path), clip={"x": 0, "y": 0, "width": 1536, "height": 1024})
            browser.close()
        return True
    except Exception as e:
        print(f"  [slide-html] error: {e}")
        return False


if __name__ == "__main__":
    out = Path("/tmp/test_slide_html.png")
    ok = generate_slide(
        title="都心マンション価格、3カ月連続で上昇　港区が牽引",
        category="市況",
        source="楽待新聞",
        summary="2026年5月の中古マンション価格指数が前月比+1.2%。在庫減少と外国人需要が継続。",
        keypoints=[
            "港区平均で坪単価+5%、需給逼迫が顕著",
            "外国人投資家のシェアが過去最高の18%に",
            "金利上昇でも住宅ローン需要は底堅い",
            "REIT指数も連動して年初来高値を更新",
        ],
        output_path=out,
    )
    print(f"生成: {ok} → {out}")
