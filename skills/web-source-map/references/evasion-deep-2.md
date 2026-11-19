# Evasion (deep-2) — advanced resistance and the deeper workarounds

## Note

This file extends `evasion-deep.md` — the deeper workarounds for a
bundle that resists mining and a deployment that hides the artifact.

## The JS-rendered bundle — when curl sees nothing

A SPA that renders its `<script>` tags client-side serves an entry page
with no scripts for `curl` to find — the bundle list is behind JS.

```bash
# drive a headless browser to capture the real bundle set — web-chromedriver
# the network log names every script the page loads
```

Use `../web-chromedriver/` to render the page and capture the network
log — the bundle set is every `.js` the browser fetched.

## The chunked/obfuscated endpoint indirection

The endpoint is built at runtime — `base + '/api/' + name`, a template
literal `apiUrl + '/users'` — the literal path never appears whole.

```bash
# find the base + the suffix separately
grep -oE '(api|base|BASE)(Url|URL|url)?\s*[:=]\s*["'"'"'`][^"'"'"'`]+' b.js
grep -oE '\+\s*["'"'"'`]/[a-z0-9_./{}$-]+' b.js | sort -u
grep -oE '`[^`]*\$\{[^}]+\}[^`]*`' b.js | sort -u     # template-literal endpoints
```

The concatenation parts are still literals — grep the base and the
suffix separately, then reassemble.

## The remote/dynamic route table

The routes come from a fetched config — `fetch('/api/routes')` or a
remote `featureService` — the bundle only holds the fetch, not the
table. The route table is server-side; the map only shows the client's
fetch of it. Probe the route-config endpoint directly.

## The signed/integrity-gated bundle

`integrity="sha384-..."` / a Subresource Integrity attribute — the
bundle is hash-locked. For mining (not executing), irrelevant — grep
the strings anyway; SRI is a load-time check, not a read gate.

## The chunked-source map

A `.map` may itself be code-split — a per-chunk map per chunk
(`main.js.map`, `2.chunk.js.map`, `pages/admin-*.js.map`). Probe each
chunk's map, not just `main`'s — the admin map is the gold.

## The no-scripts-CDN case

The app loads its bundle from a CDN (`cdn.x.com`, `unpkg`, `jsdelivr`)
— the script src is off-host. Fetch the CDN URL directly; the map and
the bundle are on the CDN host, not the app host.

## The integrity/protected `.map`

A `.map` that 401/403s — auth-gated source. Probe with the session
(`-H "Cookie: $C"`) — a session-gated map is still readable.

## The deeper fallback

When every workaround fails — the strings are opaque, the map is absent,
the bundle is a thin loader — the surface is server-side, not this
route. Record the dead end and move to `.git`/`.env`/`web-triage`, not
a repeat of the same mine.
