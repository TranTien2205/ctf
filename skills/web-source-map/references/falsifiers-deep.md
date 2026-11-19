# Falsifiers (deep) — the five-depth kill map

## Depth 0: is there a bundle?

Falsifier: the entry page loads no application `.js` — only CDN libs, or
a fully server-rendered page. If there is no shipped client logic, the
route does not apply. Kill condition: zero application bundles in the
script inventory.

## Depth 1: is there a map?

Falsifier: every `.map` probe 404s or returns `text/html` (catch-all).
No `sourceMappingURL`, no inline map, no `SourceMap` header. Kill: the
map route is dead → string mining only; the *route* is not dead, the
*map* is.

## Depth 2: does the map carry source?

Falsifier: the map exists but `sourcesContent` is null/absent — you get
`sources` (file names) + `names`, not the text. Kill: reconstruction
yields structure, not source — downgrade the claim from "recovered the
source" to "recovered the file layout".

## Depth 3: does the mining yield leads?

Falsifier: after `bundle_miner` + targeted greps, the output is empty —
no endpoint strings, no params, no flags, no secrets, no flag shape. Kill:
the bundle is opaque (all literals stripped/hidden, or it is a thin
loader). The route produces no leads.

## Depth 4: do the leads verify?

Falsifier — the deepest: leads exist but every one fails the live check:
- every endpoint 404s (dead client routes)
- every secret candidate fails auth (dead/publishable keys)
- every flag is server-side enforced
- every route is client-only

Kill: the map produced leads, none actionable — the recon is done, no
bug fed. Record the clean negative.

## The per-lead falsifier (repeated from per-falsifier.md)

| Claim | Falsifier |
|---|---|
| endpoint real | 404 live |
| secret leaks | fails auth/decode |
| flag is a gate | server enforces it |
| route is server-side | 404 — client path |
| map is trustworthy | a `sources` traversal rejected |

## The honesty at each depth

- depth 0-1 dead → move to a different recon layer (`.git`, `.env`,
  `web-triage`)
- depth 2 dead → string mine; still useful
- depth 3 dead → the bundle is genuinely opaque; record and move
- depth 4 dead → the map gave leads, none actionable; record per-lead
  negatives and move to the next surface

A dead end at every depth is a *recorded measurement*, not a failure to
retry.
