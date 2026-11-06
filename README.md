# BIM Farers website

Static HTML, CSS and a small progressive-enhancement script. No framework, package
manager, animation library or production build service is required.

This iteration lives on `design/modern-minimal-refresh`. **Do not merge or deploy
it until the design, content and QA review are complete.** The production branch
is `main` (the repository does not use `master`).

![Desktop design preview](docs/previews/desktop.jpg)

- [Design audit and recommendations](docs/DESIGN-REVIEW.md)
- [QA handoff for Claude or another reviewer](docs/QA-HANDOFF.md)
- [Current performance evidence](docs/OPTION-A-PERFORMANCE.md)
- [Original full-site performance comparison](docs/PERFORMANCE.md)
- [Mobile preview](docs/previews/mobile.png)

## Edit and preview

```sh
git switch design/modern-minimal-refresh
python scripts/build.py
python scripts/check.py
python scripts/preview.py --port 8000
```

Open `http://127.0.0.1:8000`. The preview server supports both `.html` and the
existing extensionless URLs. A plain static server also serves the `.html` links.
The site assumes hosting at the root of its domain, as configured by `CNAME`.

Edit these source files, then run `python scripts/build.py` and commit the
generated root HTML files alongside the source:

| Area | Source |
| --- | --- |
| Page content | `content/*.html` |
| Titles, descriptions and navigation state | `content/pages.json` |
| Shared document, header and footer | `templates/*.html` |
| Layout, colours, responsive rules and motion | `css/site.css` |
| Mobile menu / optional section motion | `js/navigation.js` (inlined) / `js/site.js` |
| Optimised images | `assets/optimized/` |

The generator only shares the HTML shell. It uses Python's standard library and
emits ready-to-serve HTML; Python is not needed by the deployed site. Original
images and unused legacy assets remain available for comparison. The old
`map.html` remains accessible but is no longer embedded by the site.

The approved hero is option A: the team photo overlaps the model on desktop and
tucks below it on phones. Typography restores the original light/bold Inter
weights and Work Sans wordmark. Menu code in `js/navigation.js` is inserted at
the end of the header, so it initialises before the main content can paint and
avoids a late menu collapse. `js/site.js` only adds optional below-fold motion.
Fonts and images are committed, optimised assets; their preparation script is
optional. See [font packaging](fonts/README.md) and
[responsive evidence](docs/RESPONSIVE-QA.md).

## Optional browser checks

Install Playwright in your own development environment, then use installed
Chromium or install Playwright's browser:

```sh
python -m pip install playwright
python -m playwright install chromium
python scripts/browser_check.py
python scripts/responsive_check.py
```

This checks all ten redesigned pages at four widths, image loading, browser
errors, third-party requests, keyboard navigation, no-JavaScript use, reduced
motion and the nested 404. Screenshots are written to a temporary directory.
The responsive suite additionally exercises 23 viewport sizes, landscape,
200% text enlargement, reflow, retina image selection and WebP fallbacks.

`scripts/check.py` runs in GitHub Actions on iteration-branch pushes and PRs. It
checks links, assets, anchors, schema, image dimensions and size budgets. The
deployment workflow only permits `refs/heads/main`, including manual runs.
