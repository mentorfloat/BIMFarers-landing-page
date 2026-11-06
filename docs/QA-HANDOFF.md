# QA handoff — modern minimal refresh

Review branch: `design/modern-minimal-refresh`.
Compare against baseline `7cf7a55dacc0eb5e379b5edb786f3596a1ee9d03` on `main`.
Do not merge or deploy while reviewing. Production is `main`, not `master`.

## Approved hero update

The owner selected option A: a smaller real team photograph overlaps the model
on desktop and sits beneath it on mobile. See [responsive verification](RESPONSIVE-QA.md)
and [updated performance evidence](OPTION-A-PERFORMANCE.md). Shared typography now
uses three small original Inter subsets (300/500/700) and the Work Sans wordmark.
`js/navigation.js` is inserted inline after the header to avoid a late menu collapse;
the remaining deferred `js/site.js` only adds optional section movement.

## Scope and architecture

- Ten redesigned root HTML pages. Existing filenames and extensionless routes
  remain usable. Shared navigation now labels About as Practice, Blog as Journal
  and Plugins as Revit tools.
- `content/` + `templates/` are source. `scripts/build.py` emits checked-in root
  HTML with no external Python dependencies. Edit source, rebuild, commit both.
- `css/site.css` and `js/site.js` are the only active local stylesheet/script.
  Inter WOFF2 subsets are self-hosted, and the tiny wordmark font is embedded in CSS. Image derivatives are committed;
  originals remain. No image processing is needed to build or deploy.
- Desktop/mobile navigation uses normal links. The menu becomes collapsible
  only when JS successfully initialises; without JS all links remain visible.
- Optional section animation never sets opacity to zero or hides content.
- The privacy policy and published article text remain original. All original
  article paragraphs were compared against the baseline and retained. Articles
  keep their 2023 dates and BlogPosting schema.
- `map.html` and old unreferenced CSS/JS/media are retained for a later cleanup.
  They are outside the redesigned page load path and static-page check list.

## Reproduce checks

```sh
python scripts/build.py
python scripts/check.py
python scripts/preview.py --port 8000
```

Optional Playwright checks (instructions in README):

```sh
python scripts/browser_check.py
```

The browser suite passed in installed Chromium on Linux, at 320, 390, 768 and
1440 CSS pixels. It checks all ten redesigned pages, horizontal overflow, images,
console errors, failed resource responses, first-party-only loads, keyboard menu
operation and Escape, anchor clearance, nested 404 assets, no-JS navigation on all
pages, and reduced-motion behaviour. Screenshots are generated after scrolling
to load native lazy images. This is not a full accessibility certification or a
cross-browser guarantee.

The static suite checks internal paths/fragments, unique IDs, one h1 per page,
image dimensions/alt attributes, JSON-LD validity and load budgets. CI also checks
that a fresh build does not change generated HTML.

## Review priorities

1. **Loading:** hero image priority/srcset and preload must agree. No new network
   origins, font weights, JS libraries, render gates or autoplay media. Check
   cold and repeat views on an actual mid-range phone. Re-run the controlled
   comparison in PERFORMANCE.md, and use production-like compression when a
   preview environment is available.
2. **Responsive layout:** check long article titles, project captions, credential
   logos, team photos, menu wrapping and office addresses at intermediate widths,
   200% text zoom, landscape phones and Safari. Every loaded image should retain
   its expected aspect ratio. Gallery frames intentionally crop to 4:5.
3. **Navigation/accessibility:** keyboard-visible focus, skip link, mobile Menu
   open/close/resize, no hidden focus targets, reduced motion, no JS and blocked
   image/font cases. Check actual screen-reader behaviour and colour contrast.
   The mobile menu is an inline disclosure, not a modal, so it has no focus trap.
4. **Content preservation:** compare all three articles and the privacy policy.
   Two old article reference problems (duplicate/missing targets) were corrected.
   The payment-return page now asks visitors to verify status in PayPal/email;
   a static page cannot verify payment by itself.
5. **Business review:** confirm current team/credentials, both addresses, phone,
   project participation and image usage. Review all shortened marketing copy.
   Validate live Autodesk listings before adding specific compatibility/pricing
   claims. No new statistics, client testimonials or project outcomes were made up.
6. **Hosting:** the site assumes domain-root hosting. Verify existing clean URLs,
   `www` domain redirection, canonical/social metadata and the sitemap before
   release. Old article schema uses the existing apex URLs. New canonical tags
   use the configured `www` domain; confirm how production redirects both forms.
7. **Deployment:** `.github/workflows/static.yml` now explicitly refuses any
   branch other than `main`, even for manual runs. The validation workflow has no
   Pages write permission and does not deploy. Confirm these settings in GitHub.

## Intentional limits

- There is no public preview deployment, PR merge, analytics installation or new
  external service connection in this iteration.
- The 2023 journal entries are archived, not rewritten as current advice.
- Legacy counters and the old partner-logo strip are omitted pending verification.
  Existing credential badges are retained for the owner to verify.
- The gallery has no dead “view project” buttons; full case studies need real
  scope and outcome material before implementation.
- Performance numbers are laboratory observations, not field Core Web Vitals.
  The script's mirrored baseline external assets are explicitly documented.
