"""Rebuild the front page from the latest published issue without changing articles or dates."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from newspaper import index


def main():
    issues = sorted((ROOT / "docs/news").glob("*/articles.json"))
    if not issues:
        raise SystemExit("No published issue found; front page was not changed")
    latest = issues[-1]
    articles = json.loads(latest.read_text(encoding="utf-8"))
    path = index([issue.parent.name for issue in issues], articles, latest.parent.name)
    print(f"Front page rebuilt from {latest.parent.name}: {len(articles)} articles -> {path.name}")


if __name__ == "__main__":
    main()
