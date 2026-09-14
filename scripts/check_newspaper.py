"""Check generated newspaper links, images and article preservation offline."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1] / 'docs'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.refs = set(), []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, 'duplicate id: ' + attrs['id']
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.refs.append(attrs[key])


paths = [ROOT / 'index.html', *sorted(ROOT.glob('news/*/index.html'))]
pages = {p: Page(p) for p in paths}
for path, page in pages.items():
    for ref in page.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc:
            continue
        target = (ROOT / unquote(url.path).lstrip('/')) if url.path.startswith('/') else path.parent / unquote(url.path)
        if not url.path:
            target = path
        if target.is_dir():
            target /= 'index.html'
        assert target.exists(), f'{path}: missing {ref}'
        if url.fragment and target.suffix == '.html':
            parsed = pages.get(target) or Page(target)
            assert unquote(url.fragment) in parsed.ids, f'{path}: missing anchor {ref}'
    data = path.parent / 'articles.json'
    if data.exists():
        articles = json.loads(data.read_text())
        for i in range(1, len(articles) + 1):
            assert f'topic-{i}' in page.ids, f'{path}: lost article {i}'
print(f'PASS: {len(paths)} pages; local links, images, anchors and article counts')
