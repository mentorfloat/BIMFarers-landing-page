#!/usr/bin/env python3
"""Optional asset preparation, never run at request/build time.

Requires Pillow with AVIF support, fonttools and brotli. Source images and original
Inter fonts are already in this repository. Generated assets are checked in.
"""
import base64
from pathlib import Path
import re
from PIL import Image
from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
UNICODES=list(range(0x20,0x7f))+[0xA0,0xA9,0xB0,0xB2,0xD7,0xE9,0x2013,0x2014,0x2018,0x2019,0x201c,0x201d,0x2022,0x2026,0x20ac]


def prepare():
    for weight in [300,500,700]:
        font=TTFont(ROOT/f'fonts/inter-v12-latin-{weight}.woff2')
        options=Options()
        options.layout_features=['kern']
        options.hinting=False
        subset=Subsetter(options=options)
        subset.populate(unicodes=UNICODES)
        subset.subset(font)
        font.flavor='woff2'
        font.save(ROOT/f'fonts/inter-web-{weight}.woff2')
    for label,source in [('model','assets/RevitRender2.webp'),('team','assets/photo/HRes-CandidGroup2.webp')]:
        image=Image.open(ROOT/source).convert('RGB')
        if label=='team':
            image=image.crop((0,350,2160,1410))
        for width in ([640,1280] if label=='model' else [320,640]):
            resized=image.resize((width,round(image.height*width/image.width)),Image.Resampling.LANCZOS)
            for extension in ['avif','webp']:
                quality=(38 if width==640 else 40) if label=='model' and extension=='avif' else 45 if label=='model' else 60 if extension=='avif' else 68
                resized.save(ROOT/f'assets/optimized/hero-{label}-{width}.{extension}',quality=quality)
    css=ROOT/'css/site.css'
    brand=base64.b64encode((ROOT/'fonts/work-sans-brand.woff2').read_bytes()).decode()
    css.write_text(re.sub(r'url\(data:font/woff2;base64,[A-Za-z0-9+/=]+\)',f'url(data:font/woff2;base64,{brand})',css.read_text()))
    print('Prepared hero images, font subsets and embedded wordmark font.')


if __name__=='__main__':
    prepare()
