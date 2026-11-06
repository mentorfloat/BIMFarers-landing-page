#!/usr/bin/env python3
"""Static integrity and initial-load budgets. Run after build.py; no dependencies."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = json.loads((ROOT / 'content/pages.json').read_text())


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.links, self.assets, self.headings = [], [], [], []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a':
            self.links.append(a.get('href', ''))
        if tag == 'h1':
            self.headings.append(tag)
        if tag in ['img', 'script', 'iframe'] and a.get('src'):
            self.assets.append(a['src'])
        if tag == 'img':
            assert 'alt' in a, f'Missing alt: {a}'
            assert 'width' in a and 'height' in a, f'Missing image dimensions: {a}'
        if tag == 'link' and a.get('rel') in ['stylesheet', 'preload', 'icon', 'apple-touch-icon']:
            self.assets.append(a['href'])


def check():
    parsed = {p['file']: Page((ROOT / p['file']).read_text()) for p in PAGES}
    for name, page in parsed.items():
        assert len(page.headings) == 1, f'{name}: expected one h1'
        assert len(page.ids) == len(set(page.ids)), f'{name}: duplicate IDs'
        for link in page.links + page.assets:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            path = (unquote(url.path).lstrip('/') or 'index.html') if url.path else name
            if not (ROOT / path).is_file() and (ROOT / (path + '.html')).is_file():
                path += '.html'
            assert (ROOT / path).is_file(), f'{name}: missing {link}'
            if url.fragment and path in parsed:
                assert unquote(url.fragment) in parsed[path].ids, f'{name}: missing anchor {link}'
        assert not any(urlsplit(a).scheme for a in page.assets), f'{name}: third-party loading dependency'
        source = (ROOT / name).read_text()
        assert '{{' not in source, f'{name}: unrendered template'
        for script in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S):
            json.loads(script)
    assert (ROOT / 'css/site.css').stat().st_size <= 20_000, 'CSS over 20 KB budget'
    assert (ROOT / 'js/site.js').stat().st_size <= 3_000, 'JS over 3 KB budget'
    assert (ROOT / 'index.html').stat().st_size <= 30_000, 'Homepage HTML over 30 KB budget'
    assert (ROOT / 'assets/optimized/model-1280.webp').stat().st_size <= 60_000
    assert (ROOT / 'assets/optimized/model-640.webp').stat().st_size <= 30_000
    for url in re.findall(r'url\([\'\"]?([^\)\'\"]+)', (ROOT / 'css/site.css').read_text()):
        assert (ROOT / 'css' / url).is_file(), f'Missing CSS asset {url}'
    print(f'PASS: {len(parsed)} pages, assets, links, anchors, schema and load budgets.')


if __name__ == '__main__':
    check()
