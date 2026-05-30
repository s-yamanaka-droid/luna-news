#!/bin/bash
# Now on AIr — 毎朝の全自動パイプライン
# launchd から 6:30 に呼ばれる
set -e

cd /Users/yamanakashuto/apps/vigil-news
source venv/bin/activate

export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-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}"
export GEMINI_API_KEY="${GEMINI_API_KEY:-AIzaSyB_YxhSIVU7titeZ7BSIlQGjAQPD3y-NKg}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-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}"
export LLM_PROVIDER="${LLM_PROVIDER:-claude}"
export OPENAI_IMAGE_API_KEY="${OPENAI_IMAGE_API_KEY:-$OPENAI_API_KEY}"
# SLACK_TOKEN は launchd plist または ~/.zshrc から渡る（直書き禁止・秘密番人ブロック対象）
export SLACK_TOKEN="${SLACK_TOKEN}"
# 手動実行時は事前に source ~/.zshrc しておくこと

# 失敗時の Slack 通知関数
notify_failure() {
  local stage="$1"; local msg="$2"
  curl -s -X POST "https://slack.com/api/chat.postMessage" \
    -H "Authorization: Bearer $SLACK_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"channel\":\"C0B3M8YB1B9\",\"text\":\"⚠️ Now on AIr <@U0A5ALYDKMZ> $(date +%Y-%m-%d) 配信失敗\\n段階: $stage\\nエラー: $msg\\n→ ログ: /Users/yamanakashuto/apps/vigil-news/logs/daily_$(date +%Y-%m-%d).log\"}" >/dev/null 2>&1
}
trap 'notify_failure "unknown" "daily.sh が異常終了"' ERR

TODAY=$(date +%Y-%m-%d)
LOG=/Users/yamanakashuto/apps/vigil-news/logs/daily_${TODAY}.log

echo "=== Now on AIr daily $TODAY ===" | tee -a "$LOG"

echo "[1/4] RSS収集 → 記事生成 → スライド生成 → push" | tee -a "$LOG"
python pipeline/run.py 2>&1 | tee -a "$LOG"

# 記事生成失敗を検知（articles.json なければ即通知して終了）
if [ ! -f "/Users/yamanakashuto/apps/vigil-news/docs/news/$TODAY/articles.json" ]; then
  notify_failure "記事生成" "articles.json が作成されませんでした（pipeline/run.py 失敗）"
  echo "❌ 記事生成失敗 → Slack通知済み・以降スキップ" | tee -a "$LOG"
  exit 1
fi

echo "[2/4] quickstart 追加" | tee -a "$LOG"
python scripts/gen_quickstart.py "$TODAY" 2>&1 | tee -a "$LOG"

echo "[2.5/4] icebreak（会話・商談で使える）追加" | tee -a "$LOG"
python scripts/gen_icebreak.py "$TODAY" 2>&1 | tee -a "$LOG" || echo "icebreak生成失敗（処理は継続）" | tee -a "$LOG"

echo "[3/4] weekly digest 更新" | tee -a "$LOG"
python scripts/gen_weekly.py 2>&1 | tee -a "$LOG"

echo "[4/7] HTML 再ビルド" | tee -a "$LOG"
python scripts/rebuild_all.py 2>&1 | tee -a "$LOG"

echo "[5/7] GitHub push" | tee -a "$LOG"
cd /Users/yamanakashuto/apps/vigil-news
git add -A 2>&1 | tee -a "$LOG"
git commit -m "daily: $TODAY — quickstart + weekly refresh" 2>&1 | tee -a "$LOG" || echo "no changes" | tee -a "$LOG"
git push origin main 2>&1 | tee -a "$LOG"

echo "[6/7] Vercel 本番デプロイ" | tee -a "$LOG"
export PATH="$HOME/.npm-global/bin:$PATH"
vercel deploy --prod --yes 2>&1 | tee -a "$LOG" || echo "Vercelデプロイ失敗（処理は継続）" | tee -a "$LOG"

echo "[7/7] Slack #朝刊 通知 + Obsidian同期" | tee -a "$LOG"
python scripts/notify_slack.py "$TODAY" 2>&1 | tee -a "$LOG" || echo "Slack送信失敗（処理は継続）" | tee -a "$LOG"
python scripts/sync_obsidian.py "$TODAY" 2>&1 | tee -a "$LOG" || echo "Obsidian同期失敗（処理は継続）" | tee -a "$LOG"

echo "=== 完了 $TODAY ===" | tee -a "$LOG"
