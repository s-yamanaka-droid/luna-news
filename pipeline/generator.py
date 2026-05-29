"""
VIGIL — Generator v3 (2-Stage Pipeline)
Stage 1: Gemini Flash で全記事をスコアリング → TOP 30 選出
Stage 2: Gemini Flash で本文付き深い要約 → 記事8本生成
"""
import json

RANK_SYSTEM = """あなたはAI業界ニュースの編集長です。
与えられた記事一覧から、日本のビジネスパーソンにとって最も重要な記事を30件選んでください。

選定基準（重要度順）：
1. 日本企業・日本市場への直接的影響があるもの
2. AIツールの実務活用に直結するもの（新機能・価格変更・新サービス）
3. 大手AIラボの重大発表（新モデル・資金調達・提携）
4. 業界構造を変える動き（規制・M&A・標準化）
5. 同じトピックが複数ソースで報じられているもの（注目度が高い証拠）

除外：
- 古いニュースの焼き直し
- 特定ニッチすぎる研究論文（実用性が低いもの）
- 広告・PR記事

出力：JSONオブジェクトで返すこと。
{"top_indices": [0, 3, 7, ...]}
indexは入力記事の0始まり番号。最大30件。重要度順に並べること。"""

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


def _rank_articles(raw_articles: list[dict]) -> list[int]:
    """Stage 1: Gemini Flash で全記事をスコアリングし、TOP 30 の index を返す"""
    from llm import extract_json
    import google.generativeai as genai
    import os

    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")

    # タイトル+要約だけの軽量ダイジェストを作成
    lines = []
    for i, a in enumerate(raw_articles):
        lines.append(f"[{i}] [{a['source']}] {a['title']} — {a.get('summary','')[:150]}")
    digest = "\n".join(lines)

    resp = model.generate_content(
        f"{RANK_SYSTEM}\n\n記事一覧（{len(raw_articles)}件）:\n\n{digest}",
        generation_config=genai.GenerationConfig(
            max_output_tokens=1000,
            temperature=0.3,
        ),
    )
    text = resp.text
    parsed = json.loads(extract_json(text, "object"))
    return parsed.get("top_indices", list(range(min(30, len(raw_articles)))))


def generate_articles(raw_articles: list[dict]) -> list[dict]:
    """
    2-Stage Pipeline:
    Stage 1: Gemini Flash で全記事から TOP 30 を選出
    Stage 2: Gemini Flash で TOP 30 → 記事8本を生成
    """
    from llm import extract_json
    import google.generativeai as genai
    import os
    import logging

    log = logging.getLogger(__name__)

    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Stage 1: スコアリング（Gemini Flash・無料枠）
    log.info("   [Stage1] 全記事スコアリング（Gemini Flash）")
    top_indices = _rank_articles(raw_articles)
    log.info(f"   [Stage1] TOP {len(top_indices)}件選出")

    # Stage 2: 本格要約（Gemini Flash）
    top_articles = [raw_articles[i] for i in top_indices if i < len(raw_articles)]

    blocks = []
    for a in top_articles[:30]:
        body_part = f"\n【元記事本文】\n{a['body'][:1500]}" if a.get("body") else ""
        blocks.append(
            f"[{a['source']}] {a['title']}\n"
            f"RSS要約: {a['summary'][:200]}\n"
            f"URL: {a.get('link','')}"
            f"{body_part}"
        )
    digest = "\n\n---\n\n".join(blocks)

    log.info("   [Stage2] 記事生成（Gemini Flash）")
    resp = model.generate_content(
        f"{SYSTEM}\n\n今日のAI関連記事:\n\n{digest}",
        generation_config=genai.GenerationConfig(
            max_output_tokens=6000,
            temperature=0.3,
        ),
    )
    text = resp.text
    return json.loads(extract_json(text, "array"))


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from collector import fetch_all
    raw = fetch_all(max_per_feed=2, fetch_body=True)
    articles = generate_articles(raw)
    print(json.dumps(articles, ensure_ascii=False, indent=2))
