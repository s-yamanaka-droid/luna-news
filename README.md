# Now on AIr — AIの変化を、仕事の判断に

株式会社Lakkanが運営するAI専門メディア。発表原典、分かりやすい図解、実務で確認すべき点を一つの記事につなぐ。

**公開状態（2026-10-14 JST）:** Gemini 4 Argonの1本を10月14日号としてmainへ統合し、本番の本文・日付・4画像とPC/モバイル表示を確認済み。制作はLuna-mk6クラウド（Ubuntu）で行った。追加2記事は転送停止のため非公開。物理Mark 6の受信・実行と定期配信は未確認。公開記録は `reports/mark6-news-release-20261014.md`。

**更新処理の修正候補:** 候補制作・Git公開・本番照合を分離した。修正branchの検証は `reports/news-update-recovery-20261014.md`、実行手順は `OPERATIONS.md`。この変更だけで定期配信が再開したとは扱わない。

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
  daily.sh           明示した1工程を実行（引数なしは読取検査のみ）
  issue_check.py     号・本文・画像を読取検査しhashを返す
  watchdog.sh        本番の1回限りの読取検査（通知なし）
docs/                GitHub Pages / Vercel 公開ディレクトリ
```

## 既存リポの実行環境

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install Pillow feedparser beautifulsoup4 requests
```

Python 3.11以降と、対象端末で通常ログインしたCodex/Claude Code CLIを使う。CLIの利用枠・認証方式はその端末で確認する。直接APIへの自動フォールバックは候補制作で使わない。画像の制作は承認済み編集方針に従って別工程で行う。秘密・他端末の認証ファイルはコピーしない。

## 実行

```bash
bash scripts/daily.sh --check --date 2026-10-14    # ローカル読取のみ
bash scripts/watchdog.sh --date 2026-10-14        # 本番読取のみ
python -m unittest discover -s tests -v
```

`--prepare` はネットワーク・CLI・ファイル書込を使う制作工程。公開、SNS、既読登録は実行しない。生成後は事実・画像・PC/モバイルの編集確認が必要。既存号の再生成は停止する。各工程と受入条件は `OPERATIONS.md` を参照。

## デプロイ

- **Vercel（本番）:** 既存Git連携でmainからデプロイ。Git push成功と本番の受入を分けて確認する。
- `pipeline/deploy.py --publish` はmain・既存origin・個別ファイル・技術検査を要求する。既存stageや未選択docs差分があれば停止する。手順は `OPERATIONS.md`。
- `daily.sh` は公開や通知を行わず、既存のdone/content_ready markerも成功根拠に使わない。新規スケジューラは追加していない。

## ライセンス / 運営

運営：株式会社Lakkan（編集責任者：山中秀斗）
© 2026 Now on AIr / Lakkan
