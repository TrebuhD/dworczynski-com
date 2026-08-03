# Implementation notes

Working knowledge that isn't obvious from the code. Trimmed to constraints that will bite again if forgotten.

## Deploy

Cloudflare Pages, connected to this repo. Build command: none, output directory: `/`. Custom domains `dworczynski.com` and `www.dworczynski.com`; Cloudflare handles TLS.

Everything in the repo deploys, including this file. `_redirects` shadows `docs/`, `tools/` and `README.md` (Pages evaluates redirects before static assets) - without it this file is public and leaks the email address verbatim, defeating the JS assembly on the page. Keep `_redirects` in step with any new non-site files.

## Email

`hubert@dworczynski.com` forwards to Gmail via Cloudflare Email Routing (set up 2026-07-30). Zone records: three `route*.mx.cloudflare.net` MX records, SPF TXT, DKIM TXT. Verify with `dig +short MX dworczynski.com`.

Adding another mail sender later means merging its `include:` into the existing SPF record, not adding a second TXT - two SPF records fail SPF entirely.

## Page

- Email address is assembled in JS at runtime and deliberately absent from JSON-LD and `llms.txt` - putting it there hands it to scrapers. Ships as a `span`, promoted to an anchor by script; with JS off it degrades to readable text.
- `--rule` and `--link-line` are separate tokens on purpose. The link colour is the text colour, so the underline is the only link marker and must clear 3:1 (WCAG 1.4.11); the `hr` stays faint. `--dim` sits at 4.8:1 in both schemes.
- No external requests during a normal page load: inline SVG favicon, system mono stack, `og.png`/`apple-touch-icon.png` only fetched by crawlers and iOS.
- **`#plate` needs explicit `width`/`height`; `inset: 0` alone will not do it.** A canvas is a replaced element - with `width: auto` it takes its backing-store size, overflows sideways, and feeds back into the JS resize loop.
- `body` uses `min-height: 100svh`, not `lvh` - `lvh` forces a toolbar-height of empty scroll on iOS, so the toolbars never retract.
- The plate and grain size to `body` (`position: relative` exists for this), not the viewport - otherwise the texture ends mid-page when content overflows (large-text settings, text-only zoom, short landscape phones).
- `overscroll-behavior-y: contain` kills pull-to-refresh but keeps the iOS rubber band; `none` made scrolling feel dead.
- Text column is anchored at `14vh`, not centred - tried centring, reads worse.

## iOS bars

The status/tab bars show a flat colour, not the plate. Deliberate; bisected on a real iPhone (iOS 26.5.2). Two mechanisms:

1. **The layout viewport is inset unconditionally.** Safari 26 sets `obscuredContentInsets`; `viewport-fit=cover` governs display-cutout insetting, not browser-UI insetting. `env(safe-area-inset-top)` is 0 in portrait and that is correct. No page-level markup reaches those bands. ([Safari 26.0 release notes](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/))
2. **Bar tint is sampled from the page's `background-color`** near the viewport edges, falling back to `body`. `theme-color` is ignored entirely.

So `body` must be opaque and the plate must not use a negative `z-index`. The old stacking (plate at `-2`, transparent body) gave Safari nothing to sample - that was the "solid bars" bug. Current stacking: plate `0`, grain `1`, `main` `2`, opaque body. The plate's mean tone is 2/255 from `var(--bg)`, so flat bars match anyway.

Rejected approaches for getting the sim behind the bars (all built and tested on-device): scroll runway, pinned layers via transform / `animation-timeline: scroll()` / `sticky` / body-as-scroller (all jitter - scroll runs on the compositor), mandatory scroll snap. All require the page to scroll. **Do not use `position: fixed` or `sticky` near a viewport edge** - iOS 26 clips it and the bars go opaque ([Stack Overflow](https://stackoverflow.com/questions/79753701/)). The only real solution is home-screen standalone mode, which changes nothing for a normal visitor.

## Shader

Chladni figures: the shader evaluates `cos(nπx)cos(mπy) − λ·cos(mπx)cos(nπy)`, two such terms cross-faded by a rotating mix angle. All four mode numbers wander on incommensurate sinusoids - nothing repeats, no discrete mode list. Driven off `SPEED` (0.055 keeps a mode number under ~0.08/s, movement rather than animation).

- `λ` drifts around 1 rather than sitting on it - at exactly 1 every mode vanishes on `x == y`, nailing a static diagonal. A two-octave warp keeps the field from reading as an analytic lattice.
- Mode numbers stay in ~1.5-7: higher fights the text, lower empties the screen.
- The nodal set is never drawn - stippling a line just decorates it. The field maps to a 2-level dithered screen (interleaved gradient noise, pinned to the pixel grid).
- `thr` keeps ink off the mid-tones; mapping tone straight to alpha inks the whole viewport and eats text contrast. `thr` is the coverage control.
- 2 quantization levels, not 1 - at these opacities the grain has to come from quantization; 1 level is too coarse.
- `lit` uses a facing-and-steepness term, not lambert - lambert gives flat regions a mid-tone veil.
- **WebGPU only, no WebGL fallback, deliberately.** `if (!navigator.gpu) throw 0` leaves the plain page plus grain.
- Capped at 40fps (120 looks identical, costs 3x). Pauses on `visibilitychange`; `prefers-reduced-motion` renders one static frame.
- Tunables: `SPEED`, `CENTER`, per-style `OPACITY`/`OPACITY_L`/`THR`/`NZ` tables, `LEVELS`, `MIN_DT`.

## tools/

Nothing runs at build time; all for regenerating artwork by hand. macOS only.

- `build-og.sh [wash|glow|lit|poster] [dark|light]` - renders `og.png` with the real shader extracted from `index.html`, so the card can't drift from the page. Currently `lit / dark`, ink boosted 2.6x. Runs `pngquant` if on PATH (4-bit palette is lossless here, ~230K to ~55K).
- `make-mark.py` - prints the favicon data URI; `--touch`, `--card`, `--solid` variants. The mark is a path (no font dependency), grid 32 so every coordinate is an integer - at 16 the dither eats the silhouette. Check any accent replacement against **both** light (3.9:1) and dark (4.5:1) backgrounds.
- `og-gen.html` - the card layout `build-og.sh` screenshots.
- `marks-preview.html` - 30 typefaces as a `D`; kept from when the mark was a letter. Check any face at 16px - Didone hairlines die at icon sizes.

The `D` glyph source lives in the favicon data URI in `index.html` - keep the three copies in sync if the mark changes.

## SEO

JSON-LD `schema.org/Person` block with `sameAs` links to GitHub and LinkedIn - keep them in step with the visible link list. Sitemap: bump `lastmod` in `sitemap.xml` when copy changes; mirror bio edits in `llms.txt`. Sitemap submitted to Google Search Console and Bing Webmaster Tools.
