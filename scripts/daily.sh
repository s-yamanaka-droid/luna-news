#!/bin/bash
# Now on AIr — 毎朝の全自動パイプライン
# launchd から 6:30 に呼ばれる
set -e

cd /Users/yamanakashuto/apps/vigil-news
source venv/bin/activate

export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-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}"
export GEMINI_API_KEY="${GEMINI_API_KEY:-AIzaSyDc5WQWXjQOLvisJue5cwskk95lpVBg794}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-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}"
export LLM_PROVIDER="${LLM_PROVIDER:-openai}"

TODAY=$(date +%Y-%m-%d)
LOG=/Users/yamanakashuto/apps/vigil-news/logs/daily_${TODAY}.log

echo "=== Now on AIr daily $TODAY ===" | tee -a "$LOG"

echo "[1/4] RSS収集 → 記事生成 → スライド生成 → push" | tee -a "$LOG"
python pipeline/run.py 2>&1 | tee -a "$LOG"

echo "[2/4] quickstart 追加" | tee -a "$LOG"
python scripts/gen_quickstart.py "$TODAY" 2>&1 | tee -a "$LOG"

echo "[3/4] weekly digest 更新" | tee -a "$LOG"
python scripts/gen_weekly.py 2>&1 | tee -a "$LOG"

echo "[4/5] HTML 再ビルド + push" | tee -a "$LOG"
python scripts/rebuild_all.py 2>&1 | tee -a "$LOG"
cd /Users/yamanakashuto/apps/vigil-news
git add -A 2>&1 | tee -a "$LOG"
git commit -m "daily: $TODAY — quickstart + weekly refresh" 2>&1 | tee -a "$LOG" || echo "no changes" | tee -a "$LOG"
git push origin main 2>&1 | tee -a "$LOG"

echo "[5/6] Slack #朝刊 通知" | tee -a "$LOG"
python scripts/notify_slack.py "$TODAY" 2>&1 | tee -a "$LOG" || echo "Slack送信失敗（処理は継続）" | tee -a "$LOG"

echo "[6/6] Obsidian vault 同期" | tee -a "$LOG"
python scripts/sync_obsidian.py "$TODAY" 2>&1 | tee -a "$LOG" || echo "Obsidian同期失敗（処理は継続）" | tee -a "$LOG"

echo "=== 完了 $TODAY ===" | tee -a "$LOG"
