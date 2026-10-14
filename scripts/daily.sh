#!/bin/bash
# Explicit stages only. The default performs a read-only local check.
set -euo pipefail

ROOT="${LUNA_NEWS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
MODE="${1:---check}"
if [ "$#" -gt 0 ]; then shift; fi
case "$MODE" in
  --check|--dry|--prepare|--render|--record-published) ;;
  *) echo "usage: daily.sh [--check|--prepare|--render|--record-published] [--date YYYY-MM-DD]" >&2; exit 2 ;;
esac
DATE_VALUE=""
while [ "$#" -gt 0 ]; do
  if [ "$1" != "--date" ] || [ "$#" -lt 2 ] || [ -n "$DATE_VALUE" ]; then
    echo "invalid arguments: only one --date YYYY-MM-DD is accepted" >&2
    exit 2
  fi
  DATE_VALUE="$2"
  shift 2
done
if [ -n "$DATE_VALUE" ] && ! [[ "$DATE_VALUE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "invalid date format: expected YYYY-MM-DD" >&2; exit 2
fi
if [ -n "${LUNA_NEWS_PYTHON:-}" ]; then
  PYTHON="$LUNA_NEWS_PYTHON"
elif [ -x "$ROOT/venv/bin/python" ]; then
  PYTHON="$ROOT/venv/bin/python"
else
  PYTHON=python3
fi
cd "$ROOT"
if [ -n "$DATE_VALUE" ]; then
  # Validate the calendar before --render can change any generated files.
  "$PYTHON" -c 'from datetime import date; import sys
try: date.fromisoformat(sys.argv[1])
except ValueError: sys.exit(2)' "$DATE_VALUE"
  set -- --date "$DATE_VALUE"
else
  set --
fi
case "$MODE" in
  --check|--dry)
    exec "$PYTHON" scripts/issue_check.py --root "$ROOT/docs" "$@" ;;
  --prepare)
    exec env LLM_PROVIDER=codex LLM_FALLBACK_CHAIN=codex,claude \
      "$PYTHON" pipeline/run.py --prepare --skip-slides --skip-social "$@" ;;
  --render)
    # Rebuild reviewed source first; stale generated HTML is expected beforehand.
    "$PYTHON" scripts/rebuild_all.py
    "$PYTHON" scripts/issue_check.py --root "$ROOT/docs" "$@"
    exec "$PYTHON" scripts/check_newspaper.py ;;
  --record-published)
    exec "$PYTHON" pipeline/run.py --record-published "$@" ;;
esac
