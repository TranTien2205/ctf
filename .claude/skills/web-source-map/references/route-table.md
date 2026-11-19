# Route table — building the complete route map

## The goal

The bundle's route definitions + endpoint strings = the app's complete
route table — every client route AND every server endpoint the client
calls. It is the real surface, replacing brute-force enumeration.

## The route sources

| Source | Yields |
|---|---|
| `path:`/`component:`/`Route` defs | client routes (SPA pages) |
| `_buildManifest.js` keys | Next.js page routes |
| `loadChildren`/lazy `import()` | lazy route modules |
| `meta: {requiresAuth/role}` | gated routes |
| fetch/axios call sites | server endpoints |
| `"/api/..."` literals | server endpoints |
| `sw.js`/precache manifest | the asset/route inventory |

## The route-table build

```bash
{
  echo "== client routes =="
  grep -oE 'path\s*:\s*["'"'"'`][^"'"'"'`]+' bundle.js | sort -u
  echo "== next manifest routes =="
  curl -s "$BASE/_next/static/$BUILD/_buildManifest.js" | grep -oE '"/[^"]*"' | sort -u
  echo "== server endpoints =="
  grep -oE '"/(api|v[0-9]+|internal|admin|graphql|auth|file|upload)[^"]*"' bundle.js | sort -u
  echo "== lazy chunks =="
  grep -oE 'import\(\s*["'"'"'`][^"'"'"'`]+' bundle.js | sort -u
}
```

## The route classification

| Route type | Verify |
|---|---|
| client route (`/admin`) | does `/api/admin` or the route's own endpoint exist |
| server endpoint (`/api/x`) | `curl` it — real response? |
| param route (`/user/:id`) | `curl /api/user/1` — an IDOR probe |
| gated route (`meta.requiresAuth`) | the gate is client-side — probe the endpoint directly |
| lazy route | fetch its chunk → its endpoints |

## The gated-route priority

A route with `meta: {requiresAuth: true}` or `role: 'admin'` names a
gate the *client* checks — the gated code and its endpoints are shipped
regardless. The `meta` field is a map of which routes the app thinks
are protected — and the server often does not enforce it.

## The param-route lead

`/:id`, `/:slug`, `/:name`, `/:file` — a param-bearing route names a
server param. `/user/:id` → `web-idor`, `/file/:name` →
`file-read-primitives`, `/post/:slug` → a content-fetch. Each param
route is an injection/IDOR-shaped lead.

## The completeness check

The route table is complete only when every chunk's routes are
extracted — `main`'s table + each lazy chunk's `forChild`/`Route` defs +
the manifest's lazy routes. A partial table misses the hidden admin
chunk.
