# Web font packaging

The approved design restores the original Inter 300 body, Inter 500 interface
and Inter 700 headline hierarchy, with a Work Sans 600 wordmark.

`inter-web-{300,500,700}.woff2` are small subsets of the corresponding original
`inter-v12-latin-*.woff2` files already present in this repository. They retain
kerning and cover printable English ASCII, common editorial punctuation and the
additional symbols listed in `scripts/prepare_hero_assets.py`. Characters outside
that set use the system fallback font. Expand the set if adding other languages.
The three font files total approximately 23 KB, versus 53 KB for the original
three full Latin weights. They are local assets and have no Google Fonts request.

`work-sans-brand.woff2` contains only the glyphs in “BIM Farers”. Its approximately
1.5 KB of font data is embedded in the stylesheet to avoid a separate blocking
font request. Its source was the Work Sans 600 file served by Google Fonts:
`https://fonts.gstatic.com/s/worksans/v24/QGY_z_wNahGAdqQ43RhVcIgYT2Xz5u32K5fQNig.ttf`.
The standalone WOFF2 is retained as the source for that embedding.

Licences: [Inter](OFL-Inter.txt), [Work Sans](OFL-Work-Sans.txt).

The optional asset-preparation script needs Pillow with AVIF support, fonttools
and brotli. It is not a dependency of the static website, normal HTML build or
deployment. Generated assets are committed. Changing the wordmark requires
regenerating its glyph subset; normal English headline/content edits do not.
