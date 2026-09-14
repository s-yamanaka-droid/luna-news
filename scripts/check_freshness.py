"""Read-only freshness check; exit 1 when news is older than two days."""
import json
from datetime import date
from pathlib import Path

def status(root, today):
    issues = sorted(root.glob('news/*/articles.json'))
    latest = issues[-1].parent.name if issues else None
    age = (today - date.fromisoformat(latest)).days if latest else None
    return {'latest_issue': latest, 'checked_on': today.isoformat(), 'age_days': age,
            'fresh': age is not None and 0 <= age <= 2,
            'article_count': len(json.loads(issues[-1].read_text())) if issues else 0}

if __name__ == '__main__':
    report = status(Path(__file__).resolve().parents[1] / 'docs', date.today())
    print(json.dumps(report, ensure_ascii=False))
    raise SystemExit(0 if report['fresh'] else 1)
