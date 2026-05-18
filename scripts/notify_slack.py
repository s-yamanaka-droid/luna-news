"""
今日のNow on AIr配信内容を Slack #朝刊 に送信。
daily.sh の最後で呼ばれる。
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path.home() / "agents/cmo/x_agent"))
from slack_notifier import send_digest

ROOT = Path(__file__).parent.parent
TARGET = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()

articles_path = ROOT / "docs" / "news" / TARGET / "articles.json"
if not articles_path.exists():
    print(f"[skip] articles.json not found: {articles_path}")
    sys.exit(0)

articles = json.loads(articles_path.read_text(encoding="utf-8"))

# 各記事の link は articles[i]["links"][0] にある
top_articles = []
for a in articles[:5]:
    top_articles.append({
        "source": a.get("source", ""),
        "title": a.get("title", ""),
        "lede": a.get("lede", ""),
        "link": (a.get("links") or [""])[0],
    })

# weekly のトレンド総評があれば使う、なければ簡易メッセージ
weekly_files = sorted((ROOT / "docs" / "weekly").glob("*.json"), reverse=True)
trend = "本日のAIニュースをお届けします。詳細はサイトをご覧ください。"
if weekly_files:
    try:
        trend = json.loads(weekly_files[0].read_text(encoding="utf-8")).get("trend_summary", trend)
    except Exception:
        pass

send_digest(trend, top_articles)
print(f"✓ Slack #朝刊 配信完了 ({TARGET}, {len(top_articles)}件)")
