#!/usr/bin/env python3
"""Regenerate review previews in docs/previews and the social card.

Optional (pip install playwright). Starts its own local preview server, renders
at 2x and downsamples, so images stay sharp without bloating the repository.
    python scripts/make_previews.py            # previews + assets/social-card.jpg
"""
import asyncio
from functools import partial
from http.server import ThreadingHTTPServer
import io
import shutil
from threading import Thread
from PIL import Image
from playwright.async_api import async_playwright
from preview import Handler, ROOT

OUT = ROOT / 'docs/previews'
# (file, page, viewport width, viewport height, full page, output width)
SHOTS = [
    ('desktop.jpg', '/', 1440, 900, False, 1440),
    ('mobile.png', '/', 390, 844, False, 390),
    ('small-mobile.png', '/', 375, 667, False, 375),
    ('home-full.jpg', '/', 1440, 900, True, 800),
    ('tools-full.jpg', '/automation.html', 1440, 900, True, 800),
    ('practice-full.jpg', '/aboutus.html', 1440, 900, True, 800),
    ('journal-full.jpg', '/blog.html', 1440, 900, True, 800),
    ('home-mobile-full.jpg', '/', 390, 844, True, 390),
]
PALETTE = [  # Taken from the Canva logo and proposal designs.
    ('Navy', '#060d4e', 'Proposals · dark sections, buttons'),
    ('Charcoal', '#212529', 'Logo sail · text'),
    ('Azure', '#0a8ae6', 'Logo wave · links, focus, labels'),
    ('Crimson', '#f40042', 'Logo sail · signature accent'),
    ('Periwinkle', '#6767bd', 'Proposal ribbon lines'),
    ('Paper', '#f5f6f9', 'Page background'),
]


def palette_html():
    cells = ''.join(
        f'<div class="s"><div class="c" style="background:{hex_}"></div><b>{name}</b>'
        f'<code>{hex_}</code><small>{use}</small></div>' for name, hex_, use in PALETTE)
    return ('<link rel="stylesheet" href="/css/site.css"><style>body{padding:40px}'
            '.g{display:grid;grid-template-columns:repeat(6,1fr);gap:20px}.c{height:120px;'
            'border:1px solid var(--line)}.s b{display:block;margin-top:14px;font-weight:500}'
            '.s code{font:500 12px var(--mono)}.s small{display:block;color:var(--muted);'
            'font-size:12px;margin-top:6px}</style><p class="eyebrow">BIM Farers brand palette'
            f'</p><div class="g" style="margin-top:24px">{cells}</div>')


def social_html():
    return ('<link rel="stylesheet" href="/css/site.css"><style>'
            'body{margin:0;width:1200px;height:630px;overflow:hidden;background:var(--navy);color:#fff;'
            'position:relative}body::before{content:"";position:absolute;inset:0;'
            'background:url(/assets/waves.svg) 30% 70%/1900px auto no-repeat;opacity:.9}'
            '.copy{position:absolute;left:72px;top:64px;width:520px}.brand{font-size:30px;color:#fff}'
            'h1{font-size:62px;font-weight:700;letter-spacing:-.05em;line-height:1.02;margin:64px 0 0}'
            'h1 span{font-weight:300;color:var(--on-navy)}.eyebrow{color:var(--azure);margin-top:32px}'
            '.model{position:absolute;right:56px;top:120px;width:560px;background:#dde1e9}'
            '.model img{width:100%;mix-blend-mode:multiply}</style>'
            '<div class="copy"><span class="brand"><img src="/assets/brand.svg" width="34" '
            'height="38" alt="">BIM Farers</span><h1>Better coordinated.<br><span>Ready to build.'
            '</span></h1><p class="eyebrow">Engineering · BIM · Revit automation<br>'
            'Melbourne + Kuala Lumpur</p></div><div class="model">'
            '<img src="/assets/optimized/hero-model-1280.webp" alt=""></div>')


def save(png, path, width):
    image = Image.open(io.BytesIO(png)).convert('RGB')
    image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    if path.suffix == '.png':
        image.save(path, optimize=True)
    else:
        image.save(path, quality=80, optimize=True, progressive=True)
    print(f'{path.relative_to(ROOT)} {image.size[0]}x{image.size[1]}')


async def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
        for name, url, width, height, full, out_width in SHOTS:
            page = await browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=2)
            await page.goto(origin + url, wait_until='networkidle')
            # Load native lazy images, then return to the top for the capture.
            await page.evaluate("""async () => {
                for (let y = 0; y < document.body.scrollHeight; y += 700) {
                    scrollTo(0, y); await new Promise(r => setTimeout(r, 50)); }
                await Promise.all([...document.images].map(i => Promise.race([i.decode().catch(() => {}), new Promise(r => setTimeout(r, 5000))])));
                scrollTo(0, 0); await document.fonts.ready; }""")
            await page.wait_for_timeout(200)
            save(await page.screenshot(full_page=full), OUT / name, out_width)
            await page.close()
        for name, html, size, target in [
            ('palette.png', palette_html(), (1200, 330), OUT / 'palette.png'),
            ('social', social_html(), (1200, 630), ROOT / 'assets/social-card.jpg'),
        ]:
            page = await browser.new_page(viewport={'width': size[0], 'height': size[1]}, device_scale_factor=2)
            await page.goto(origin + '/404.html')  # same origin, so relative asset URLs resolve
            await page.set_content(html, wait_until='networkidle')
            await page.evaluate('document.fonts.ready')
            save(await page.screenshot(), target, size[0])
            await page.close()
        await browser.close()
    server.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
