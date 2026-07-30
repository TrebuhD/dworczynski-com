# dworczynski.com

Single static page. No build step, no dependencies - `index.html` is the whole site.

| File | Purpose |
| --- | --- |
| `index.html` | The page. Inline CSS/JS, inline SVG favicon. |
| `og.png` | 1200x630 link preview. Only fetched by crawlers. |
| `apple-touch-icon.png` | 180x180, full-bleed - iOS applies its own corner mask. |
| `robots.txt` | Allows all, points at the sitemap. |
| `sitemap.xml` | One URL. Bump `lastmod` when the copy changes. |
| `llms.txt` | Plain-text facts for LLM crawlers. Mirror any bio edit here. |

## Preview

```
open index.html
```

## Deploy (Cloudflare Pages)

1. Push this directory to a GitHub repo.
2. Cloudflare dashboard - Workers & Pages - Create - Pages - connect the repo.
3. Build command: none. Output directory: `/`.
4. Custom domains - add `dworczynski.com` and `www.dworczynski.com`.

Cloudflare handles TLS. Subsequent deploys are a `git push`.

## Email

`hubert@dworczynski.com` forwards to Gmail via Cloudflare Email Routing. Set up 2026-07-30.

Records in the zone:

```
MX   84  route1.mx.cloudflare.net.
MX   56  route2.mx.cloudflare.net.
MX   66  route3.mx.cloudflare.net.
TXT      v=spf1 include:_spf.mx.cloudflare.net ~all
TXT      cf2024-1._domainkey   (DKIM)
```

Verify with `dig +short MX dworczynski.com`.

Adding another mail sender later (a newsletter service, a transactional provider) means merging
its `include:` into the existing SPF record rather than adding a second TXT - a domain with two
SPF records fails SPF entirely.

## Notes

- Email is assembled in JS at runtime so the address isn't plain text in the source. For the same
  reason it is deliberately absent from the JSON-LD and from `llms.txt` - putting it in either would
  hand it straight back to scrapers.
- Dark mode follows `prefers-color-scheme`; both palettes are in the `:root` block.
- Favicon is an inline SVG data URI. Nothing on the page triggers an external request; `og.png` and
  `apple-touch-icon.png` are same-origin and are not fetched during a normal page load.
- Fonts are the system mono stack. No webfonts, so no FOUT and no network dependency.
- **`#plate` needs an explicit `width`/`height`; `inset: 0` alone will not do it.** A
  `canvas` is a replaced element, so with `width: auto` the box takes its *intrinsic* size
  - the backing-store `width` attribute - and the `right` offset is ignored. Left as
  `left/right: 0` it stretched to the backing width and overflowed the page sideways, which
  then fed back into the JS resize loop. Verified in Chromium at a 390px viewport.
- `body` carries `min-height: 100lvh` to match the plate. The plate is absolutely
  positioned and so still contributes scrollable overflow; without the matching
  `min-height` the document is content-height and the plate adds a toolbar-height of empty
  scroll to the bottom of a short page. Verified: vertical overflow is 0 either way now.
- `overscroll-behavior-y: contain` kills pull-to-refresh but leaves the iOS rubber band
  alone. `none` killed the bounce too and made scrolling feel dead.

### Unresolved: the iOS status bar and toolbar

Solid bars still appear above and below the plate on iOS Safari, where other sites show
page content. **The cause is not established** - the notes previously here asserted a
mechanism (`position: fixed` near a viewport edge makes Safari abandon compositing and
paint a flat tint) that was never confirmed, and flip-flopping the plate between `fixed`
and `absolute` did not fix it either way. Treat that claim as unverified.

What is known:

- `theme-color` is gone. It definitely does hardcode the bar tint on iOS, so it had to go
  before anything else could be tested, but removing it alone did not fix the bars.
- `viewport-fit=cover` is set, so the layout viewport does span the safe areas.
- None of this reproduces in Chromium, which is the only engine testable here. It needs a
  real device, and ideally a screenshot plus the iOS version to tell a chrome tint apart
  from a safe-area gap.

