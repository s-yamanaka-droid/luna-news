"""Published URL state is local to the checkout and works on a clean target."""
import importlib.util
import json
import sys
import types
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class CollectorStateTests(TestCase):
    def test_published_urls_save_into_a_new_nested_directory_and_preserve_existing_urls(self):
        modules = {name: types.ModuleType(name) for name in ('feedparser', 'requests', 'bs4', 'feeds', 'api_sources')}
        modules['bs4'].BeautifulSoup = object
        modules['feeds'].RSS_FEEDS = []
        modules['api_sources'].fetch_api_sources = object
        with patch.dict(sys.modules, modules), TemporaryDirectory() as folder:
            spec = importlib.util.spec_from_file_location('isolated_collector', ROOT / 'pipeline/collector.py')
            collector = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(collector)
            collector.SEEN_PATH = Path(folder) / 'new' / 'logs' / 'seen_urls.json'
            collector.mark_seen(['https://example.org/one'])
            collector.mark_seen(['https://example.org/two', 'https://example.org/one', ''])
            self.assertEqual(json.loads(collector.SEEN_PATH.read_text())['urls'],
                             ['https://example.org/one', 'https://example.org/two'])
            self.assertEqual(list(collector.SEEN_PATH.parent.glob('.seen-*')), [])


if __name__ == '__main__':
    main()
