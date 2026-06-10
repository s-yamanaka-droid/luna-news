#!/bin/bash
# Now on AIr — 配信番犬（毎日13:00）
# 本番サイトに「今日の朝刊」が出ているかを外形監視し、
# 出ていない時だけ Slack #朝刊 に警報を出す。正常時は何も言わない。
# daily.sh とは独立（パイプラインが沈黙死した日を検知するのが役目）。

TODAY=$(date +%Y-%m-%d)
URL="https://nowonair.vercel.app/news/${TODAY}/"
IMG="https://nowonair.vercel.app/assets/images/${TODAY}/topic_1.png"
LOG=/Users/yamanakashuto/apps/vigil-news/logs/watchdog.log

alert() {
  curl -s -X POST "https://slack.com/api/chat.postMessage" \
    -H "Authorization: Bearer $SLACK_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"channel\":\"C0B3M8YB1B9\",\"text\":\"🚨 Now on AIr 番犬 <@U0A5ALYDKMZ>\\n${TODAY} の朝刊が本番に出ていません\\n理由: $1\\n→ 復旧: cd ~/apps/vigil-news && bash scripts/daily.sh\"}" >/dev/null 2>&1
  echo "$(date '+%F %T') ALERT: $1" >> "$LOG"
}

# 1. 今日のページが 200 か（キャッシュバスター付き）
code=$(curl -sIL -o /dev/null -w "%{http_code}" --max-time 20 "${URL}?v=$(date +%s)")
if [ "$code" != "200" ]; then
  alert "ページが HTTP ${code}（未配信の可能性）"
  exit 1
fi

# 2. 図解画像が本物品質か（500KB未満 = Playwright劣化版の疑い）
size=$(curl -sIL --max-time 20 "${IMG}?v=$(date +%s)" | grep -i content-length | tail -1 | awk '{print $2}' | tr -d '\r')
if [ -z "$size" ] || [ "$size" -lt 500000 ] 2>/dev/null; then
  alert "topic_1.png が ${size:-取得不可}B（劣化画像 or 欠落の疑い）"
  exit 1
fi

echo "$(date '+%F %T') OK ${TODAY} (img=${size}B)" >> "$LOG"
exit 0
