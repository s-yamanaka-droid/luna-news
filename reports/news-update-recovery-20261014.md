# 更新経路の修正候補 — 2026-10-14

## 確認した問題

- 旧dailyは `set -e` とteeの組合せでPython/git失敗を見落とし、公開・SNS・Slack・有料repair等を一括実行した。Vercel失敗を無視した後でもready/done markerを作成できた。
- 旧watchdogは現行メタデータに存在しないtopic_1.pngと500KBの閾値を期待した。
- 候補生成時に未採用URLまで既読登録し、同日号を再生成で上書きできた。
- deployは現在branchでcommit後にlocal mainをpushし、空commit時はpush前に成功を返す経路があった。
- LLM既定のfallbackには直接APIが含まれ、CLI/providerの例外本文をログへ出した。

## 変更

候補制作、明示した個別ファイルのGit公開、本番の内容照合、採用URL既読登録を分離した。dailyの既定と--dryは読取検査だけ。watchdogは実メタデータと実bytesに基づく1回のGET検査。旧marker・通知・再試行sleep・自動backfill・有料repairを実行経路から外した。

issue_checkはarticles JSONのSHAと4役の画像SHAを返し、日付・見出し・canonical・OG・NewsArticle・画像のdecode/形式/参照を確認する。404、HTML偽画像、重複bytes/pixels、外部asset、redirect、root外pathを拒否する。応答・画像pixels・合計bytes・全体時間は上限付き。

独立レビューで見つかった2件も修正した。未選択dirty/untracked docsがあればGit公開を停止する。公開照合後に原稿を再読取する際は同じbytesのSHAを再確認し、別候補のURLを既読にしない。

## 検証結果

- `bash -n scripts/daily.sh scripts/watchdog.sh`: 成功。
- `python3 -m unittest discover -s tests -v`: 53件成功。ネットワーク・モデル・push・通知はmock/一時fixture。
- `python3 scripts/check_newspaper.py`: 129ページのリンク・画像・アンカー・記事件数に合格。
- `bash scripts/daily.sh --check --date 2026-10-14`: ok=true、1記事、4画像。
- `bash scripts/watchdog.sh --date 2026-10-14`: 本番GETでok=true、同じ1記事/4画像。local/publicのarticles SHA `02362d2ddd17d6106b7af4838e8e001dfb64adf9d0660d746f2b51c6aeea82b8` と全asset hashesが一致。
- `git diff --check`: 成功。

## 未実行と境界

新しい記事生成、実CLIモデル呼出、Git公開helperの実本番push、record-publishedの実既読更新、通知、新規schedulerは実行していない。本番コンテンツは既存main `1190f679ebc6d23970bb874b2fddee887853d2d5` の10/14号1記事を維持。

この修正はreview用候補。物理Mark 6への受領と単号実行、MCP連携、ウェビナー実制作、追加2記事の転送/公開、定期workerの稼働は未完。具体的な単号手順は `OPERATIONS.md`。技術検査の合格を、原典確認・デザイン合格・継続稼働の証拠にしない。
