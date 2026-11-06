# Approved option A — loading comparison

Compared with the previous iteration commit `a747821` on this branch. Production
`main` remains at the original site. This update adds the smaller team image,
restores the original font-weight hierarchy and fixes mobile menu layout shift.

## What keeps it small

- Inter 300/500/700 are subsets of the original local font files: 7.7, 7.8 and
  7.9 KB, approximately 23.3 KB total. This preserves the approved typography
  without downloading the original 52.7 KB of full Latin fonts.
- The Work Sans wordmark uses a 1.5 KB glyph subset embedded in the stylesheet,
  avoiding another font round trip. It makes no Google Fonts request.
- The model is delivered as responsive AVIF: 8.6 KB at 640 pixels or 24.5 KB at
  1280 pixels, versus 23.7 / 58.2 KB in the previous iteration. WebP alternatives
  remain available for browsers that do not select AVIF.
- The team photograph is 7.3 KB / 20.2 KB in AVIF at 320 / 640 pixels. Responsive
  sources select an appropriate size, with WebP alternatives.
- Only the model has high fetch priority. The team image uses low fetch priority
  and asynchronous decoding. Images reserve their dimensions before download.
- Total source CSS remains below 20 KB, including the embedded wordmark font;
  combined menu/motion JS remains below 3 KB. The tiny menu script is inserted
  immediately after the header to prevent a late mobile menu collapse. Section
  animation remains deferred and optional.
- The stylesheet is discovered before the font/image preloads in the document
  head. There is no hero entrance animation, loader or external loading dependency.

## Final comparison

Cold Chromium contexts, three runs per version and viewport. Both local preview
servers enable gzip for text assets. Emulated network: 150 ms latency, 1.6 Mbps
download, 0.75 Mbps upload; CPU slowdown 4×. Mobile: 390×844, desktop: 1440×1000,
device scale factor 1. No scrolling or interaction during capture.

| Median | Mobile before | Mobile option A | Desktop before | Desktop option A |
| --- | ---: | ---: | ---: | ---: |
| First contentful paint | 0.872 s | 0.808 s | 0.784 s | 0.848 s |
| Largest contentful paint | 0.980 s | 0.808 s | 0.904 s | 0.860 s |
| Headline/font readiness probe | 0.977 s | 0.752 s | 0.839 s | 0.809 s |
| Cumulative layout shift | 0.038 | 0 | 0.004 | 0 |
| Resource entries, excluding document | 12 | 15 | 12 | 15 |

No LCP regression was observed in this final comparison. First-paint results vary:
desktop FCP was 64 ms later, while mobile FCP was earlier. These are small local
samples, not an absolute guarantee that every loading metric is unchanged on
every connection. Earlier captures varied by tens of milliseconds between runs;
all final hero LCP medians remain below one second in this setup. The original
production site comparison and its much heavier runtime are recorded separately
in [PERFORMANCE.md](PERFORMANCE.md).

The headline-readiness probe checks the headline, font loading and any loader;
it is a diagnostic, not a standard Web Vital. The revised page has no loader.
The original branch's menu collapse was an observed source of layout shift; its
replacement now initialises inline before the main content can paint.

Raw observations: [option-a-performance-results.json](option-a-performance-results.json).

## Reproduce against the previous iteration

```sh
git worktree add --detach /tmp/bim-a-before a747821
python scripts/preview.py --directory /tmp/bim-a-before --port 8014 --gzip
```

In a second terminal:

```sh
python scripts/build.py
python scripts/preview.py --port 8015 --gzip
```

In a third terminal with Playwright and Chromium installed:

```sh
python scripts/performance.py --before http://127.0.0.1:8014 --after http://127.0.0.1:8015 --runs 3 --output /tmp/bim-option-a.json
```

`preview.py --gzip` approximates compressed static hosting. It does not reproduce
GitHub Pages' CDN, connection reuse, geographical latency or browser hardware.
Production has not been deployed as part of this update. Confirm real-device
behaviour before release, alongside the [responsive checks](RESPONSIVE-QA.md).
