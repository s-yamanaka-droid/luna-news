"""今日の Now on AIr を Slack #朝刊へ冪等に配信する。"""

import hashlib
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).parent.parent
CHANNEL = os.environ.get("SLACK_DAILY_CHANNEL", "C0B3M8YB1B9")
MENTION = "<@U0A5ALYDKMZ>"
SITE_URL = os.environ.get("NOW_ON_AIR_SITE_URL", "https://nowonair.vercel.app")


def load_digest(target: str) -> tuple[Path, str, list[dict]]:
    articles_path = ROOT / "docs" / "news" / target / "articles.json"
    if not articles_path.exists():
        raise FileNotFoundError(f"articles.json not found: {articles_path}")

    articles = json.loads(articles_path.read_text(encoding="utf-8"))
    top_articles = [
        {
            "source": article.get("source", ""),
            "title": article.get("title", ""),
            "lede": article.get("lede", ""),
            "link": (article.get("links") or [""])[0],
        }
        for article in articles[:5]
    ]

    trend = "本日のAIニュースをお届けします。詳細はサイトをご覧ください。"
    weekly_files = sorted((ROOT / "docs" / "weekly").glob("*.json"), reverse=True)
    if weekly_files:
        try:
            trend = json.loads(weekly_files[0].read_text(encoding="utf-8")).get(
                "trend_summary", trend
            )
        except (OSError, json.JSONDecodeError):
            pass
    return articles_path, trend, top_articles


def build_payload(target: str, trend: str, articles: list[dict]) -> dict:
    lines = []
    for index, article in enumerate(articles[:5], 1):
        title = article.get("title", "")[:80]
        source = article.get("source", "")
        lede = article.get("lede", "")[:120]
        link = article.get("link", "")
        line = f"{index}. *[{source}]* {title}"
        if lede:
            line += f"\n    _{lede}_"
        if link:
            line += f"\n    <{link}|元記事を読む>"
        lines.append(line)

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"Now on AIr — {target}"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{MENTION} 本日のAIニュースです。",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*今日のトレンド*\n{trend}"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Top 5*\n\n{'\n\n'.join(lines)}",
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"<{SITE_URL}/news/{target}/|本日の全記事を見る>",
                }
            ],
        },
    ]
    return {"channel": CHANNEL, "text": f"Now on AIr — {target}", "blocks": blocks}


def send_digest(target: str, session=requests) -> dict:
    token = os.environ.get("SLACK_TOKEN") or os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise RuntimeError("SLACK_TOKEN が未設定です")

    articles_path, trend, articles = load_digest(target)
    content_hash = hashlib.sha256(articles_path.read_bytes()).hexdigest()
    receipt_path = ROOT / "logs" / f"delivery_{target}.json"
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("content_sha256") == content_hash and receipt.get("ts"):
            return {**receipt, "already_delivered": True}

    response = session.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=build_payload(target, trend, articles),
        timeout=20,
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("ok") or not result.get("ts"):
        raise RuntimeError(f"Slack API error: {result.get('error', 'missing_message_ts')}")

    receipt = {
        "target": target,
        "channel": result.get("channel", CHANNEL),
        "ts": result["ts"],
        "content_sha256": content_hash,
        "delivered_at": datetime.now(timezone.utc).isoformat(),
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = receipt_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(receipt_path)
    return receipt


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    try:
        result = send_digest(target)
    except Exception as exc:
        print(f"Slack #朝刊 配信失敗 ({target}): {exc}", file=sys.stderr)
        return 1
    state = "配信済み確認" if result.get("already_delivered") else "配信完了"
    print(f"✓ Slack #朝刊 {state} ({target}, channel={result['channel']}, ts={result['ts']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
