# Per-falsifier (deep) — the kill conditions per lead type

## The endpoint-lead falsifiers

| Lead | The kill | What it means |
|---|---|---|
| `/api/x` exists | 404 on the live probe | dead client route |
| `/api/x` exists | a 200 serving the SPA index | a catch-all, not an endpoint |
| `/api/x` exists | 401/403 without auth | real but gated — a target still |
| `/api/x` is a route | `/api/x` 404s but `/x` renders | a client route, not a server endpoint |

## The secret-lead falsifiers

| Lead | The kill | What it means |
|---|---|---|
| a JWT is a session | decodes to nothing / expired | dead token |
| a key authenticates | 401 on `Authorization` probe | dead/wrong key |
| a key is a secret | `pk_live_`/`NEXT_PUBLIC_` shape | publishable, not a leak |
| `apiKey` is real | context shows a comment/var | a minified id, not a secret |

## The flag-lead falsifiers

| Lead | The kill | What it means |
|---|---|---|
| `feature.X` gates a gate | server returns 403 regardless | server-enforced — not a bypass |
| `feature.X` gates an endpoint | endpoint public without the flag | client gate — a find |
| a debug flag opens debug | `?debug=1` returns nothing new | the flag is UI-only |

## The route-lead falsifiers

| Lead | The kill | What it means |
|---|---|---|
| `/admin` is a server route | 404 | a client-only path |
| `meta.requiresAuth` gates | endpoint public anyway | client guard — a find |
| a lazy chunk exists | the chunk 404s | a dead lazy route |

## The map/source falsifiers

| Lead | The kill | What it means |
|---|---|---|
| `.map` is a map | `200 text/html` catch-all | not a map |
| the map has source | `sourcesContent` null | file names only |
| a `sources` path is a file | it escapes `--out` | a traversal — rejected |
| recovered source is true | it is planted/dev-only | attacker-controlled data |

## The route-dead falsifier

| The claim | The kill |
|---|---|
| the bundle holds leads | every lead's falsifier fires — all dead |
| re-mining helps | a dead bundle's strings are fixed |

## The honesty rule per falsifier

Every lead carries its falsifier; the lead is real only while the
falsifier has not fired. A fired falsifier is a *recorded negative*,
not a retry.
