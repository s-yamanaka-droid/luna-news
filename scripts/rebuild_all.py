"""
全日付の HTML を再ビルドするスクリプト
"""
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
from html_builder import build_daily_page, build_index, build_feed, SITE_DIR
from newspaper import PER_ARTICLE_FROM, about_page, link

base = SITE_DIR / "news"
date_dirs = sorted(d for d in base.iterdir() if d.is_dir() and (d / "articles.json").exists())

all_dates = [d.name for d in date_dirs]
print(f"Found {len(date_dirs)} date directories: {all_dates}")

# 最新日のarticles
latest_articles = []
latest_date = ""
if date_dirs:
    latest_date = date_dirs[-1].name
    latest_articles = json.loads((date_dirs[-1] / "articles.json").read_text(encoding="utf-8"))

for i, d in enumerate(date_dirs, 1):
    articles = json.loads((d / "articles.json").read_text(encoding="utf-8"))
    issue_num = i
    p = build_daily_page(d.name, articles, issue_num)
    print(f"  [{i}/{len(date_dirs)}] {d.name} → {p.name}  ({len(articles)} articles)")

# index rebuild
p_idx = build_index(all_dates, latest_articles, latest_date)
print(f"\nIndex → {p_idx}")
p_about = about_page(latest_date)
print(f"About → {p_about}")

# ── sitemap.xml: actual significant update dates, not the build date ──
SITE = "https://nowonair.vercel.app/"
from datetime import date as _date
from datetime import datetime as _datetime
from zoneinfo import ZoneInfo
today = _datetime.now(ZoneInfo('Asia/Tokyo')).date()
urls = [
    (SITE, latest_date or None),
    (SITE + "weekly.html", None),
    (SITE + "cases.html", None),
    (SITE + "privacy.html", None),
    (SITE + "about.html", None),
]
for d in reversed(all_dates):
    urls.append((f"{SITE}news/{d}/", d))
    if d >= PER_ARTICLE_FROM:
        articles = json.loads((SITE_DIR / 'news' / d / 'articles.json').read_text(encoding='utf-8'))
        for number, article in enumerate(articles, 1):
            modified = article.get('updated_at') or d
            urls.append((SITE.rstrip('/') + link(d, number), modified))
xml = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, modified in urls:
    xml.append(f"  <url><loc>{xml_escape(loc)}</loc>"
               + (f"<lastmod>{xml_escape(str(modified))}</lastmod>" if modified else '') + '</url>')
xml.append("</urlset>")
(SITE_DIR / "sitemap.xml").write_text("\n".join(xml), encoding="utf-8")
print(f"Sitemap → {SITE_DIR / 'sitemap.xml'} ({len(urls)} URLs)")

# Google News sitemap contains only stories from the most recent two days.
news_xml = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">']
for d in reversed(all_dates):
    age = (today - _date.fromisoformat(d)).days
    if not 0 <= age < 2 or d < PER_ARTICLE_FROM:
        continue
    articles = json.loads((SITE_DIR / 'news' / d / 'articles.json').read_text(encoding='utf-8'))
    for number, article in enumerate(articles, 1):
        if article.get('article_kind') != 'news':
            continue
        news_xml.append(f'  <url><loc>{xml_escape(SITE.rstrip("/") + link(d, number))}</loc><news:news>'
                        f'<news:publication><news:name>Now on AIr</news:name><news:language>ja</news:language></news:publication>'
                        f'<news:publication_date>{d}</news:publication_date><news:title>{xml_escape(str(article.get("title", "")))}</news:title>'
                        '</news:news></url>')
news_xml.append('</urlset>')
(SITE_DIR / 'news-sitemap.xml').write_text('\n'.join(news_xml), encoding='utf-8')

# ── RSS フィード生成（購読・被リンク・Discover）──
feed_path = build_feed(all_dates)
from check_freshness import status
report = status(SITE_DIR, today)
snapshot = {'latest_issue': report['latest_issue'], 'checked_on': report['checked_on'],
            'age_days_at_build': report['age_days'], 'fresh_at_build': report['fresh'],
            'article_count': report['article_count'], 'snapshot_only': True}
(SITE_DIR / 'health.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"Feed → {feed_path}")

print("\nAll pages rebuilt successfully!")
