"""
記事に icebreak フィールド追加：商談・雑談・SNS発信で「そのまま使える一言」をAI生成。
読者がサイトを開いて「今日この話できる」状態にする。
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
from llm import chat_json, extract_json

ICEBREAK_PROMPT = """以下のAIニュース記事に対して、各記事ごとに「商談・雑談・SNS発信でそのまま使える一言」を icebreak フィールドとして追加してください。

icebreak の構造:
{
  "hook": "話の入り口の一言（50字以内・口語・「〜知ってます？」「〜らしいですよ」など自然な切り出し）",
  "punchline": "その一言で相手の興味を引く本質的な示唆（70字以内・口語・敬語）",
  "ctx_meeting": "商談で使う場面の例（25字以内・例: AI導入提案の冒頭で）",
  "ctx_chat": "雑談で使う場面の例（25字以内・例: ランチ・移動中の会話）",
  "share_text": "X/Threads でそのままシェアできる短文（130字以内・ハッシュタグ無し・絵文字は1つまで・記事URLは付けない）"
}

【重要ルール】
- hook と punchline は「コピペで明日使える」レベルの自然な日本語で
- 数字・固有名詞は記事に書かれているものだけを使い、推測で加えない
- 「最新トレンド」のような抽象語は禁止。具体エピソードに落とす
- share_text は「自分の体験・気づき・問い」の形にする（ニュース引用そのままはNG）
- 全て日本語

入力された各記事の title・lede・keypoints を参考に、icebreak をJSON配列で返してください。
配列の順番は入力と同じにすること。

出力形式:
[
  {"hook": "...", "punchline": "...", "ctx_meeting": "...", "ctx_chat": "...", "share_text": "..."},
  ...
]
"""


def generate_icebreak(articles: list[dict]) -> list[dict]:
    digest_parts = []
    for i, a in enumerate(articles):
        kp = "\n".join(f"  - {k}" for k in a.get("keypoints", []))
        digest_parts.append(
            f"[{i}] {a['title']}\n"
            f"lede: {a.get('lede','')}\n"
            f"keypoints:\n{kp}"
        )
    digest = "\n\n".join(digest_parts)

    text = chat_json(
        system="あなたは日本のビジネスパーソン向けAIメディアの編集者。商談・雑談で使える自然な日本語の一言を作る専門家。",
        user=f"{ICEBREAK_PROMPT}\n\n記事リスト:\n{digest}",
        max_tokens=4500,
    )
    return json.loads(extract_json(text, "array"))


def process_file(path: Path, force: bool = False) -> bool:
    with open(path) as f:
        articles = json.load(f)

    if not force and all("icebreak" in a for a in articles):
        print(f"  SKIP (already done): {path.parent.name}")
        return False

    print(f"  Generating icebreak for {len(articles)} articles in {path.parent.name}...")
    ib_list = generate_icebreak(articles)

    for article, ib in zip(articles, ib_list):
        article["icebreak"] = ib

    with open(path, "w") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"  DONE: {path.parent.name}")
    return True


if __name__ == "__main__":
    base = Path("/Users/yamanakashuto/apps/vigil-news/docs/news")
    if len(sys.argv) > 1:
        target = base / sys.argv[1] / "articles.json"
        process_file(target, force=True)
    else:
        for p in sorted(base.glob("*/articles.json")):
            process_file(p)
