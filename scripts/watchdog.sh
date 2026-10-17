#!/bin/bash
# One read-only production check. No retries, generation, notifications, or markers.
set -euo pipefail
ROOT="${LUNA_NEWS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
if [ -n "${LUNA_NEWS_PYTHON:-}" ]; then
  PYTHON="$LUNA_NEWS_PYTHON"
elif [ -x "$ROOT/venv/bin/python" ]; then
  PYTHON="$ROOT/venv/bin/python"
else
  PYTHON=python3
fi
cd "$ROOT"
exec "$PYTHON" scripts/issue_check.py \
  --base-url "${LUNA_NEWS_PUBLIC_URL:-https://nowonair.vercel.app}" "$@"
