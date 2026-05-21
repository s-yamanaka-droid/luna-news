"""
記事に quickstart フィールドを追加。
個人事業主・社長が「明日からできる3ステップ＋プロンプト＋ツール＋コスト」を持てるようにする。
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
from llm import chat_json, extract_json

QUICKSTART_PROMPT = """以下のAIニュース記事リストに対して、各記事に「個人事業主・小さな会社の社長が明日から自社で試せるアクション」を quickstart フィールドとして追加してください。

quickstart の構造:
{
  "headline": "明日から自社でこう使える、を15字以内で（例: 営業資料の初稿作成を10分に）",
  "tool": {
    "name": "推奨ツール名（例: ChatGPT Plus / Claude Pro / Gemini / Cursor / Notion AI など実在ツール）",
    "url": "公式URL（例: https://claude.ai）",
    "cost": "月額目安（例: 無料 / ¥3,000/月 / ¥3,200/月）"
  },
  "time": "試すのにかかる時間（例: 10分 / 30分 / 半日）",
  "steps": [
    "ステップ1：何をするか（25字以内・命令形）",
    "ステップ2：何をするか（25字以内・命令形）",
    "ステップ3：何をするか（25字以内・命令形）"
  ],
  "prompt": "コピペで即使えるClaude/ChatGPTプロンプト本体（150字以内・「あなたは〜」から始まり、{自社名}{業種}など差し替え変数を{}付きで含める）",
  "roi": "想定効果（例: 月10時間削減＝3万円相当 / 提案書作成を70%短縮）"
}

【重要ルール】
- 対象は「1人〜10人の小さな会社の社長・個人事業主」
- 大企業向けの抽象論ではなく、明日からPCを開いて試せる具体性
- prompt は本当にコピペするだけで動くもの。{業種}{自社名}{課題}など差し替え変数は必ず{}で明示
- tool.url は実在の公式URLのみ（推測禁止・知らないものは https://claude.ai 等の代表的なものに）
- ニュース内容と無関係に汎用的な提案にしない。記事の本質を活かす
- 全て日本語

入力の各記事の title・lede・keypoints・bizapp を参考に、JSON配列で返してください。順番は入力と同じ。

出力形式:
[
  {"headline": "...", "tool": {...}, "time": "...", "steps": [...], "prompt": "...", "roi": "..."},
  ...
]
"""


def generate_quickstart(articles: list[dict]) -> list[dict]:
    digest_parts = []
    for i, a in enumerate(articles):
        kp = "\n".join(f"  - {k}" for k in a.get("keypoints", []))
        bz = a.get("bizapp", {})
        bz_text = ""
        if bz:
            bz_text = f"bizapp.summary: {bz.get('summary','')}\nbizapp.actions: {bz.get('actions',[])}"
        digest_parts.append(
            f"[{i}] {a['title']}\n"
            f"lede: {a.get('lede','')}\n"
            f"keypoints:\n{kp}\n"
            f"{bz_text}"
        )
    digest = "\n\n".join(digest_parts)

    text = chat_json(
        system="あなたは日本のAI活用コンサルタントです。指示に従って厳密にJSONを返してください。",
        user=f"{QUICKSTART_PROMPT}\n\n記事リスト:\n{digest}",
        max_tokens=4500,
    )
    return json.loads(extract_json(text, "array"))


def process_file(path: Path, force: bool = False) -> bool:
    with open(path) as f:
        articles = json.load(f)

    if not force and all("quickstart" in a for a in articles):
        print(f"  SKIP (already done): {path.parent.name}")
        return False

    print(f"  Generating quickstart for {len(articles)} articles in {path.parent.name}...")
    qs_list = generate_quickstart(articles)

    for article, qs in zip(articles, qs_list):
        article["quickstart"] = qs

    with open(path, "w") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"  DONE: {path.parent.name}")
    return True


if __name__ == "__main__":
    import sys
    base = Path("/Users/yamanakashuto/apps/vigil-news/docs/news")

    if len(sys.argv) > 1:
        # 単一日付指定
        target = base / sys.argv[1] / "articles.json"
        process_file(target, force=True)
    else:
        # 全件
        for p in sorted(base.glob("*/articles.json")):
            process_file(p)
