# BIM Farers — design review, 6 November 2026

Baseline: `mentorfloat/BIMFarers-landing-page`, `main`, commit
`7cf7a55dacc0eb5e379b5edb786f3596a1ee9d03`.
Working branch: `design/modern-minimal-refresh`. This is a reviewable first
redesign, with no production deployment or merge.

## What the existing site gets right

The strongest material is already here: a real Revit model, six recognisable
Melbourne developments, team photography, a clear contractor audience, and a
Melbourne/Malaysia delivery model. Its combination of engineering, modelling and
software development is a more useful distinction than generic agency language.

The homepage is not fundamentally out of date in purpose. The visual treatment
is: floating text over a masked image, oversized rounded buttons and shadows,
alternating feature blocks, a desktop hover gallery with a separate mobile
carousel, animated counters and long staggered reveals. The loading screen also
makes a static website feel like an application that needs to boot up.

## Inventory and findings

| Surface | Existing behaviour | First iteration |
| --- | --- | --- |
| Home | Hero, six projects, team, three engagement tiers, software/registration claims, counters, careers, contact and logos | One responsive project grid; clearer service and engagement sections; team, journal and direct enquiry links |
| About | Full-height background photo, credential logos, six people, immediate Google Maps iframe | Consistent Practice page, smaller responsive photo, all six people and credentials, static location images and explicit contact/map links |
| Plugins / automation | A holding page saying the website is being updated | Useful Revit tools page, existing Autodesk publisher destination, custom development enquiry and privacy link |
| Blog | Three long post previews, all dated 2023 | Compact journal, actual dates and an explicit archive label |
| Three articles | Bootstrap layouts, duplicated headers, AOS, jQuery, inline fonts, original references and BlogPosting data | Readable shared article layout; original copy, dates, references and schema preserved; fixed duplicate/missing anchor targets |
| Plugin privacy | Policy effective 11 February 2024 | Original policy wording and date, new shared shell and heading hierarchy |
| Payment return | Static page asserts payment success without verifying a transaction | Directs visitors to PayPal/email for actual transaction status and to the Autodesk store |
| 404 | Separate legacy styling | Shared shell, root-relative assets that work on missing nested paths, working homepage link |
| map.html | Google Maps locator with two office addresses and Handlebars | Retained as an unlinked legacy page; no longer part of any redesigned page's load path |
| Hosting | Static GitHub Pages, custom `www.bimfarers.com.au` domain, production branch `main` | Same hosting; added branch-safe deployment guard and static validation workflow |

The last code changes were maintenance (fonts and removal of polyfill.io), while
editorial content remains older. A visual refresh alone will not make the journal
or project information current.

## Contemporary reference points

Reviewed the current public homepages on 6 November 2026:

- [Snøhetta](https://www.snohetta.com/): prominent projects, a short practice
  statement, disciplines, people/process, and clear project navigation.
- [SOM](https://www.som.com/): projects alongside research, stories and the people
  behind the work; engineering is visible within the practice's expertise.
- [Arup](https://www.arup.com/): clear routes through services, projects and
  insights, with work described in terms of practical outcomes.

These are references for information hierarchy, not templates to copy or claims
that every visual effect they use is appropriate here. My recommendation for
BIM Farers is an editorial, project-led presentation at a much smaller technical
weight. Native HTML and restrained CSS can provide that character.

## Design decisions implemented

1. **Give the model room.** A large, immediately visible headline and uncropped
   model replace the text/image mask. The caption names the development. A small
   overview makes the service understandable before the visitor scrolls.
2. **Use an architectural grid.** Warm off-white, charcoal, thin rules, consistent
   gutters, square image frames and restrained sage accents. Preserve the real
   brand mark and owned photography. One local type weight keeps font transfer
   and typography consistent.
3. **Make the work legible.** All six developments appear in one grid on desktop
   and mobile. Captions are always visible. They are figures, not dead links
   pretending to be case studies. The note distinguishes building-services
   involvement from authorship of the whole building.
4. **Shorten the route to an enquiry.** Clear services, three engagement models,
   a visible email address, retained phone number and a direct mail link. No
   unconnected form or claim that a message has been sent.
5. **Treat animation as feedback.** 180 ms link/button and menu feedback; 280 ms
   image hover; optional 320 ms, 12 px section movement. Content is always
   visible. The hero never animates in, and no loader, scroll hijacking, parallax,
   autoplay video, custom cursor or animation dependency is introduced.
6. **Use one site language.** Practice, tools, journal, articles and utility pages
   share the same header, footer, typography and navigation. Reduced motion and
   no-JavaScript use are first-class behaviours.

## Recommended next content updates, in order

1. **Publish two or three proper case studies.** Confirm permission for images and
   name the actual scope, trades served, deliverables, project stage, tools and
   an evidenced outcome. Use drawings/model details alongside the architectural
   rendering. A visitor should learn what BIM Farers contributed, not just which
   development it worked on. Do not invent performance percentages or imply
   building design authorship.
2. **Refresh professional proof.** Confirm the people, roles, office addresses,
   phone, credential badges, current registrations and the precise engineering
   certification scope. The previous Regulation 126/Performance Solutions
   wording needs a qualified business review before being republished. Old
   17.2k Revit-hour and $1.89b aggregate-project-value counters are omitted from
   the first redesign until their dates and basis are confirmed. Partner logos
   can return as a compact, approved strip after relationship/permission review.
3. **Replace the plugin holding page with maintained product information.** The
   first iteration supplies a useful route to the existing Autodesk listing.
   Add specific tool names, supported Revit releases, screenshots and support
   instructions only after checking the live product details.
4. **Restart the journal with useful recent practice.** Suggested subjects:
   coordinating MEP handovers, reducing repetitive Revit work, and practical BIM
   model checking. Keep the 2023 posts as dated archives. Any current regulatory
   or software guidance should be checked by its author, not silently redated.
5. **Make maintenance predictable.** Quarterly content review, a small image
   budget, and browser/performance checks on this branch before release. Keep
   production HTML static. The small Python shell renderer avoids header/footer
   drift without adding runtime software.

## Performance is part of the design

The first screen has one stylesheet, one deferred script, one self-hosted font,
one brand SVG and one responsive model image. Remaining images use native lazy
loading and explicit dimensions. No third party is contacted until the visitor
chooses an external link. No video is loaded.

Source-file budgets are enforced in `scripts/check.py`: CSS ≤20 KB, JS ≤3 KB,
homepage HTML ≤30 KB, mobile model ≤30 KB and desktop model ≤60 KB. Timing results,
limitations and reproduction commands are in [PERFORMANCE.md](PERFORMANCE.md).

## Still required before production

Owner review of the design, rewritten marketing copy and the business facts
above; Claude/independent code QA; real Safari/iOS and Firefox checks; final
production-like performance validation. The branch has not been deployed. The
legacy map and unused Bootstrap/AOS assets can be removed in a separate cleanup
once the new direction is accepted.
