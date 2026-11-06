# Performance evidence — first redesign

For the subsequently approved overlapping team-photo hero, see
[the option A comparison](OPTION-A-PERFORMANCE.md). This document preserves the
initial full-site baseline comparison.

The homepage comparison shows a substantial improvement in this controlled
environment, with no observed loading regression. These results are not field
Core Web Vitals and do not guarantee a timing on every device or connection.
Repeat against a production-like preview before release.

## Asset changes

Decimal KB, uncompressed source file sizes; these are not CDN transfer sizes.

| Asset | Baseline | Redesign |
| --- | ---: | ---: |
| Active stylesheet | 295.1 KB | 15.4 KB |
| Local homepage scripts | 94.7 KB | 1.9 KB |
| External jQuery script | 89.8 KB | 0 |
| Local type weights | 3 × WOFF2, 52.7 KB total | 1 × WOFF2, 17.6 KB |
| External Google Fonts stylesheet/font | Additional requests | 0 |
| Hero model, desktop | 235.4 KB | 58.2 KB |
| Hero model, mobile | 235.4 KB background | 23.7 KB responsive image |
| About hero photo | 444.9 KB | 75.5 KB desktop / 26.8 KB mobile |
| Homepage HTML | 37.8 KB | About 16 KB |

The new CSS compresses to approximately 4 KB with gzip and JS to 0.75 KB. Actual
hosting compression and response headers were not measured here. Original assets
remain in the repository but are not requested by the redesigned pages.

## Controlled homepage comparison

Captured 6 November 2026 in Chromium on Linux. Three fresh browser contexts per
version at each viewport. Cold browser cache, 150 ms emulated latency, 1.6 Mbps
download, 0.75 Mbps upload and 4× CPU slowdown. Desktop: 1440×1000; mobile:
390×844, device scale factor 1. No scrolling or input during timing capture.
Values below are medians, rounded for readability.

| Measurement | Mobile before | Mobile after | Desktop before | Desktop after |
| --- | ---: | ---: | ---: | ---: |
| First contentful paint | 4.09 s | 0.92 s | 4.10 s | 0.95 s |
| Largest contentful paint | 9.61 s | 0.92 s | 14.00 s | 1.01 s |
| Headline ready, font loaded, loader gone | 13.53 s | 0.87 s | 13.84 s | 0.93 s |
| Locally reported resource body bytes | 2.33 MB | 0.40 MB | 2.37 MB | 0.43 MB |
| Resource entries (excluding document) | 18 | 12 | 19 | 12 |

No layout shifts were observed on the redesigned homepage in these runs. The
baseline mobile shift was approximately 0.000368. Resource totals include native
lazy images the browser elected to fetch near the viewport; they are not a
carefully isolated “above-the-fold bundle”. Cross-origin baseline resource body
sizes are not exposed by Resource Timing and are excluded from the byte totals.
Thus the baseline totals omit its external Google Fonts and jQuery bytes.

The loader itself can count towards first paint/LCP, so those metrics alone do
not express the original site's perceived readiness. The additional ready probe
checks that the headline exists, its ancestors are opaque, fonts have finished
loading and the loader is no longer displayed. This probe is a local diagnostic,
not a standard Web Vital or a measure of full-page interactivity.

### Important test constraints

- Local Python HTTP servers were used with uncompressed responses. Absolute
  numbers exaggerate transfer costs compared with a compressed CDN and must not
  be presented as production speeds.
- Chromium did not initially trust the environment's external proxy CA. The
  comparison therefore mirrors the original external Google Fonts and jQuery
  responses in memory using Python's normal TLS-verified HTTP client and inherited
  proxy. Both original scripts/fonts successfully execute/load; no mock code is
  substituted. These mirrored responses bypass CDP network throttling, making
  baseline timings optimistic for that part of the load. The redesign has no
  such external dependencies. TLS verification was not disabled.
- The original Google Fonts response was selected by urllib's default user agent
  and supplied a Work Sans TTF. A production browser may negotiate different
  font formats. This limits precision of the baseline's external-font cost.
- Results cover the first homepage iteration; final metadata, footer contact
  details and whitespace cleanup are small subsequent changes. Budgets and
  browser integrity checks cover the completed branch. This is evidence of the
  direction and scale of improvement, not a release certification.
- Chromium desktop emulation is not a real low-end phone, Safari or Firefox.
  Background server load and browser scheduling introduce variance.

Raw observations: [performance-results.json](performance-results.json).

## Reproduce

Use a separate baseline worktree so neither version needs to be overwritten:

```sh
git worktree add --detach /tmp/bim-before 7cf7a55dacc0eb5e379b5edb786f3596a1ee9d03
python -m http.server 8001 --bind 127.0.0.1 --directory /tmp/bim-before
```

In a second terminal on the redesign branch:

```sh
python scripts/build.py
python scripts/preview.py --port 8002
```

With Playwright and Chromium installed, in a third terminal:

```sh
python scripts/performance.py --before http://127.0.0.1:8001 --after http://127.0.0.1:8002 --runs 3 --output /tmp/bim-performance.json
```

## Guardrails for subsequent iterations

- Keep the initial screen fully visible without JS and without an entrance
  animation. Never wait for `window.load` to remove a covering element.
- Keep critical CSS ≤20 KB, deferred JS ≤3 KB, homepage HTML ≤30 KB and model
  images ≤30/60 KB mobile/desktop. These budgets run in CI.
- Preload only the selected responsive hero and one font. Keep image dimensions,
  native lazy loading below the hero and a useful fallback font.
- Do not add third-party embeds, animation libraries, additional type weights,
  video, trackers or a client-rendered framework without measuring their cost.
- Before release, compare compressed previews under identical conditions, check
  repeat visits and collect real-user performance if an appropriate analytics
  approach is agreed. Do not install analytics just to complete this design task.
