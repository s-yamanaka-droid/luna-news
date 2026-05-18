"""
VIGIL — Generator v2
元記事本文をHaikuに渡してファクトグラウンドな要約を生成する
"""
import json
import anthropic

SYSTEM = """あなたはAI業界ニュースを「日本人ビジネスパーソン」に届ける専門編集者です。
与えられた記事の【元記事本文】を一次情報として使い、ニュースサイト掲載用データをJSON配列で返してください。

出力形式（JSON配列）:
[
  {
    "title": "見出し（日本語・40字以内）",
    "category": "カテゴリ（業界動向/ツール更新/新モデル発表/研究/その他）",
    "source": "ソース名",
    "lede": "リード文（日本語・100字以内・核心を一文で）",
    "keypoints": ["要点1（30字以内）", "要点2", "要点3", "要点4"],
    "pull": "プルクォート（60字以内・本質的な洞察を）",
    "bizapp": {
      "summary": "このニュースをビジネスでどう使うか（60字以内・一言で結論から）",
      "actions": [
        "社内活用例：Claude / Cursor / Codex など具体ツールを絡めた実践アクション（30字以内）",
        "他社提案例：中小企業・採用・営業など現場に刺さる提案アイデア（30字以内）",
        "注目理由：なぜ今これを知っておくべきか（30字以内）"
      ]
    },
    "links": ["元記事URL"],
    "likes": 0
  }
]

【文章スタイルの指針】
- 対象読者：AIに詳しくない日本のビジネスパーソン（営業・マーケ・経営層）
- 難しい英語の専門用語は必ず日本語で言い換えるか、括弧で補足する
  例：「LLM（大規模言語モデル）」「RAG（AIが資料を参照して回答する仕組み）」
- 「これが自分の仕事にどう関係するか」が伝わる書き方にする
- 抽象的な技術説明より「何ができるようになったか・何が変わるか」を優先
- 見出しは新聞の一面のように、読んだ瞬間に内容がわかる表現にする
- keypoints は箇条書きで、専門知識がなくても読める平易な日本語で

【bizapp の書き方】
- summary：「〇〇に使える」「〇〇が変わる」など結論ファーストで
- actions[0] 社内活用：Claude（AIアシスタント）・Cursor（AI搭載コードエディタ）・Codex（AIコーディングエージェント）など実在ツールを具体的に挙げ、「△△の業務に使える」形式で
- actions[1] 他社提案：採用・営業・中小企業DX・バックオフィス自動化など現場目線の提案を
- actions[2] 注目理由：競合が動いている・コストが下がる・規制リスクがあるなどの理由を
- ツールが関係ない記事（研究・政策系）は「業界への示唆」として意義を書く

【厳守ルール】
- 上位8件を重要度順で選ぶ（日本のビジネス文脈で影響が大きい順）
- 全て日本語
- 【元記事本文】に書かれていない事実・数字・固有名詞は絶対に追加しない
- 本文が空の場合はタイトルとRSS要約だけを根拠にする
- 同じトピックの記事は1本にまとめる"""


def generate_articles(raw_articles: list[dict]) -> list[dict]:
    client = anthropic.Anthropic()
    # 記事ごとに元本文を含めた情報を構築
    blocks = []
    for a in raw_articles[:24]:
        body_part = f"\n【元記事本文】\n{a['body'][:1500]}" if a.get("body") else ""
        blocks.append(
            f"[{a['source']}] {a['title']}\n"
            f"RSS要約: {a['summary'][:200]}\n"
            f"URL: {a.get('link','')}"
            f"{body_part}"
        )
    digest = "\n\n---\n\n".join(blocks)

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=6000,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"今日のAI関連記事:\n\n{digest}"}],
    )

    text = msg.content[0].text.strip()
    start = text.find("[")
    end   = text.rfind("]") + 1
    raw = text[start:end]
    # Claude が末尾カンマを出すケースの修復
    import re
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    return json.loads(raw)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path.home() / "agents/cmo/x_agent"))
    from researcher import fetch_latest
    raw = fetch_latest(max_per_feed=3, fetch_body=True)
    articles = generate_articles(raw)
    print(json.dumps(articles, ensure_ascii=False, indent=2))
