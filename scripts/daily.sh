#!/bin/bash
# Now on AIr — 毎朝の全自動パイプライン
# launchd から 6:30 に呼ばれる
set -e

cd /Users/yamanakashuto/apps/luna-news
source venv/bin/activate

# 🔒 APIキーは直書き禁止（憲法§秘密番人）。値は launchd plist の EnvironmentVariables
#    または手動実行時の ~/.zshrc から注入される。ここではデフォルト値を一切持たない。
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
export GEMINI_API_KEY="${GEMINI_API_KEY}"
export OPENAI_API_KEY="${OPENAI_API_KEY}"
export LLM_PROVIDER="${LLM_PROVIDER:-codex}"   # ChatGPT Plus サブスク内・API課金ゼロ
export OPENAI_IMAGE_API_KEY="${OPENAI_IMAGE_API_KEY:-$OPENAI_API_KEY}"
export SLACK_TOKEN="${SLACK_TOKEN}"
# 手動実行時は事前に source ~/.zshrc しておくこと（plist 経由の launchd 実行時は自動注入）

# 失敗時の Slack 通知関数
notify_failure() {
  local stage="$1"; local msg="$2"
  curl -s -X POST "https://slack.com/api/chat.postMessage" \
    -H "Authorization: Bearer $SLACK_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"channel\":\"C0B3M8YB1B9\",\"text\":\"⚠️ Now on AIr <@U0A5ALYDKMZ> $(date +%Y-%m-%d) 配信失敗\\n段階: $stage\\nエラー: $msg\\n→ ログ: /Users/yamanakashuto/apps/luna-news/logs/daily_$(date +%Y-%m-%d).log\"}" >/dev/null 2>&1
}
trap 'notify_failure "unknown" "daily.sh が異常終了"' ERR

TODAY=$(date +%Y-%m-%d)
LOG=/Users/yamanakashuto/apps/luna-news/logs/daily_${TODAY}.log
DONE_MARKER=/Users/yamanakashuto/apps/luna-news/logs/done_${TODAY}

# 冪等ガード：当日完了済みなら何もしない（launchd 1日3回トリガーの2回目以降用）
if [ -f "$DONE_MARKER" ]; then
  echo "$(date '+%H:%M') already done for $TODAY — skip" >> "$LOG"
  exit 0
fi

echo "=== Now on AIr daily $TODAY ===" | tee -a "$LOG"

echo "[1/4] RSS収集 → 記事生成 → スライド生成 → push" | tee -a "$LOG"
python pipeline/run.py 2>&1 | tee -a "$LOG"

# 記事生成失敗を検知（articles.json なければ即通知して終了）
if [ ! -f "/Users/yamanakashuto/apps/luna-news/docs/news/$TODAY/articles.json" ]; then
  notify_failure "記事生成" "articles.json が作成されませんでした（pipeline/run.py 失敗）"
  echo "❌ 記事生成失敗 → Slack通知済み・以降スキップ" | tee -a "$LOG"
  exit 1
fi

# [1.7] 図解の自己修復（md5重複・劣化画像を OpenAI API で自動打ち直し）
echo "[1.7] 図解品質リペア" | tee -a "$LOG"
python scripts/repair_slides.py "$TODAY" 2>&1 | tee -a "$LOG" || echo "repair失敗（処理は継続）" | tee -a "$LOG"

# [1.8] WebP変換（表示用軽量版・PNGは番犬/OG用に残す。詳細ページ 12.8MB→1.5MB）
python scripts/webp_convert.py "$TODAY" 2>&1 | tee -a "$LOG" || echo "webp変換失敗（png表示にフォールバック）" | tee -a "$LOG"

# [1.5] 欠番バックフィル（直近3日・6/7 永久欠番事故の再発防止）
for d in 1 2 3; do
  DAY=$(date -v-${d}d +%Y-%m-%d)
  if [ ! -f "/Users/yamanakashuto/apps/luna-news/docs/news/$DAY/articles.json" ]; then
    echo "[backfill] $DAY が欠番 → 補完試行" | tee -a "$LOG"
    python pipeline/run.py --date "$DAY" --skip-social 2>&1 | tee -a "$LOG" || { echo "[backfill] $DAY 失敗（処理は継続）" | tee -a "$LOG"; continue; }
    if [ -f "/Users/yamanakashuto/apps/luna-news/docs/news/$DAY/articles.json" ]; then
      python scripts/repair_slides.py "$DAY" 2>&1 | tee -a "$LOG" || true   # 補完日の図解も検品・修復
      python scripts/webp_convert.py "$DAY" 2>&1 | tee -a "$LOG" || true     # 補完日もWebP化
      python scripts/gen_quickstart.py "$DAY" 2>&1 | tee -a "$LOG" || true
      python scripts/gen_icebreak.py "$DAY" 2>&1 | tee -a "$LOG" || true
      echo "[backfill] $DAY 補完完了" | tee -a "$LOG"
    fi
  fi
done

echo "[2/4] quickstart 追加" | tee -a "$LOG"
python scripts/gen_quickstart.py "$TODAY" 2>&1 | tee -a "$LOG"

echo "[2.5/4] icebreak（会話・商談で使える）追加" | tee -a "$LOG"
python scripts/gen_icebreak.py "$TODAY" 2>&1 | tee -a "$LOG" || echo "icebreak生成失敗（処理は継続）" | tee -a "$LOG"

echo "[3/4] weekly digest 更新" | tee -a "$LOG"
python scripts/gen_weekly.py 2>&1 | tee -a "$LOG"

echo "[4/7] HTML 再ビルド" | tee -a "$LOG"
python scripts/rebuild_all.py 2>&1 | tee -a "$LOG"

echo "[5/7] GitHub push" | tee -a "$LOG"
cd /Users/yamanakashuto/apps/luna-news
git add docs/ 2>&1 | tee -a "$LOG"   # 全体共通憲法: git add -A 恒久禁止。daily は docs/ のみ生成
git commit -m "daily: $TODAY — quickstart + weekly refresh" 2>&1 | tee -a "$LOG" || echo "no changes" | tee -a "$LOG"
git push origin main 2>&1 | tee -a "$LOG"

echo "[6/7] Vercel 本番デプロイ" | tee -a "$LOG"
export PATH="$HOME/.npm-global/bin:$PATH"
vercel deploy --prod --yes 2>&1 | tee -a "$LOG" || echo "Vercelデプロイ失敗（処理は継続）" | tee -a "$LOG"

echo "[7/7] Slack #朝刊 通知 + Obsidian同期" | tee -a "$LOG"
python scripts/notify_slack.py "$TODAY" 2>&1 | tee -a "$LOG" || echo "Slack送信失敗（処理は継続）" | tee -a "$LOG"
python scripts/sync_obsidian.py "$TODAY" 2>&1 | tee -a "$LOG" || echo "Obsidian同期失敗（処理は継続）" | tee -a "$LOG"

touch "$DONE_MARKER"   # 冪等ガード用（成功した日だけ作る）
echo "=== 完了 $TODAY ===" | tee -a "$LOG"
