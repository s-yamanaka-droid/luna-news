# Now on AIr — 単号の制作と公開

## 状態と実行先

2026-10-14号は1記事を公開済み。更新経路の修正は候補であり、定期workerは未起動。物理Mark 6の受信・実行も未確認。画面共有やSMB接続を、このGit作業の必須条件にしない。

対象端末の既存 `s-yamanaka-droid/luna-news` を使い、現在のmainと本人の最新指示を確認する。古いデザインpatchや過去号のoverlayを戻さない。Python 3.11以降・Pillow・対象端末での通常CLIログインを確認する。OS/メモリとCLIの存在確認は、制作実行やMCP接続の証拠とは分ける。

## 1. 既存号の読取検査

```bash
bash scripts/daily.sh --check --date 2026-10-14
bash scripts/watchdog.sh --date 2026-10-14
```

引数なしの `daily.sh` と `daily.sh --dry` はローカルの読取検査のみ。watchdogは本番の検査を1巡だけ実施する。どちらも通知・既読登録・生成・公開を行わない。JSONの `ok`、`errors`、`articles_sha256`、`asset_hashes` を見る。HTTP 200やhealthの生成日時だけで最新号と判断しない。

## 2. 新しい候補を制作

本人が指定した、まだ存在しない号日付で実行する。

```bash
bash scripts/daily.sh --prepare --date YYYY-MM-DD
```

これはRSS等の読取、Codex/Claude CLI、ローカル書込を使う。候補は `docs/news/日付/articles.json` に保存される。直接APIプロバイダへ自動で切り替えず、生成失敗なら停止する。既存号があれば上書きしない。

候補はそのまま公開しない。編集担当が原典の日付・数字・対象・例外を確認し、記事ごとのhero、PC図解、mobile図解、OGを用意する。発表日と号日付を区別する。4役の画像は固有の内容を持たせる。技術検査の合格は原典の事実やデザインの合格ではない。

## 3. 編集済み原稿をHTMLへ反映

```bash
bash scripts/daily.sh --render --date YYYY-MM-DD
python3 -m unittest discover -s tests -v
git diff --check
```

renderは既存の原稿からHTML等を再生成し、対象号と全体リンクを検査する。エラーは非zeroで停止する。PC・mobile・OGの実画面と主要操作を別途確認する。SNS・Slack・メール・有料画像生成をこのコマンドへ追加しない。

## 4. 承認された変更をGitへ公開

作業リポ・branch・remote・statusとremote mainとの差分/未push履歴を確認する。mainへ統合する範囲をレビューし、既存stageと無関係のdirty docsを残したまま進めない。`deploy.py` は既存main・既存origin・個別ファイルだけを受け付ける。今回選択したファイル以外の未push履歴も `HEAD:main` へ送られるため、履歴のレビューを省略しない。

```bash
python3 pipeline/deploy.py --publish --date YYYY-MM-DD \
  --message 'Publish reviewed issue YYYY-MM-DD' \
  --path docs/index.html \
  --path docs/news/YYYY-MM-DD/articles.json
```

これは引数の形を示す例。実際には号/記事HTML、全画像、feed、sitemap、healthなど、レビューで確定した**すべての変更ファイルを個別に**追加する。ディレクトリや `git add .` / `git add -A` は使わない。候補に依存する未選択docs差分があれば停止する。検査失敗後に選択ファイルがstageへ残ることがあるため、statusを再確認する。

Git公開の成功はremote mainのSHA一致まで。既存VercelのReadyと本番aliasを確認し、pushを本番受入と読み替えない。

## 5. 本番を読み戻して、採用URLだけ既読登録

```bash
bash scripts/watchdog.sh --date YYYY-MM-DD
bash scripts/daily.sh --record-published --date YYYY-MM-DD
```

record-publishedはローカル/本番双方の号・本文・画像検査とarticles/4画像のhash一致を要求する。照合中に原稿が変われば停止する。成功時だけ採用記事のlinksを既読登録し、`logs/published_日付.json` に内容を識別できるreceiptを残す。未採用候補・通知・相手の受領は記録対象に含めない。

既読状態は既定でこのcheckoutの `logs/seen_urls.json`。必要時は `LUNA_NEWS_SEEN_FILE` で明示する。旧CMOのcacheや旧done/content_ready markerはコピー・削除・成功根拠への流用をしない。

## 定期実行へ進む条件

対象端末で単号の制作・編集・Git公開・本番照合を実行した証拠が必要。新規scheduler、通知、課金や権限追加はこの修正の対象外。既存workerがない状態で「定期復旧済み」と報告しない。

既存のクラウド成果物の転送が自動承認レビューで停止した範囲は保留し、権限モードやセッションを変えて回避しない。
