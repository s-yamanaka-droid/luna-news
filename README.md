# Now on AIr — AIの変化を、仕事の判断に

株式会社Lakkanが運営するAI専門メディア。発表原典、分かりやすい図解、実務で確認すべき点を一つの記事につなぐ。

**現状（2026-10-14 JST）:** 2026-10-14号（3本）をLuna-mk6クラウド（Ubuntu）で制作・検証した。C12デザインを維持し、トップ記事に固有のトップ画像・本文図解・SNS画像を付けた。main統合・本番反映・定期配信の再開は未確認で、報告は `reports/` を参照。

**公開URL:** https://nowonair.vercel.app

---

## 既存の制作・配信基盤

- RSS収集 → LLM要約 → 図解画像生成 → HTML生成 → デプロイの構成を持つ。各工程の現在の稼働状況は別途確認する
- 各記事に「明日からできる」quickstart（3ステップ＋プロンプト＋ROI）付き
- 週次ダイジェスト（TOP3）・AI活用事例集を併設
- 配信先：GitHub Pages / Vercel / Slack #朝刊 / Obsidian vault

## アーキテクチャ

```
pipeline/
  collector.py     RSS・API収集（本文取得）
  generator.py     記事生成（LLM抽象 llm.py 経由）
  llm.py           LLMプロバイダ抽象（codex / openai / anthropic）
  slide_maker.py   図解画像生成（Playwright HTML→PNG / Codex CLI）
  html_builder.py  サイトHTML生成（SEO・OGP・JSON-LD込み）
  newspaper.py     編集面・記事別ページ・運営者情報の生成
scripts/
  gen_quickstart.py  「明日からできる」生成
  gen_weekly.py      週次ダイジェスト生成
  notify_slack.py    Slack #朝刊 配信
  sync_obsidian.py   Obsidian vault 同期
  rebuild_all.py     全HTML再ビルド + sitemap生成
  daily.sh           旧定期配信入口（現行の起動状態は別確認）
docs/                GitHub Pages / Vercel 公開ディレクトリ
```

## セットアップ（5分）

```bash
cd /Users/yamanakashuto/Documents/ChatGPT/Luna/nowonair-journal
python3 -m venv venv && source venv/bin/activate
pip install openai anthropic feedparser beautifulsoup4 requests jinja2 playwright
playwright install chromium

# 環境変数
export OPENAI_API_KEY=...      # または LLM_PROVIDER=codex（ChatGPT Plus・API課金ゼロ）
export GEMINI_API_KEY=...      # 画像生成（任意）
export SLACK_TOKEN=...         # Slack配信
```

## 実行

```bash
bash scripts/daily.sh          # フルパイプライン（毎朝launchdが実行）
python scripts/rebuild_all.py  # HTMLのみ再生成
```

## デプロイ

- **Vercel（本番）:** `vercel deploy --prod` — 全セキュリティヘッダー付与（vercel.json）
- **GitHub Pages:** `git push origin main`（docs/ 配信）

## ライセンス / 運営

運営：株式会社Lakkan（編集責任者：山中秀斗）
© 2026 Now on AIr / Lakkan
