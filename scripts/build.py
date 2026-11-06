#!/usr/bin/env python3
"""Render shared HTML shells. Python standard library only; no runtime build needed."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    pages = json.loads((ROOT / 'content/pages.json').read_text())
    shell = (ROOT / 'templates/page.html').read_text()
    header = (ROOT / 'templates/header.html').read_text()
    footer = (ROOT / 'templates/footer.html').read_text()
    for page in pages:
        nav = header
        if page.get('nav'):
            nav = nav.replace(f'data-page="{page["nav"]}"', 'aria-current="page"')
        schema = (ROOT / 'content' / page['schema']).read_text() if page.get('schema') else ''
        # JPG card: WebP previews are not supported by every social platform.
        og_image = 'https://www.bimfarers.com.au/assets/social-card.jpg'
        og_image_size = '<meta property="og:image:width" content="1200">\n  <meta property="og:image:height" content="630">'
        if schema:
            data = json.loads(re.search(r'<script[^>]*>(.*?)</script>', schema, re.S).group(1))
            og_image = data['image']['url']
            og_image_size = ''
        jsonld = (ROOT / 'content' / page['jsonld']).read_text() if page.get('jsonld') else ''
        canonical = 'https://www.bimfarers.com.au/' + (page['file'][:-5] if page['file'] != 'index.html' else '')
        indexable = not page.get('noindex')
        values = {
            'title': html.escape(page['title']),
            'description': html.escape(page['description'], quote=True),
            'canonical_link': f'<link rel="canonical" href="{canonical}">' if indexable else '',
            'og_url': f'<meta property="og:url" content="{canonical}">' if indexable else '',
            'og_image_size': og_image_size,
            'robots': '<meta name="robots" content="noindex">' if page.get('noindex') else '',
            'header': nav, 'footer': footer,
            'navigation_script': (ROOT / 'js/navigation.js').read_text(),
            'content': (ROOT / 'content' / page['file']).read_text(),
            'schema': schema + jsonld,
            'og_type': 'article' if schema else 'website',
            'og_image': og_image,
            'preload': '<link rel="preload" as="image" type="image/avif" href="/assets/optimized/hero-model-1280.avif" imagesrcset="/assets/optimized/hero-model-640.avif 640w, /assets/optimized/hero-model-1280.avif 1280w" imagesizes="(max-width: 760px) calc(100vw - 48px), 56vw" fetchpriority="high">' if page['file'] == 'index.html' else '',
        }
        output = shell
        for key, value in values.items():
            output = output.replace('{{' + key + '}}', value)
        # Inline arrows avoid platform/font-dependent missing glyphs.
        for symbol, path in {'↗': 'M4 12 12 4M4 4h8v8', '↑': 'M8 14V2M3 7l5-5 5 5', '←': 'M14 8H2m5-5L2 8l5 5'}.items():
            output = output.replace(symbol, f'<svg class="icon" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.25" aria-hidden="true"><path d="{path}"/></svg>')
        output = '\n'.join(line.rstrip() for line in output.splitlines()) + '\n'
        (ROOT / page['file']).write_text(output)
    print(f'Rendered {len(pages)} static HTML pages.')


if __name__ == '__main__':
    build()
