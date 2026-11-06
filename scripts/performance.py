#!/usr/bin/env python3
"""Optional controlled Chromium comparison against a separately served baseline.

python scripts/performance.py --before http://127.0.0.1:8001 --after http://127.0.0.1:8002
Requires Playwright and Chromium. Never sends form submissions or modifies sites.
Original external font/jQuery responses are mirrored in memory through urllib,
with normal TLS verification and the inherited environment proxy. This avoids
Chromium's separate proxy CA setup. These responses bypass CDP network throttling,
so baseline timings are optimistic and are not production field measurements.
"""
import argparse
import asyncio
import json
from pathlib import Path
import shutil
import statistics
import urllib.request
from playwright.async_api import async_playwright

METRICS = """window.audit={lcp:0,cls:0,ready:0};
new PerformanceObserver(l=>{for(const e of l.getEntries())audit.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)audit.cls+=e.value}).observe({type:'layout-shift',buffered:true});
function ready(){
 const h=document.querySelector('h1');const loader=document.querySelector('.loader-wrapper');
 let visible=!!h && (!loader || getComputedStyle(loader).display==='none');
 for(let el=h;el && visible;el=el.parentElement)if(Number(getComputedStyle(el).opacity)<.99)visible=false;
 if(visible && document.fonts.status==='loaded')audit.ready=performance.now();
 else requestAnimationFrame(ready);
}requestAnimationFrame(ready);"""


async def run(args):
    cache = {}
    async def mirror(route):
        url = route.request.url
        if not url.startswith('https:'):
            await route.continue_()
            return
        if url not in cache:
            def fetch():
                with urllib.request.urlopen(url, timeout=30) as response:
                    return response.read(), response.headers.get('Content-Type', 'application/octet-stream')
            cache[url] = await asyncio.to_thread(fetch)
        body, content_type = cache[url]
        await route.fulfill(body=body, content_type=content_type)

    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
        for viewport, width, height in [('mobile', 390, 844), ('desktop', 1440, 1000)]:
            for label, origin in [('before', args.before), ('after', args.after)]:
                for sample in range(args.runs):
                    context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=1)
                    page = await context.new_page()
                    errors = []
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    await page.route('**/*', mirror)
                    await page.add_init_script(METRICS)
                    cdp = await context.new_cdp_session(page)
                    await cdp.send('Network.enable')
                    await cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
                    await cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 150, 'downloadThroughput': 200000, 'uploadThroughput': 93750})
                    await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
                    await page.goto(origin, wait_until='networkidle', timeout=90000)
                    await page.wait_for_function('audit.ready > 0', timeout=30000)
                    await page.wait_for_timeout(1200)
                    data = await page.evaluate("""() => ({...audit,fcp:performance.getEntriesByName('first-contentful-paint')[0]?.startTime,localResourceBytes:performance.getEntriesByType('resource').reduce((n,r)=>n+r.decodedBodySize,0),requests:performance.getEntriesByType('resource').length})""")
                    assert not errors, errors
                    row = {'viewport': viewport, 'version': label, 'sample': sample + 1, **data}
                    results.append(row)
                    print(json.dumps(row), flush=True)
                    await context.close()
        await browser.close()
    summary = []
    for viewport in ['mobile', 'desktop']:
        for label in ['before', 'after']:
            rows = [r for r in results if r['viewport'] == viewport and r['version'] == label]
            summary.append({'viewport': viewport, 'version': label, **{k: round(statistics.median(r[k] for r in rows), 3) for k in ['fcp', 'lcp', 'cls', 'ready', 'localResourceBytes', 'requests']}})
    Path(args.output).write_text(json.dumps({'conditions': 'Cold Chromium; 150ms RTT, 1.6Mbps down, 4x CPU; external baseline responses mirrored in memory and not CDP-throttled.', 'runs': results, 'medians': summary, 'externalMirrors': {k: len(v[0]) for k,v in cache.items()}}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', required=True)
    parser.add_argument('--after', default='http://127.0.0.1:8000')
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--output', default='/tmp/bim-performance.json')
    asyncio.run(run(parser.parse_args()))
