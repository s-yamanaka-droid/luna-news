"""Publication and candidate generation must have separate side effects."""
import importlib.util
import hashlib
import json
import os
import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


class UpdateRecoveryTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {'LLM_PROVIDER': 'codex', 'LLM_FALLBACK_CHAIN': 'codex,claude'})
        environment.start()
        self.addCleanup(environment.stop)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name) / 'docs'
        self.raw = [{'link': 'https://example.org/used'}, {'link': 'https://example.org/unused'}]
        self.articles = [{'title': 'Verified candidate', 'links': ['https://example.org/used']}]
        self.collector = types.ModuleType('collector')
        self.collector.fetch_all = Mock(return_value=self.raw)
        self.collector.mark_seen = Mock()
        generator = types.ModuleType('generator')
        generator.generate_articles = Mock(return_value=self.articles)
        html = types.ModuleType('html_builder')
        html.SITE_DIR = self.site
        html.build_daily_page = Mock(return_value=self.site / 'issue.html')
        html.build_index = Mock(return_value=self.site / 'index.html')
        self.deploy = types.ModuleType('deploy')
        self.deploy.git_push = Mock(return_value=False)
        self.social = types.ModuleType('social_poster')
        self.social.post_dispatch = Mock()
        feeds = types.ModuleType('feeds')
        feeds.RSS_FEEDS = []
        self.checks = types.ModuleType('issue_check')
        self.checks.check_local = Mock(return_value={'ok': True, 'articles_sha256': 'same', 'asset_hashes': {'/assets/a.webp': 'x'}})
        self.checks.check_public = Mock(return_value={'ok': True, 'articles_sha256': 'same', 'asset_hashes': {'/assets/a.webp': 'x'}})
        modules = {'collector': self.collector, 'generator': generator, 'html_builder': html,
                   'deploy': self.deploy, 'social_poster': self.social, 'feeds': feeds, 'issue_check': self.checks}
        module_patch = patch.dict(sys.modules, modules)
        module_patch.start()
        self.addCleanup(module_patch.stop)
        spec = importlib.util.spec_from_file_location('isolated_news_run', ROOT / 'pipeline/run.py')
        self.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.runner)
        self.runner.SITE_DIR = self.site
        self.runner.LOG_DIR = Path(self.temp.name) / 'logs'

    def test_dry_preparation_does_not_publish_notify_or_mark_seen(self):
        self.runner.run(dry_run=True, skip_slides=True, skip_social=True)
        self.deploy.git_push.assert_not_called()
        self.social.post_dispatch.assert_not_called()
        self.collector.mark_seen.assert_not_called()

    def test_legacy_publish_request_stops_before_generation(self):
        with self.assertRaises(RuntimeError):
            self.runner.run(dry_run=False, skip_slides=True, skip_social=True)
        self.collector.fetch_all.assert_not_called()
        self.collector.mark_seen.assert_not_called()

    def test_existing_issue_is_not_overwritten_or_regenerated(self):
        from datetime import datetime
        from zoneinfo import ZoneInfo
        date_str = datetime.now(ZoneInfo('Asia/Tokyo')).date().isoformat()
        target = self.site / 'news' / date_str / 'articles.json'
        target.parent.mkdir(parents=True)
        target.write_text('[{"title":"owner saved"}]')
        with self.assertRaises(FileExistsError):
            self.runner.run(date_str=date_str, dry_run=True, skip_slides=True)
        self.assertEqual(json.loads(target.read_text())[0]['title'], 'owner saved')
        self.collector.fetch_all.assert_not_called()

    def _published_fixture(self):
        target = self.site / 'news/2026-10-14/articles.json'
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps(self.articles))
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        self.checks.check_local.return_value['articles_sha256'] = digest
        self.checks.check_public.return_value['articles_sha256'] = digest

    def test_published_receipt_marks_only_accepted_links(self):
        self._published_fixture()
        self.runner.record_published('2026-10-14')
        self.collector.mark_seen.assert_called_once_with(['https://example.org/used'])
        self.collector.fetch_all.assert_not_called()
        self.social.post_dispatch.assert_not_called()

    def test_different_candidate_on_same_date_does_not_mark_seen(self):
        self._published_fixture()
        self.checks.check_public.return_value = {'ok': True, 'articles_sha256': 'old', 'asset_hashes': {'/assets/a.webp': 'x'}}
        with self.assertRaises(RuntimeError):
            self.runner.record_published('2026-10-14')
        self.collector.mark_seen.assert_not_called()

    def test_failed_public_readback_does_not_create_receipt(self):
        self._published_fixture()
        self.checks.check_public.return_value = {'ok': False, 'errors': ['HTTP 404']}
        with self.assertRaises(RuntimeError):
            self.runner.record_published('2026-10-14')
        self.collector.mark_seen.assert_not_called()
        self.assertFalse((self.runner.LOG_DIR / 'published_2026-10-14.json').exists())

    def test_changed_source_during_readback_does_not_mark_different_urls(self):
        self._published_fixture()
        def replacement(*args):
            (self.site / 'news/2026-10-14/articles.json').write_text('[{"links":["https://example.org/different"]}]')
            return self.checks.check_local.return_value.copy()
        self.checks.check_public.side_effect = replacement
        with self.assertRaises(RuntimeError):
            self.runner.record_published('2026-10-14')
        self.collector.mark_seen.assert_not_called()


if __name__ == '__main__':
    unittest.main()
