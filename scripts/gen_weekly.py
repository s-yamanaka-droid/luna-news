"""
週次ダイジェスト生成
過去7日のarticles.jsonから「個人事業主・社長が絶対押さえるべき3本」をClaudeに選ばせる。
docs/weekly/YYYY-MM-DD.json と docs/weekly.html を出力。
"""
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
from llm import chat_json, extract_json

ROOT = Path(__file__).parent.parent
NEWS_DIR = ROOT / "docs" / "news"
WEEKLY_DIR = ROOT / "docs" / "weekly"
WEEKLY_DIR.mkdir(parents=True, exist_ok=True)

DIGEST_PROMPT = """以下は過去7日のAIニュース一覧です。
個人事業主・1〜10人規模の小さな会社の社長が「今週これだけ押さえれば十分」というTOP 3を選んでください。

選定基準：
1. 明日から自社で試せる即実行性が高い
2. 大企業向けの抽象論ではなく、小規模事業者にも恩恵がある
3. お金になる・時間が浮く・差別化になる

各記事に対して以下のJSONを返してください：

{
  "rank": 1,
  "date": "YYYY-MM-DD",
  "title": "元のタイトル",
  "category": "元のカテゴリ",
  "source": "元のソース",
  "why_picked": "なぜTOP 3に選んだか（40字以内・個人事業主目線）",
  "tldr": "30字以内の超要約",
  "action": "今週中にやるべき1アクション（30字以内）",
  "image": "../assets/images/YYYY-MM-DD/topic_N.png",
  "link": "../news/YYYY-MM-DD/#topic-N"
}

加えて、週全体の「今週のトレンド総評」を3文（180字以内）で書いてください。

出力JSON:
{
  "trend_summary": "...",
  "top3": [{...}, {...}, {...}]
}
"""


def collect_recent_articles(days: int = 7) -> list[dict]:
    """直近days日の記事を全部集める"""
    today = date.today()
    items = []
    for offset in range(days):
        d = today - timedelta(days=offset)
        path = NEWS_DIR / d.isoformat() / "articles.json"
        if not path.exists():
            continue
        articles = json.loads(path.read_text(encoding="utf-8"))
        for i, a in enumerate(articles, 1):
            items.append({
                "date": d.isoformat(),
                "topic_n": i,
                "title": a.get("title", ""),
                "category": a.get("category", ""),
                "source": a.get("source", ""),
                "lede": a.get("lede", ""),
                "keypoints": a.get("keypoints", []),
                "bizapp": a.get("bizapp", {}),
                "quickstart": a.get("quickstart", {}),
            })
    return items


def pick_top3(items: list[dict]) -> dict:
    digest_parts = []
    for it in items:
        kp = "; ".join(it["keypoints"][:3])
        bz = it["bizapp"].get("summary", "") if it["bizapp"] else ""
        qs = it["quickstart"].get("headline", "") if it["quickstart"] else ""
        digest_parts.append(
            f"[{it['date']} #{it['topic_n']}] {it['title']}\n"
            f"  category: {it['category']} | source: {it['source']}\n"
            f"  lede: {it['lede']}\n"
            f"  keypoints: {kp}\n"
            f"  bizapp: {bz}\n"
            f"  quickstart: {qs}"
        )
    digest = "\n\n".join(digest_parts)

    text = chat_json(
        system="あなたは日本のAI活用コンサルタントです。指示に従って厳密にJSONを返してください。",
        user=f"{DIGEST_PROMPT}\n\n記事:\n{digest}",
        max_tokens=2500,
    )
    return json.loads(extract_json(text, "object"))


