# dworczynski.com

Single static page. No build step, no dependencies - `index.html` is the whole site.

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

- Email is assembled in JS at runtime so the address isn't plain text in the source.
- Dark mode follows `prefers-color-scheme`; both palettes are in the `:root` block.
- Favicon is an inline SVG data URI. No external requests anywhere on the page.
