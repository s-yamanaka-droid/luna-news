"""
Now on AIr の今日の配信を Obsidian vault に同期する。
- ~/vault/3-プロジェクト/NowOnAIr/daily/YYYY-MM-DD.md（その日のニュース詳細）
- ~/vault/3-プロジェクト/NowOnAIr/index.md（全日付テーブル一覧 = ダッシュボード）

daily.sh から毎朝呼ばれる。Obsidianのカラム/ダッシュボードとして即見れる。
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
NEWS_DIR = ROOT / "docs" / "news"
VAULT_DIR = Path.home() / "vault" / "3-プロジェクト" / "NowOnAIr"
DAILY_DIR = VAULT_DIR / "daily"
SITE_URL = "https://s-yamanaka-droid.github.io/nowonair/"

VAULT_DIR.mkdir(parents=True, exist_ok=True)
DAILY_DIR.mkdir(parents=True, exist_ok=True)


def render_daily(target_date: str, articles: list[dict]) -> str:
    """その日のMarkdownを生成"""
    lines = [
        f"# Now on AIr — {target_date}",
        "",
        f"**配信日**: {target_date}",
        f"**記事数**: {len(articles)} 件",
        f"**サイト**: {SITE_URL}news/{target_date}/",
        "",
        "---",
        "",
    ]

    for i, a in enumerate(articles, 1):
        title = a.get("title", "")
        category = a.get("category", "")
        source = a.get("source", "")
        lede = a.get("lede", "")
        link = (a.get("links") or [""])[0]
        img = f"{SITE_URL}assets/images/{target_date}/topic_{i}.png"

        lines += [
            f"## {i:02d}. {title}",
            "",
            f"**カテゴリ**: {category} | **ソース**: [{source}]({link})",
            "",
            f"![]({img})",
            "",
            f"> {lede}",
            "",
        ]

        # keypoints
        kps = a.get("keypoints", [])
        if kps:
            lines.append("### キーポイント")
            for kp in kps:
                lines.append(f"- {kp}")
            lines.append("")

        # bizapp
        bz = a.get("bizapp", {})
        if bz.get("summary"):
            lines += [
                "### 💡 ビジネス活用",
                f"**結論**: {bz['summary']}",
                "",
            ]
            for act in bz.get("actions", []):
                lines.append(f"- {act}")
            lines.append("")

        # quickstart
        qs = a.get("quickstart", {})
        if qs.get("headline"):
            lines += [
                "### ⚡ 明日からできる（個人事業主向け）",
                f"**{qs['headline']}**",
                "",
                f"- **推奨ツール**: [{qs.get('tool', {}).get('name', '')}]({qs.get('tool', {}).get('url', '')}) ({qs.get('tool', {}).get('cost', '')})",
                f"- **所要時間**: {qs.get('time', '')}",
                f"- **想定効果**: {qs.get('roi', '')}",
                "",
                "**3ステップ**:",
            ]
            for step in qs.get("steps", []):
                lines.append(f"1. {step}")
            lines.append("")
            if qs.get("prompt"):
                lines += [
                    "**コピペプロンプト**:",
                    "```",
                    qs["prompt"],
                    "```",
                    "",
                ]

        lines += ["---", ""]

    return "\n".join(lines)


def update_index():
    """全日付のサマリーテーブル（Obsidianのカラム/ダッシュボード）"""
    daily_files = sorted(DAILY_DIR.glob("*.md"), reverse=True)

    lines = [
        "# Now on AIr — ダッシュボード",
        "",
        f"**全 {len(daily_files)} 日分の配信履歴**",
        f"🔗 [サイト]({SITE_URL}) · [週次ダイジェスト]({SITE_URL}weekly.html) · [事例集]({SITE_URL}cases.html)",
        "",
        "---",
        "",
        "## 配信履歴",
        "",
        "| 日付 | 記事数 | TOP記事 | 詳細 |",
        "|---|---|---|---|",
    ]

    for f in daily_files:
        d = f.stem
        # 記事数とTOP記事を articles.json から取得
        articles_path = NEWS_DIR / d / "articles.json"
        n = "-"
        top_title = "-"
        if articles_path.exists():
            try:
                arts = json.loads(articles_path.read_text(encoding="utf-8"))
                n = str(len(arts))
                top_title = arts[0].get("title", "-")[:40] if arts else "-"
            except Exception:
                pass
        lines.append(f"| {d} | {n} | {top_title} | [[daily/{d}\\|開く]] |")

    return "\n".join(lines)


def sync(target_date: str | None = None):
    target_date = target_date or date.today().isoformat()
    articles_path = NEWS_DIR / target_date / "articles.json"
    if not articles_path.exists():
        print(f"[skip] {articles_path} なし")
        return

    articles = json.loads(articles_path.read_text(encoding="utf-8"))

    # 今日の詳細MD
    md = render_daily(target_date, articles)
    daily_path = DAILY_DIR / f"{target_date}.md"
    daily_path.write_text(md, encoding="utf-8")
    print(f"✓ Daily MD: {daily_path}")

    # ダッシュボード更新
    index_md = update_index()
    index_path = VAULT_DIR / "index.md"
    index_path.write_text(index_md, encoding="utf-8")
    print(f"✓ Index MD: {index_path}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    sync(target)
