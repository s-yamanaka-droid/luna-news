"""Prepare one issue, or record a separately published and verified issue.

Preparation uses network/CLI and writes a candidate. It never pushes, posts,
deploys, calls paid repair, or marks source URLs as seen.
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'pipeline'), str(ROOT / 'scripts')]
from html_builder import build_daily_page, build_index, SITE_DIR
LOG_DIR = ROOT / 'logs'


def issue_date(value=None):
    from datetime import date
    return date.fromisoformat(value).isoformat() if value else datetime.now(ZoneInfo('Asia/Tokyo')).date().isoformat()


def _filter_by_pubdate(raw: list[dict], date_str: str) -> list[dict]:
    """バックフィル用：対象日の朝刊ウィンドウ（前日06:30〜当日06:30 JST）に
    公開された記事だけ残す。published が解析不能な記事は除外。"""
    from email.utils import parsedate_to_datetime
    from datetime import timedelta, timezone
    jst = timezone(timedelta(hours=9))
    day_end = datetime.strptime(date_str, "%Y-%m-%d").replace(
        hour=6, minute=30, tzinfo=jst)
    day_start = day_end - timedelta(hours=24)
    out = []
    for a in raw:
        pub = a.get("published", "")
        if not pub:
            continue
        try:
            dt = parsedate_to_datetime(pub)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except Exception:
            try:
                dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            except Exception:
                continue
        if day_start <= dt.astimezone(jst) < day_end:
            out.append(a)
    return out

def run(date_str=None, dry_run=True, skip_slides=True, skip_social=True):
    if not dry_run:
        raise RuntimeError('Publication is separate: review the candidate, then use deploy.py with explicit paths.')
    if not skip_slides:
        raise RuntimeError('Legacy generic slides are not part of the current editorial workflow.')
    date_str = issue_date(date_str)
    target = SITE_DIR / 'news' / date_str / 'articles.json'
    if target.exists():
        raise FileExistsError('Issue already exists; edit its reviewed source instead of regenerating it.')
    provider = os.environ.get('LLM_PROVIDER', 'codex').lower()
    chain = os.environ.get('LLM_FALLBACK_CHAIN', 'codex,claude').lower().split(',')
    if provider not in ('codex', 'claude') or any(value.strip() not in ('codex', 'claude') for value in chain):
        raise RuntimeError('Preparation permits codex/claude CLI only; direct API fallback is disabled.')
    from collector import fetch_all
    from generator import generate_articles
    raw = fetch_all(max_per_feed=2, fetch_body=True)
    if date_str != issue_date():
        raw = _filter_by_pubdate(raw, date_str)
    if not raw:
        raise RuntimeError('No dated source candidates; no issue was written.')
    articles = generate_articles(raw)
    if not articles:
        raise RuntimeError('No articles generated; no issue was written.')
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create protects against another session saving first.
    with target.open('x', encoding='utf-8') as output:
        json.dump(articles, output, ensure_ascii=False, indent=2)
    build_daily_page(date_str, articles)
    dates = sorted(path.parent.name for path in (SITE_DIR / 'news').glob('*/articles.json'))
    build_index(dates, articles, date_str)
    return {'status': 'candidate_needs_editorial_review', 'date': date_str, 'article_count': len(articles),
            'published': False, 'seen_updated': False, 'social_sent': False}


def record_published(date_str):
    from issue_check import check_local, check_public
    date_str = issue_date(date_str)
    local = check_local(SITE_DIR, date_str)
    if not local.get('ok'):
        raise RuntimeError('Local technical validation failed; no receipt or seen update.')
    public = check_public('https://nowonair.vercel.app', date_str)
    if not public.get('ok'):
        raise RuntimeError('Public readback failed; no receipt or seen update.')
    if not local.get('articles_sha256') or not local.get('asset_hashes'):
        raise RuntimeError('Missing content identity; no receipt or seen update.')
    if any(local.get(key) != public.get(key) for key in ('articles_sha256', 'asset_hashes')):
        raise RuntimeError('Production differs from this candidate; observe the alias again after deployment.')
    raw = (SITE_DIR / 'news' / date_str / 'articles.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != local['articles_sha256']:
        raise RuntimeError('Candidate changed during readback; no receipt or seen update.')
    articles = json.loads(raw)
    used = sorted({url for article in articles for url in article.get('links', []) if url})
    from collector import mark_seen
    mark_seen(used)
    receipt = {'status': 'published_and_read_back', 'date': date_str,
               'checked_at': datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(),
               'articles_sha256': local['articles_sha256'], 'asset_hashes': local['asset_hashes'],
               'accepted_source_count': len(used), 'social_sent': False}
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=LOG_DIR, delete=False) as output:
        json.dump(receipt, output, ensure_ascii=False, indent=2)
        temporary = Path(output.name)
    temporary.replace(LOG_DIR / f'published_{date_str}.json')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', '--dry', dest='prepare', action='store_true',
                      help='Candidate only: uses network/CLI and writes files.')
    mode.add_argument('--record-published', action='store_true',
                      help='Read production before updating accepted URLs and the local receipt.')
    parser.add_argument('--date', type=issue_date, default=None)
    parser.add_argument('--skip-slides', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--skip-social', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        result = record_published(args.date) if args.record_published else run(date_str=args.date)
    except (RuntimeError, FileExistsError, ValueError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=False))
        return 1
    except Exception as error:
        # Provider stderr/exception bodies can contain credentials.
        print(json.dumps({'ok': False, 'error': type(error).__name__}))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
