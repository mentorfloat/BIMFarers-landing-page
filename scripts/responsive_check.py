#!/usr/bin/env python3
"""Check the approved hero at breakpoints, short screens, zoom and no-JS.

Requires Playwright. Use --browser firefox or webkit when those engines and
their system dependencies are installed; default is installed Chromium.
"""
import argparse
import asyncio
from functools import partial
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
from threading import Thread
from preview import Handler, ROOT
from playwright.async_api import async_playwright

SIZES = [(320,568),(360,640),(375,667),(390,844),(414,896),(480,800),
         (600,960),(760,900),(761,900),(768,1024),(820,1180),(900,900),
         (1024,768),(1100,800),(1280,720),(1366,768),(1440,900),
         (1600,900),(1920,1080),(2560,1440),(667,375),(844,390),(1024,600)]
PROBE = """() => {
 const rect = e => {const r=e.getBoundingClientRect();return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height}};
 const model=document.querySelector('.hero-model img'),people=document.querySelector('.hero-people img');
 const targets=[document.querySelector('.hero-title .soft'),document.querySelector('.hero-intro'),document.querySelector('.hero-copy .button')];
 const photo=rect(people);
 const overlaps=targets.filter(e=>{const r=rect(e);return r.left<photo.right-1&&r.right>photo.left+1&&r.top<photo.bottom-1&&r.bottom>photo.top+1}).map(e=>e.className);
 return {overflow:document.documentElement.scrollWidth>innerWidth,model:rect(model),people:photo,button:rect(targets[2]),overlaps,
 loaded:[model,people].every(i=>i.complete&&i.naturalWidth>0),
 modelSource:model.currentSrc,peopleSource:people.currentSrc,
 fonts:[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family)};
}"""


async def check(args):
    output = Path(tempfile.mkdtemp(prefix='bim-responsive-'))
    server = ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    results=[]
    async with async_playwright() as p:
        browser_type=getattr(p,args.browser)
        options={'executable_path':shutil.which('chromium'),'args':['--no-sandbox']} if args.browser=='chromium' else {}
        browser=await browser_type.launch(**options)
        page=await browser.new_page()
        for width,height in SIZES:
            await page.set_viewport_size({'width':width,'height':height})
            await page.goto(origin,wait_until='networkidle')
            await page.evaluate('document.fonts.ready')
            await page.locator('.hero-people img').evaluate('(i)=>i.decode()')
            data=await page.evaluate(PROBE)
            assert not data['overflow'],(width,height,'horizontal overflow')
            assert not data['overlaps'],(width,height,'people cover copy',data['overlaps'])
            assert data['loaded'],(width,height,'images failed')
            # First-screen guarantee at normal phone/laptop/desktop sizes.
            # Landscape, tablets and enlarged text may scroll vertically.
            first_screen=(width<=480 and height>=568) or (width>=1280 and height>=720)
            if first_screen:
                for target in ['model','people','button']:
                    assert data[target]['bottom']<=height+1,(width,height,target,data[target])
            results.append({'width':width,'height':height,'firstScreenRequired':first_screen,**data})
            if (width,height) in [(375,667),(390,844),(768,1024),(1366,768),(1440,900)]:
                await page.screenshot(path=str(output/f'{args.browser}-{width}x{height}.png'))
        # 200% page zoom reduces the CSS viewport and exercises natural reflow.
        # Text-only zoom enlarges CSS typography without shrinking the viewport.
        for width,height in [(640,400),(720,450)]:
            await page.set_viewport_size({'width':width,'height':height})
            await page.goto(origin,wait_until='networkidle')
            assert not (await page.evaluate(PROBE))['overflow']
        for width,height in [(390,844),(768,1024),(1440,900)]:
            await page.set_viewport_size({'width':width,'height':height})
            await page.goto(origin,wait_until='networkidle')
            await page.evaluate("""() => {
                const values=[...document.querySelectorAll('body *')].filter(e=>!(e instanceof SVGElement)).map(e=>[e,parseFloat(getComputedStyle(e).fontSize)]);
                for(const [e,n] of values)e.style.fontSize=`${n*2}px`;
            }""")
            data=await page.evaluate(PROBE)
            assert not data['overflow'],(width,'200% text zoom overflow')
            assert not data['overlaps'],(width,'200% text zoom overlap',data['overlaps'])
            assert await page.locator('.hero-copy .button').is_visible()
        await page.close()
        for scale in [2,3]:
            context=await browser.new_context(viewport={'width':390,'height':844},device_scale_factor=scale)
            page=await context.new_page();await page.goto(origin,wait_until='networkidle')
            assert (await page.evaluate(PROBE))['loaded']
            await context.close()
        page=await browser.new_page(viewport={'width':390,'height':844})
        await page.goto(origin,wait_until='networkidle')
        await page.locator('.hero source[type="image/avif"]').evaluate_all('(sources)=>sources.forEach(s=>s.remove())')
        await page.locator('.hero-model img').evaluate('(i)=>i.decode()')
        await page.locator('.hero-people img').evaluate('(i)=>i.decode()')
        fallback=await page.evaluate(PROBE)
        assert fallback['loaded'] and fallback['modelSource'].endswith('.webp') and fallback['peopleSource'].endswith('.webp')
        await page.close()
        await browser.close()
    server.shutdown()
    (output/'results.json').write_text(json.dumps(results,indent=2))
    print(f'PASS: {args.browser}, {len(SIZES)} screen sizes, landscape, 200% reflow/text zoom, DPR 2/3, WebP fallback. Evidence: {output}')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--browser',choices=['chromium','firefox','webkit'],default='chromium')
    asyncio.run(check(parser.parse_args()))
