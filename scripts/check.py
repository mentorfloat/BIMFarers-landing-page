#!/usr/bin/env python3
"""Static integrity and initial-load budgets. Run after build.py; no dependencies."""
import gzip
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
        if tag in ['img', 'source', 'link']:
            for item in (a.get('srcset') or a.get('imagesrcset') or '').split(','):
                if item.strip():
                    self.assets.append(item.split()[0])
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
    # Transfer size is what affects loading; the raw ceiling stops unchecked growth.
    css = (ROOT / 'css/site.css').read_bytes()
    assert len(css) <= 32_000, 'CSS over 32 KB raw budget'
    assert len(gzip.compress(css, 9)) <= 9_000, 'CSS over 9 KB gzip budget'
    assert sum((ROOT / 'js' / name).stat().st_size for name in ['site.js','navigation.js']) <= 3_000, 'JS over 3 KB budget'
    assert (ROOT / 'index.html').stat().st_size <= 30_000, 'Homepage HTML over 30 KB budget'
    assert (ROOT / 'assets/optimized/model-1280.webp').stat().st_size <= 60_000
    assert (ROOT / 'assets/optimized/model-640.webp').stat().st_size <= 30_000
    assert sum((ROOT / 'fonts' / f'inter-web-{weight}.woff2').stat().st_size for weight in [300,500,700]) <= 24_000
    assert (ROOT / 'fonts/work-sans-brand.woff2').stat().st_size <= 2_000
    for name, budget in [('hero-model-640.avif',12_000),('hero-model-1280.avif',30_000),('hero-team-320.avif',8_000),('hero-team-640.avif',21_000)]:
        assert (ROOT / 'assets/optimized' / name).stat().st_size <= budget, f'{name} over budget'
    for url in re.findall(r'url\([\'\"]?([^\)\'\"]+)', (ROOT / 'css/site.css').read_text()):
        if url.startswith('data:font/woff2;base64,'):
            continue
        assert (ROOT / 'css' / url).is_file(), f'Missing CSS asset {url}'
    print(f'PASS: {len(parsed)} pages, assets, links, anchors, schema and load budgets.')


if __name__ == '__main__':
    check()