def render_html(week_start: str, week_end: str, digest: dict) -> str:
    top3 = digest.get("top3", [])
    cards_html = ""
    for item in top3:
        rank = item.get("rank", "")
        date_str = item.get("date", "")
        title = item.get("title", "")
        category = item.get("category", "")
        source = item.get("source", "")
        why = item.get("why_picked", "")
        tldr = item.get("tldr", "")
        action = item.get("action", "")
        image = item.get("image", "")
        link = item.get("link", "")

        cards_html += f"""
  <div class="weekly-card">
    <div class="rank">RANK 0{rank}</div>
    <a href="{link}" class="weekly-img-link">
      <img src="{image}" alt="{title}" loading="lazy" />
    </a>
    <div class="weekly-meta">
      <span class="cat">{category}</span>
      <span class="date">{date_str}</span>
      <span class="src">{source}</span>
    </div>
    <h2 class="weekly-title">{title}</h2>
    <p class="weekly-tldr">{tldr}</p>
    <div class="weekly-why">
      <span class="why-label">なぜTOP {rank}？</span> {why}
    </div>
    <div class="weekly-action">
      <span class="action-label">⚡ 今週やる</span> {action}
    </div>
    <a href="{link}" class="weekly-cta">記事を読む →</a>
  </div>"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>今週のAI3本 — Now on AIr Weekly</title>
<meta name="description" content="今週のAIニュースから、個人事業主・社長が絶対押さえるべき3本だけ。">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="./assets/vigil.css?v4">
<style>
.weekly-hero{{padding:60px 32px 40px;border-bottom:4px solid var(--red);}}
.weekly-hero h1{{font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:64px;line-height:.95;margin:0 0 12px;letter-spacing:-.02em;}}
.weekly-hero h1 em{{color:var(--red);font-style:normal;}}
.weekly-hero .sub{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--mute);margin-bottom:20px;}}
.weekly-hero .summary{{font-family:'Noto Serif JP',serif;font-size:16px;line-height:1.85;color:var(--ink-2);max-width:780px;}}
.weekly-grid{{padding:48px 32px 80px;display:grid;gap:32px;max-width:1200px;margin:0 auto;}}
.weekly-card{{border:1px solid var(--rule-2);padding:24px;background:var(--paper);transition:border-color .2s,box-shadow .2s,transform .18s;}}
.weekly-card:hover{{border-color:var(--red);box-shadow:6px 6px 0 var(--red);transform:translate(-3px,-3px);}}
.weekly-card .rank{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.2em;color:#fff;background:var(--red);display:inline-block;padding:5px 12px;font-weight:800;margin-bottom:14px;}}
.weekly-img-link{{display:block;border:1px solid var(--rule-2);overflow:hidden;cursor:zoom-in;margin-bottom:14px;}}
.weekly-img-link img{{width:100%;display:block;}}
.weekly-meta{{display:flex;gap:14px;font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--mute);margin-bottom:10px;}}
.weekly-meta .cat{{color:var(--red);font-weight:700;}}
.weekly-title{{font-family:'Barlow Condensed','Noto Sans JP',sans-serif;font-weight:900;font-size:28px;line-height:1.2;margin:0 0 12px;}}
.weekly-tldr{{font-family:'Noto Serif JP',serif;font-size:14px;line-height:1.7;color:var(--ink-2);margin:0 0 16px;}}
.weekly-why,.weekly-action{{font-size:13px;line-height:1.7;padding:10px 14px;margin-bottom:8px;}}
.weekly-why{{background:#FFF8E5;border-left:4px solid #FF9800;}}
.weekly-action{{background:#FFEBEE;border-left:4px solid var(--red);}}
.why-label,.action-label{{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.15em;text-transform:uppercase;font-weight:800;margin-right:6px;}}
.why-label{{color:#E65100;}}
.action-label{{color:var(--red);}}
.weekly-cta{{display:inline-block;margin-top:14px;font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.1em;font-weight:700;color:#fff;background:var(--ink);padding:10px 22px;text-decoration:none;transition:background .15s;}}
.weekly-cta:hover{{background:var(--red);}}
@media (min-width:900px){{.weekly-grid{{grid-template-columns:1fr 1fr 1fr;}}}}
</style>
</head>
<body>
<nav class="main">
  <div class="brand"><em class="dot-r">●</em>Now on <em class="brand-ai">AI</em><span class="brand-r">r</span></div>
  <ul>
    <li><a href="./">TODAY</a></li>
    <li><a href="./weekly.html" class="active">WEEKLY</a></li>
    <li><a href="./cases.html">CASES</a></li>
    <li><a href="./#about">ABOUT</a></li>
  </ul>
</nav>

<div class="weekly-hero">
  <div class="sub">WEEKLY DIGEST · {week_start} → {week_end}</div>
  <h1>今週の<em>AI 3本</em></h1>
  <p class="summary">{digest.get('trend_summary','')}</p>
</div>

<div class="weekly-grid">
{cards_html}
</div>

<div style="text-align:center;padding:40px 32px 80px;border-top:1px solid var(--rule-2);">
  <p style="font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.15em;color:var(--mute);text-transform:uppercase;">毎週月曜更新 · 個人事業主・社長のためのAI週報</p>
  <a href="./" style="display:inline-block;margin-top:12px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--red);font-weight:700;letter-spacing:.1em;">← 毎日のAIニュースに戻る</a>
</div>

</body>
</html>
"""


if __name__ == "__main__":
    today = date.today()
    week_start = (today - timedelta(days=6)).isoformat()
    week_end = today.isoformat()

    print(f"Collecting articles {week_start} → {week_end}...")
    items = collect_recent_articles(days=7)
    print(f"  Total: {len(items)} articles")

    print("Picking TOP 3 with Claude...")
    digest = pick_top3(items)

    # JSONとHTML保存
    json_path = WEEKLY_DIR / f"{week_end}.json"
    json_path.write_text(json.dumps(digest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON: {json_path}")

    html = render_html(week_start, week_end, digest)
    html_path = ROOT / "docs" / "weekly.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"  HTML: {html_path}")

    # アーカイブ用も保存
    archive_path = WEEKLY_DIR / f"{week_end}.html"
    archive_path.write_text(html, encoding="utf-8")
    print(f"  Archive: {archive_path}")

    print("Done.")
