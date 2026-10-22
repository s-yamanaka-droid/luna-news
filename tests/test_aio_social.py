"""Regression checks for crawlable stories and social entry points."""
import json
import hashlib
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from newspaper import link, index


class Tags(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class AioSocialTests(unittest.TestCase):
    def test_latest_issue_links_to_permanent_story(self):
        self.assertEqual(link("2026-09-14", 1), "/articles/2026-09-14/story-1/")

    def test_story_page_has_unique_search_and_social_identity(self):
        path = ROOT / "docs/articles/2026-09-14/story-1/index.html"
        self.assertTrue(path.exists())
        html = path.read_text()
        tags = Tags(html).tags
        self.assertEqual(sum(tag == "h1" for tag, _ in tags), 1)
        self.assertEqual(
            [attrs.get("href") for tag, attrs in tags if tag == "link" and attrs.get("rel") == "canonical"],
            ["https://nowonair.vercel.app/articles/2026-09-14/story-1/"],
        )
        self.assertIn('property="og:description"', html)
        self.assertIn('property="og:url"', html)
        self.assertIn('class="share-article"', html)
        scripts = []
        import re
        for match in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            scripts.append(json.loads(match.group(1)))
        articles = [v for script in scripts for v in script.get("@graph", [script]) if v.get("@type") == "NewsArticle"]
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["url"], "https://nowonair.vercel.app/articles/2026-09-14/story-1/")
        self.assertEqual(articles[0]["publisher"]["name"], "株式会社Lakkan")
        self.assertNotIn("logo", articles[0]["publisher"])

    def test_sitemap_lists_story_url(self):
        tree = ElementTree.parse(ROOT / "docs/sitemap.xml")
        urls = [el.text for el in tree.findall(".//{*}loc")]
        self.assertIn("https://nowonair.vercel.app/articles/2026-09-14/story-1/", urls)

    def test_editorial_diagram_is_visible_and_crawlable(self):
        html = (ROOT / "docs/articles/2026-09-14/story-1/index.html").read_text()
        self.assertIn('class="editorial-figure"', html)
        self.assertIn('srcset="/assets/illustrations/anthropic-misuse-examples-mobile.webp"', html)
        self.assertIn('alt="サーバーの異常を調べる場面、', html)
        self.assertIn('サイバー攻撃', html)
        self.assertIn('監視', html)
        self.assertIn('詐欺', html)
        self.assertIn('実際の被害者・画面・報告書を再現したものではありません。', html)
        self.assertIn('property="og:image" content="https://nowonair.vercel.app/assets/og/anthropic-misuse-report.png"', html)
        self.assertNotIn('AIに何を許す', html)
        self.assertNotIn(str(ROOT), html)
        self.assertTrue((ROOT / "docs/assets/illustrations/anthropic-misuse-examples-wide.webp").exists())
        self.assertTrue((ROOT / "docs/assets/illustrations/anthropic-misuse-examples-mobile.webp").exists())
        self.assertTrue((ROOT / "docs/assets/og/anthropic-misuse-report.png").exists())

    def test_archived_lead_keeps_distinct_article_and_social_images(self):
        article = (ROOT / "docs/articles/2026-09-14/story-1/index.html").read_text()
        self.assertIn('src="/assets/illustrations/anthropic-misuse-examples-wide.webp"', article)
        self.assertIn('property="og:image" content="https://nowonair.vercel.app/assets/og/anthropic-misuse-report.png"', article)
        paths = [
            ROOT / "docs/assets/illustrations/anthropic-threat-report-home.webp",
            ROOT / "docs/assets/illustrations/anthropic-misuse-examples-wide.webp",
            ROOT / "docs/assets/og/anthropic-misuse-report.png",
        ]
        digests = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
        self.assertEqual(len(set(digests)), 3)

    def test_latest_home_article_and_social_use_distinct_images(self):
        latest = sorted((ROOT / "docs/news").glob("*/articles.json"))[-1]
        issue_date = latest.parent.name
        lead = json.loads(latest.read_text())[0]
        diagram = lead["editorial_diagram"]
        home = (ROOT / "docs/index.html").read_text()
        article = (ROOT / f"docs/articles/{issue_date}/story-1/index.html").read_text()
        self.assertIn(f'datetime="{issue_date}"', home)
        self.assertIn(f'src="{lead["hero_image"]}"', home)
        self.assertNotIn(diagram["wide"], home)
        self.assertIn(f'src="{diagram["wide"]}"', article)
        self.assertIn(f'srcset="{diagram["mobile"]}"', article)
        self.assertIn(f'property="og:image" content="https://nowonair.vercel.app{lead["social_image"]}"', article)
        self.assertNotIn('AIに何を許す', home)
        paths = [ROOT / "docs" / path.lstrip("/") for path in
                 (lead["hero_image"], diagram["wide"], diagram["mobile"], lead["social_image"])]
        digests = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
        self.assertEqual(len(set(digests)), 4)

    def test_october_14_issue_keeps_verified_source_dates(self):
        stories = json.loads((ROOT / "docs/news/2026-10-14/articles.json").read_text())
        self.assertEqual(len(stories), 1)
        for story in stories:
            self.assertTrue(story["links"] and all(url.startswith("https://") for url in story["links"]))
            self.assertRegex(story["published_at"], r"^2026-10-1[34]$")
            self.assertEqual(story["verified_at"], "2026-10-14")
        self.assertEqual(stories[0]["published_at"], "2026-10-13")
        self.assertIn("introducing-gemini-4-argon", stories[0]["links"][0])

    def test_single_article_home_labels_archive_rail_with_original_date(self):
        current = json.loads((ROOT / "docs/news/2026-10-14/articles.json").read_text())[:1]
        previous = json.loads((ROOT / "docs/news/2026-09-14/articles.json").read_text())[:2]
        with TemporaryDirectory() as folder:
            site = Path(folder)
            archive = site / "news/2026-09-14/articles.json"
            archive.parent.mkdir(parents=True)
            archive.write_text(json.dumps(previous))
            with patch("newspaper.SITE", site):
                path = index(["2026-09-14", "2026-10-14"], current, "2026-10-14")
            html = path.read_text()
        self.assertIn('aria-label="過去の掲載記事"', html)
        self.assertIn('2026-09-14 掲載', html)
        self.assertIn(f'href="{link("2026-09-14", 1)}"', html)
        self.assertNotIn('<h2>ほかの記事</h2>', html)

    def test_operator_page_is_linked_and_indexed(self):
        index = (ROOT / "docs/index.html").read_text()
        about = (ROOT / "docs/about.html").read_text()
        self.assertIn('href="/about.html"', index)
        self.assertIn('株式会社Lakkan', about)
        self.assertIn('"@type": "AboutPage"', about)
        sitemap = ElementTree.parse(ROOT / "docs/sitemap.xml")
        urls = [el.text for el in sitemap.findall(".//{*}loc")]
        self.assertIn("https://nowonair.vercel.app/about.html", urls)

    def test_social_entry_preserves_old_fragment_and_rss_permalink(self):
        issue = (ROOT / "docs/news/2026-09-14/index.html").read_text()
        self.assertIn('id="topic-1"', issue)
        self.assertIn('href="/articles/2026-09-14/story-1/"', issue)
        rss = ElementTree.parse(ROOT / "docs/feed.xml")
        links = [node.text for node in rss.findall(".//item/link")]
        # The feed keeps only the latest items, so check the permalink form rather than one old story.
        self.assertTrue(links)
        for url in links:
            self.assertRegex(url, r"^https://nowonair\.vercel\.app/articles/\d{4}-\d{2}-\d{2}/story-\d+/$")

    def test_freshness_report_is_explicitly_a_build_snapshot(self):
        report = json.loads((ROOT / "docs/health.json").read_text())
        self.assertTrue(report["snapshot_only"])
        self.assertNotIn("fresh", report)


if __name__ == "__main__":
    unittest.main()
