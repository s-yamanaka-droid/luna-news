import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'pipeline'), str(ROOT / 'scripts')]
from newspaper import headline, story_body, lakkan_block
from check_freshness import status

class NewspaperTests(unittest.TestCase):
    def test_article_text_is_escaped(self):
        self.assertNotIn('<script>', headline('<script>x</script>'))
        self.assertNotIn('<script>', story_body({'body': [{'heading': '<script>', 'paragraphs': ['<img onerror=x>']}]}))
    def test_service_blocks_do_not_duplicate_ids(self):
        self.assertNotIn('id="lakkan"', lakkan_block('crm'))
        self.assertIn('id="lakkan"', lakkan_block())
    def test_stale_news_is_not_healthy(self):
        latest = date.fromisoformat(status(ROOT / 'docs', date.today())['latest_issue'])
        self.assertTrue(status(ROOT / 'docs', latest)['fresh'])
        self.assertFalse(status(ROOT / 'docs', latest + timedelta(days=3))['fresh'])
    def test_current_issue_has_sources_and_content(self):
        articles = json.loads((ROOT / 'docs/news/2026-09-14/articles.json').read_text())
        self.assertEqual(len(articles), 8)
        for a in articles:
            if a['article_kind'] == 'news': self.assertTrue(a['links'])
            self.assertLessEqual(a['published_at'], a['updated_at'])
            self.assertGreater(len(json.dumps(a['body'] + a['analysis'], ensure_ascii=False)), 400)