## Background

Chladni figures - the nodal pattern sand forms on a vibrating plate. A fullscreen WebGPU fragment
shader evaluates

```
cos(nπx)cos(mπy) − λ·cos(mπx)cos(nπy)
```

Two such terms are superposed and cross-faded by a rotating mix angle: at the poles one term owns
the plate, between them the field is a hybrid. That rotation is what turns drift into a change of
shape. All four mode numbers wander on pairs of incommensurate sinusoids, so nothing repeats and
nothing snaps - no dwells, no discrete mode list. Everything is driven off `SPEED`; at 0.055 a mode
number moves at most ~0.08/s, slow enough to read as movement rather than animation.

`λ` drifts around 1 rather than sitting on it. At exactly 1 each term is antisymmetric and vanishes
on `x == y` for every mode, which nails a static diagonal across the page. A two-octave sinusoidal
warp on the sample point keeps the result from reading as a clean analytic lattice.

Mode numbers stay in roughly 1.5-7. Higher and the field gets busy enough to fight the text; lower
and the screen empties out.

### Rendering the field as tone

The nodal set is never drawn. Drawing it gives you lines, and stippling a line only ever decorates
it - the falloff band is a few pixels wide, so grains cluster into a stroke with strays around it.
Instead the field maps to a 2-level dithered screen, which reads as broad soft regions with print
grain. Interleaved gradient noise supplies the dither, pinned to the pixel grid so the texture holds
still while the field moves underneath it.

Two things this depends on:

- **`thr` keeps ink off the mid-tones.** Mapping tone straight to alpha inks the entire viewport at
  half strength, which lifts the background and eats text contrast. Only the highlights take ink, so
  the true background shows through. `thr` is the real coverage control - raise it to quiet a style.
- **2 levels, not 1.** At these opacities a smooth gradient has no visible texture, so the grain has
  to come from quantization. 1 level is a hard screen and too coarse; 2 keeps it visible but soft.

One of four tone mappings is picked per page load. `?plate=wash|glow|lit|poster` pins one:

| | |
|---|---|
| `wash` | the signed field straight to tone - broad pools sliding over each other |
| `glow` | field energy, brightest where the plate swings hardest |
| `lit` | field as a height map with light raking across it |
| `poster` | wash with the ramp pushed toward separations |

`lit` uses a facing-and-steepness term rather than lambert shading, because lambert gives every flat
region a mid-tone - the same veil `thr` exists to prevent.

No pointer input, so it behaves identically on mobile and desktop.

**WebGPU only, no WebGL fallback.** `if (!navigator.gpu) throw 0` leaves the plain page plus grain,
which is the whole experience on iOS before Safari 26 and Firefox outside Windows. Deliberate
choice, not an oversight. WebGPU buys nothing over WebGL for a shader this simple - it was picked
for the modern API, not for speed.

Tunables: `SPEED`, `CENTER`, the per-style `OPACITY`/`OPACITY_L`/`THR`/`NZ` tables, `LEVELS` in the
shader, and `MIN_DT`. Rendering is capped at 40fps because the motion is slow enough that 120 looks identical
and costs three times the GPU work. Pauses on `visibilitychange`; `prefers-reduced-motion` pins
time to a constant so it renders one static frame.

## Regenerating the PNGs

Both are screenshots of throwaway HTML rendered headless (the mark is a path, not text, so it does
not depend on a font being installed). Source for the `D` glyph lives in the favicon data URI in
`index.html` - keep the three copies in sync if the mark changes.

## SEO

Structured data is a `schema.org/Person` JSON-LD block: name, job title, locality, and `sameAs`
links to GitHub and LinkedIn. Those `sameAs` entries are what let search and answer engines connect
this page to the profiles as one entity - keep them in step with the visible link list.

After deploying, submit the sitemap in Google Search Console and Bing Webmaster Tools. Nothing links
here yet, so discovery is otherwise slow.
