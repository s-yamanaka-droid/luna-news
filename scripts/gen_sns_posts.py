"""
SNS投稿テキスト生成（X / Threads / Instagram）
今日のTOP記事から、各プラットフォーム最適化された投稿を生成。
画像はpublic GitHub Pages URLを使用。

出力：docs/news/YYYY-MM-DD/sns_posts.json
"""
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
import anthropic

ROOT = Path(__file__).parent.parent
NEWS_DIR = ROOT / "docs" / "news"
SITE_URL = "https://nowonair.vercel.app/"

PROMPT = """以下のAIニュースから、3つのSNS（X / Threads / Instagram）向けに最適化された投稿テキストを作成してください。

【記事】
タイトル: {title}
カテゴリ: {category}
ソース: {source}
要約: {lede}
キーポイント:
{keypoints}
明日からできる: {qs_headline}
推奨ツール: {qs_tool}

【プラットフォーム別ルール】

■ X (Twitter) — 250字以内
- 結論ファーストで掴む
- 「AI×個人事業主」目線で価値を1行
- 改行で読みやすく
- 末尾に詳細URL + ハッシュタグ3つ程度
- 絵文字は冒頭1〜2個

■ Threads — 450字以内
- Xより会話的・カジュアルに
- 個人的な気づきや問いかけを混ぜる
- 段落を区切って読みやすく
- 末尾に詳細URL
- ハッシュタグは最後にまとめて2〜3個

■ Instagram — 800字以内
- 画像があってこそ映えるキャプション前提
- 1行目はインパクト重視
- 中盤に価値の説明・想定読者
- ハッシュタグは末尾に大量（10〜15個）#AI #AIニュース #起業家 #フリーランス #個人事業主 など

【全プラットフォーム共通】
- 読み手は「個人事業主・1〜10人規模の小さな会社の社長」
- 抽象論NG。具体的な活用例・ツール名・数字を入れる
- 詳細URL: {detail_url}

【出力JSON】
{{
  "x": "X投稿テキスト全文",
  "threads": "Threads投稿テキスト全文",
  "instagram": "Instagram投稿テキスト全文"
}}
"""


def generate_sns_posts(article: dict, detail_url: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    qs = article.get("quickstart", {})
    qs_headline = qs.get("headline", "") if qs else ""
    qs_tool = (qs.get("tool", {}) or {}).get("name", "") if qs else ""

    kp = "\n".join(f"  - {k}" for k in article.get("keypoints", [])[:4])

    prompt = PROMPT.format(
        title=article.get("title", ""),
        category=article.get("category", ""),
        source=article.get("source", ""),
        lede=article.get("lede", ""),
        keypoints=kp,
        qs_headline=qs_headline,
        qs_tool=qs_tool,
        detail_url=detail_url,
    )

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text.strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    raw = re.sub(r",\s*([}\]])", r"\1", text[start:end])
    return json.loads(raw)


if __name__ == "__main__":
    target_date = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    articles_path = NEWS_DIR / target_date / "articles.json"
    if not articles_path.exists():
        sys.exit(f"記事なし: {articles_path}")

    articles = json.loads(articles_path.read_text(encoding="utf-8"))
    top = articles[0]
    detail_url = f"{SITE_URL}news/{target_date}/#topic-1"
    image_url = f"{SITE_URL}assets/images/{target_date}/topic_1.png"

    print(f"[{target_date}] Generating SNS posts for top article...")
    print(f"  Title: {top['title']}")

    posts = generate_sns_posts(top, detail_url)
    posts["_meta"] = {
        "date": target_date,
        "source_article_index": 0,
        "image_url": image_url,
        "detail_url": detail_url,
        "title": top.get("title", ""),
    }

    out_path = NEWS_DIR / target_date / "sns_posts.json"
    out_path.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Saved: {out_path}")
    print()
    for plat in ["x", "threads", "instagram"]:
        print(f"=== {plat.upper()} ({len(posts[plat])}字) ===")
        print(posts[plat])
        print()
