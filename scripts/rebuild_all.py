"""
全日付の HTML を再ビルドするスクリプト
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
from html_builder import build_daily_page, build_index, SITE_DIR

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

# ── sitemap.xml 自動生成（SEO）──
SITE = "https://s-yamanaka-droid.github.io/nowonair/"
from datetime import date as _date
urls = [
    (SITE, "daily", "1.0"),
    (SITE + "weekly.html", "weekly", "0.8"),
    (SITE + "cases.html", "monthly", "0.6"),
    (SITE + "privacy.html", "yearly", "0.3"),
]
for d in reversed(all_dates):
    urls.append((f"{SITE}news/{d}/", "monthly", "0.5"))
today = _date.today().isoformat()
xml = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, freq, pri in urls:
    xml.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod>"
               f"<changefreq>{freq}</changefreq><priority>{pri}</priority></url>")
xml.append("</urlset>")
(SITE_DIR / "sitemap.xml").write_text("\n".join(xml), encoding="utf-8")
print(f"Sitemap → {SITE_DIR / 'sitemap.xml'} ({len(urls)} URLs)")

print("\nAll pages rebuilt successfully!")
