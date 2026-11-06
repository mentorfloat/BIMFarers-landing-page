#!/usr/bin/env python3
"""Optional browser QA: pip install playwright; python scripts/browser_check.py.

Uses installed Chromium or Playwright's downloaded browser. Starts its own local
preview. Output and screenshots stay outside the deployed site by default.
"""
import asyncio
from functools import partial
import json
from pathlib import Path
import shutil
import tempfile
from threading import Thread
from http.server import ThreadingHTTPServer
from preview import Handler, ROOT
from playwright.async_api import async_playwright


async def check():
    output = Path(tempfile.mkdtemp(prefix='bim-browser-'))
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    pages = json.loads((ROOT / 'content/pages.json').read_text())
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
        for width in [320, 390, 768, 1440]:
            context = await browser.new_context(viewport={'width': width, 'height': 900})
            page = await context.new_page()
            errors, failures, external = [], [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('response', lambda response: failures.append(response.url) if response.status >= 400 else None)
            page.on('request', lambda request: external.append(request.url) if not request.url.startswith(origin) else None)
            for spec in pages:
                await page.goto(f'{origin}/{spec["file"]}', wait_until='networkidle')
                assert await page.locator('h1').count() == 1, spec['file']
                assert await page.locator('h1').is_visible()
                assert not await page.evaluate('document.documentElement.scrollWidth > innerWidth'), (width, spec['file'])
                # Scroll normally so native lazy images can load before checking them.
                await page.evaluate("""async () => {
                    for (let y = 0; y < document.body.scrollHeight; y += 700) {
                        window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60));
                    }
                    // Cap the wait: an image that never loads (e.g. hidden + lazy) is reported below, not hung on.
                    await Promise.all([...document.images].map(i => Promise.race([i.decode().catch(() => {}), new Promise(r => setTimeout(r, 5000))])));
                    window.scrollTo(0, 0);
                }""")
                broken = await page.locator('img').evaluate_all('(images) => images.filter(i => !i.complete || !i.naturalWidth).map(i => i.src)')
                assert not broken, (spec['file'], broken)
                if width in [390, 1440] and spec['file'] in ['index.html', 'aboutus.html', 'automation.html', '1-building-information-modelling.html']:
                    await page.screenshot(path=str(output / f'{width}-{spec["file"]}.png'), full_page=True)
            assert not errors, errors
            assert not failures, failures
            assert not external, external
            await context.close()
        # Mobile menu: keyboard, Escape, real navigation and responsive focus.
        context = await browser.new_context(viewport={'width': 390, 'height': 844})
        page = await context.new_page()
        await page.goto(origin)
        toggle = page.get_by_role('button', name='Menu')
        await toggle.focus()
        await page.keyboard.press('Enter')
        assert await toggle.get_attribute('aria-expanded') == 'true'
        await page.keyboard.press('Tab')
        assert await page.get_by_role('link', name='Projects', exact=True).evaluate('(a) => a === document.activeElement')
        await page.keyboard.press('Escape')
        assert await toggle.get_attribute('aria-expanded') == 'false'
        assert await toggle.evaluate('(a) => a === document.activeElement')
        await toggle.click()
        await page.get_by_role('link', name='Projects', exact=True).click()
        assert await toggle.get_attribute('aria-expanded') == 'false'
        await page.wait_for_timeout(100)
        assert await page.locator('#projects').evaluate('(e) => e.getBoundingClientRect().top >= 70')
        await page.goto(origin + '/unknown/nested/page')
        assert await page.get_by_role('heading', level=1).inner_text() == 'A little off plan.'
        assert await page.locator('.site-header img').evaluate('(i) => i.complete && i.naturalWidth > 0')
        await context.close()
        # No JS: full navigation and all content remain usable on mobile.
        context = await browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844})
        page = await context.new_page()
        for spec in pages:
            await page.goto(f'{origin}/{spec["file"]}', wait_until='networkidle')
            assert await page.get_by_role('link', name='Practice', exact=True).is_visible()
            assert await page.locator('h1').is_visible()
        await context.close()
        # Reduced motion has no active animation even after scrolling.
        context = await browser.new_context(reduced_motion='reduce')
        page = await context.new_page()
        await page.goto(origin)
        await page.locator('#projects').scroll_into_view_if_needed()
        assert await page.locator('.is-entering').count() == 0
        assert await page.evaluate('document.getAnimations().length') == 0
        await context.close()
        await browser.close()
    server.shutdown()
    print(f'PASS: 40 page/viewport checks, images, console, third-party requests, mobile keyboard menu, nested 404, no-JS and reduced motion. Screenshots: {output}')


if __name__ == '__main__':
    asyncio.run(check())
