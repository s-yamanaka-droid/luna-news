"""
既存の articles.json に bizapp フィールドを追加するスクリプト
"""
import json
import os
import anthropic
from pathlib import Path

BIZAPP_PROMPT = """以下の記事リストに対して、各記事にビジネス活用ポイント（bizapp）を追加してください。

bizappの構造:
{
  "summary": "このニュースをビジネスでどう使うか（60字以内・結論から）",
  "actions": [
    "社内活用例：Claude（AIアシスタント）・Cursor（AI搭載コードエディタ）・Codex（AIコーディングエージェント）など実在ツールを具体的に絡めた実践アクション（30字以内）",
    "他社提案例：採用・営業・中小企業DX・バックオフィス自動化など現場目線の提案（30字以内）",
    "注目理由：競合が動いている・コストが下がる・規制リスクなど（30字以内）"
  ]
}

【重要ルール】
- summary: 「〇〇に使える」「〇〇が変わる」など結論ファーストで
- actions[0]: Claude/Cursor/Codexなど実在ツールを具体的に挙げ「△△の業務に使える」形式で
- actions[1]: 採用・営業・中小企業DX・バックオフィス自動化など現場目線の提案
- actions[2]: 競合が動いている・コストが下がる・規制リスクがあるなどの理由
- ツールが関係ない記事（研究・政策系）は「業界への示唆」として意義を書く
- 全て30〜60字以内、日本語のみ

入力された各記事のtitleとledeとkeypointsを参考に、対応するbizappをJSON配列で返してください。
配列の順番は入力と同じにすること。

出力形式:
[
  {"summary": "...", "actions": ["...", "...", "..."]},
  ...
]
"""


def generate_bizapp(articles: list[dict]) -> list[dict]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    digest_parts = []
    for i, a in enumerate(articles):
        keypoints = "\n".join(f"  - {kp}" for kp in a.get("keypoints", []))
        digest_parts.append(
            f"[{i}] {a['title']}\n"
            f"lede: {a.get('lede', '')}\n"
            f"keypoints:\n{keypoints}"
        )
    digest = "\n\n".join(digest_parts)

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        messages=[{"role": "user", "content": f"{BIZAPP_PROMPT}\n\n記事リスト:\n{digest}"}],
    )

    text = msg.content[0].text.strip()
    start = text.find("[")
    end = text.rfind("]") + 1
    raw = text[start:end]
    # trailing comma の修正
    import re
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    return json.loads(raw)


def process_file(path: Path) -> bool:
    with open(path) as f:
        articles = json.load(f)

    # すでにbizappが全件あればスキップ
    if all("bizapp" in a for a in articles):
        print(f"  SKIP (already done): {path}")
        return False

    print(f"  Generating bizapp for {len(articles)} articles in {path.parent.name}...")
    bizapp_list = generate_bizapp(articles)

    for i, (article, bizapp) in enumerate(zip(articles, bizapp_list)):
        article["bizapp"] = bizapp

    with open(path, "w") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"  DONE: {path.parent.name}")
    return True


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1] / "docs" / "news"
    json_files = sorted(base.glob("*/articles.json"))

    print(f"Found {len(json_files)} article files")
    updated = 0
    for p in json_files:
        if process_file(p):
            updated += 1

    print(f"\nComplete: {updated}/{len(json_files)} files updated")
