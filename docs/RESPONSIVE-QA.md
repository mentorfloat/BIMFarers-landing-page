# Approved option A — responsive verification

Implemented on `design/modern-minimal-refresh` after owner approval. Production
`main` is not modified or deployed by this update.

The implementation preserves the approved desktop overlap and the mobile photo
position beneath the model. At intermediate tablet widths the photo stays inside
the model's column to avoid covering the introduction. On phones, the two images
appear before the short description and enquiry button.

## Verification completed in Chromium

`python scripts/responsive_check.py` checks these CSS viewport sizes:

| Group | Width × height |
| --- | --- |
| Phones | 320×568, 360×640, 375×667, 390×844, 414×896, 480×800 |
| Tablets and breakpoint boundaries | 600×960, 760×900, 761×900, 768×1024, 820×1180, 900×900, 1024×768, 1100×800 |
| Laptops and desktops | 1280×720, 1366×768, 1440×900, 1600×900, 1920×1080, 2560×1440 |
| Short landscape screens | 667×375, 844×390, 1024×600 |

Assertions cover horizontal overflow, copy/photo collisions and loaded images at
every size. Both hero images and the enquiry button are required to fit in the
first viewport on the listed phones and laptops/desktops. Landscape, enlarged
text and tablets may scroll vertically; content is never clipped to force a
first-screen fit.

Additional checks cover:

- CSS reflow at viewport sizes equivalent to 200% page zoom.
- 200% text enlargement at 390, 768 and 1440 pixels, with usable enquiry links and
  no horizontal overflow or copy/photo collisions.
- Device pixel ratios 2 and 3, including responsive image selection.
- AVIF hero sources and working WebP alternatives.
- All ten pages at 320, 390, 768 and 1440 pixels via `browser_check.py`.
- Keyboard menu operation, Escape/focus behaviour, no-JavaScript navigation,
  reduced motion, image loading, console/network errors and nested 404 assets.
- Internal links, anchors, image dimensions, JSON-LD and source-size budgets.

The expanded checks found and fixed a tablet photo/copy collision, long project
and journal labels at enlarged text sizes, and header wrapping at 200% text size.
Mobile menu setup now runs inline immediately after the header instead of waiting
for a downloaded deferred script, avoiding a first-paint menu collapse.

## Scope of the claim

These are automated Chromium checks on Linux, including viewport and text-size
emulation. They do not establish physical iPhone/Safari or Firefox compatibility.
Firefox could not start in this environment's process sandbox and WebKit lacks
required host libraries. Check those browsers on real devices before a production
release. No browser failure was treated as a responsive pass.

Loading results and the exact comparison method are in
[OPTION-A-PERFORMANCE.md](OPTION-A-PERFORMANCE.md). The asset sizes and no-third-party
loading rules remain enforced by `scripts/check.py`.
