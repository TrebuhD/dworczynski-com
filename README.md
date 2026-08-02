# dworczynski.com

Personal site. Single static page - no build step, no dependencies, `index.html` is the whole site.

The background is a live [Chladni figure](https://en.wikipedia.org/wiki/Chladni_figure) rendered as a dithered screen in a WebGPU fragment shader. `?plate=wash|glow|lit|poster` pins one of the four tone mappings.

## Layout

- `index.html` - the page, inline CSS/JS
- `og.png`, `apple-touch-icon.png` - link preview and iOS icon
- `robots.txt`, `sitemap.xml`, `llms.txt` - crawler plumbing
- `tools/` - scripts for regenerating the artwork (macOS, not part of the site)

## Develop

```
open index.html
```

Deployed on Cloudflare Pages; every push to `main` deploys.

Implementation notes live in [docs/NOTES.md](docs/NOTES.md).
