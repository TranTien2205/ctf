# Per-route (deep) — each route shape and its exploit path

## The route shapes

A mined route is one of: a client route, a server endpoint, a param
route, a gated route, a lazy route, an API route. Each shape verifies
and routes differently.

## Client route (`/admin`)

A react-router/vue-router path — the SPA's own navigation. Verify: does
`/api/admin` or the route's own fetch endpoint exist? The client path
is SPA-only; the API path is the real surface. A `404` on both is a
client-only dead route.

## Server endpoint (`/api/x`)

An endpoint literal — `curl` it. `200`/`401`/`403`/`405` → real; `404`
→ dead; a `200` serving the index → a catch-all. A real endpoint routes
to the class its params/verbs imply.

## Param route (`/user/:id`, `/file/:name`)

A param-bearing route — `/:id`, `?id=`, `/{id}`. The param names a
server input. `:id` → `web-idor`; `:file`/`:name` →
`file-read-primitives`; `:slug` → a content-fetch; `?q=` → `web-sqli`.

## Gated route (`meta.requiresAuth`, `PrivateRoute`)

A client-side gate on a route whose code + endpoints are still shipped.
Probe the gated endpoint directly — a public response means the guard
was client-only; a `403` that stays `403` means the server enforces it.

## Lazy route (`import()`, `loadChildren`, manifest chunk)

A route whose code is a lazy chunk — the file is public, the load is
gated. Fetch the chunk; mine it for the endpoints the route hides.
Often the admin/feature module.

## API route (`/api/*`, `/v1/*`, `/internal/*`)

A direct server path — the highest-value route class. `/api/admin`,
`/api/internal`, `/api/v2/debug` — gated-looking API routes the client
calls. Each is a probe target.

## The route → class matrix

| Route shape | Verify | Route |
|---|---|---|
| client route `/x` | `/api/x` exists? | its class or dead |
| endpoint `/api/x/{id}` | `curl /api/x/1` | `web-idor` |
| `?q=`/`?search=` | `curl "$BASE/x?q=t"` | `web-sqli`/`web-nosqli` |
| `/file/:name`, `?file=` | `curl "$BASE/file/x"` | `file-read-primitives` |
| `?url=`/`?target=`/`/proxy` | `curl "$BASE/proxy?url=x"` | `web-ssrf` |
| `/render`, `?template=` | `curl "$BASE/x?template=t"` | `web-ssti` |
| `/graphql`, `/gql` | `curl -XPOST` | `web-graphql` |
| `/admin`, `/internal` | `curl` gated? | `web-logic-flaw`/`web-idor` |
| gated `requiresAuth` | endpoint public? | client-gate find |
| `/upload` | a file-upload probe | `web-file-upload` |

## The route-table completeness

The route set is complete only when every chunk's routes are extracted
— `main`'s table + each lazy chunk's `forChild`/`Route` defs + the
manifest's lazy routes. A partial table misses the hidden chunk.
