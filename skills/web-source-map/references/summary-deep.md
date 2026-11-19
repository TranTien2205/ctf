# Summary (deep) — the complete picture

## What this layer is

`web-source-map` is **front-end bundle and source-map recon** — a
*recon layer*, not a bug class. A single-page app ships its whole
client logic to the browser; this layer reads it: the bundle's
endpoints, routes, params, flags, and secrets; and the `.map`'s
recovered original source.

## The core mechanism

- **the bundle** — minified client logic; strings survive: endpoints,
  routes, params, flags, secrets
- **the map** — `*.js.map`; `sourcesContent` recovers the original
  commented source
- **the manifests** — `_buildManifest`/`asset-manifest`/`sw.js` —
  the build's own asset+route inventory

## The pipeline

```
inventory -> map probe -> mine -> triage -> verify -> route -> record
   |           |           |        |         |         |        |
 scripts   .map probes  bundle_  rank    live    class   file+
 manifest  (4 routes)   miner/  leads   check   route   verbatim
                        grep
```

## The two mining paths

- **map present** (`sourcesContent`) → read the real commented source —
  sinks, keys, logic, the flag
- **map absent** → string-mine every bundle for literals — endpoints,
  params, secrets, flags

## The output → class map

| Lead | Route |
|---|---|
| endpoint + id | `web-idor` |
| query body | `web-sqli`/`web-nosqli` |
| template render | `web-ssti` |
| server fetch URL | `web-ssrf` |
| file path | `file-read-primitives` |
| verified key | `web-auth-session` |
| admin route/flag | `web-logic-flaw`/`web-mass-assignment` |
| internal host | `web-ssrf` |
| GraphQL | `web-graphql` |
| `__proto__`/merge | `web-prototype-pollution` |
| redirect param | `web-open-redirect` |
| flag shape | `pre-flag` |

## The five rules

1. **the map is recon, not the exploit** — it names targets; the routed
   class closes them
2. **verify every lead live** — a bundle string is a claim, not a fact
3. **a secret is a candidate** — it leaks only if it authenticates
4. **the source is attacker-controlled** — read, never execute; a
   `sources` traversal is rejected
5. **catalogue** — no local verified solve; standard published knowledge

## The one-lead economics

The whole pass is justified by ONE hidden endpoint or live key — the
map's job is to surface that one lead among the noise. Mine every
chunk; `main`-only mining is the common miss.

## The evidence level

Catalogue — no local verified solve. The corpus is standard published
knowledge until a real map-led solve lands in `../field-notes.md`.
