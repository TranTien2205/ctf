# Endpoint inventory (deep) — the complete route-table build

## The inventory goal

Build the app's complete route table — every client route AND every
server endpoint — from the client's own code, not a brute-forced
wordlist. The result is the real attack surface.

## The extraction layers (complete)

```bash
# 1. call-site endpoints — fetch/axios/XHR/HttpClient
grep -oE '(fetch|axios\.[a-z]+|\.ajax|\.get|\.post|\.put|\.delete|\.patch|http)\s*\(\s*["'"'"'`][^"'"'"'`]+' b.js | sort -u
# 2. quoted absolute paths — the non-call-site literals
grep -oE '"/[A-Za-z0-9_./?=&{}:%@!$~+-]+"' b.js | tr -d '"' | sort -u
# 3. template-literal paths
grep -oE '`/[A-Za-z0-9_./?=&{}:$-]+`' b.js | tr -d '`' | sort -u
# 4. the api/version prefixes
grep -oE '"/(api|v[0-9]+|internal|admin|graphql|auth|user|file|upload|export|debug)[^"]*"' b.js | sort -u
# 5. full URLs — external + internal hosts
grep -oE 'https?://[A-Za-z0-9._/?=&:%-]+' b.js | sort -u
# 6. route definitions — the client route table
grep -oE 'path\s*:\s*["'"'"'`][^"'"'"'`]+' b.js | sort -u
# 7. the manifest route list
curl -s "$BASE/_next/static/$BUILD/_buildManifest.js" | grep -oE '"/[^"]*"'
```

## The grouping

Group by base path: `/api/`, `/v1/`, `/internal/`, `/admin/`, `/auth/`,
`/file/`. Each group is a service surface. Within a group, the
param-bearing endpoints (`/:id`, `?file=`, `{id}`) are the high-value
leads.

## The verify pass

```bash
while read ep; do
  out=$(curl -s -o "$tmp" -w '%{http_code}' "$BASE$ep")
  idx=$(grep -c '<div id="root"' "$tmp" 2>/dev/null)   # the SPA index marker
  echo "$out $ep $([ "$idx" -gt 0 ] && echo CATCHALL)"
done < endpoints.txt
```

- `200`/`401`/`403`/`405` non-index → real
- `404` → dead client route
- `200` serving the index → a catch-all

## The param-endpoint priority

| Shape | Priority | Route |
|---|---|---|
| `{id}`/`?id=`/`/:id` | high | `web-idor` |
| `?q=`/`?search=`/`?filter=` | high | `web-sqli`/`web-nosqli` |
| `?url=`/`?target=`/`/proxy` | high | `web-ssrf` |
| `/file/`/`?file=`/`?path=` | high | `file-read-primitives` |
| `?template=`/`?render=` | high | `web-ssti` |
| `/admin`/`/internal`/`/debug` | high | `web-logic-flaw`/`web-idor` |
| `/graphql` | high | `web-graphql` |
| `/export`/`/dump`/`/backup` | high | `web-logic-flaw`/`file-read` |
| `/upload` | medium | `web-file-upload` |
| `/login`/`/public`/`/index` | low | public by design |

## The dedup rule

The same endpoint across chunks is one lead — dedupe on the endpoint
string, keep the first source file. A param template and its instances
dedupe to the template.

## The output

A deduped, live-verified route table — `endpoint, source_file,
verify_result, class_route` — the real surface the challenge exposes,
built from the client's own code.
