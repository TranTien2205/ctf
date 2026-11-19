# Endpoint inventory — turning bundle strings into a route table

## The inventory goal

The bundle's endpoint strings are the client's own route table — the
real list of server paths, not a brute-forced guess. Building the
inventory means extracting every endpoint-shaped literal and grouping
it by base.

## The extraction layers

```bash
# 1. quoted absolute paths
grep -oE '"/[A-Za-z0-9_./?=&{}:%@!$~+-]+"' b.js | tr -d '"' | sort -u
# 2. template-literal paths
grep -oE '`/[A-Za-z0-9_./?=&{}:$-]+`' b.js | tr -d '`' | sort -u
# 3. the api/version prefixes
grep -oE '(api|v[0-9]+|internal|admin|graphql|auth|user|file|upload)[A-Za-z0-9_./-]*' b.js | sort -u
# 4. call-site arguments
grep -oE '(fetch|axios\.[a-z]+|\.get|\.post|\.put|\.delete|\.patch)\s*\(\s*["'"'"'`][^"'"'"'`]+' b.js | sort -u
# 5. full URLs (external + internal hosts)
grep -oE 'https?://[A-Za-z0-9._/?=&:-]+' b.js | sort -u
```

## The grouping

Group the extracted strings by base path — `/api/`, `/v1/`, `/internal/`,
`/admin/`, `/auth/` — each group is a service surface. Within a group,
the param-bearing endpoints (`/:id`, `/{id}`, `?file=`) are the high-
value leads.

## The verify pass

Each inventory entry is a claim — `curl` it:

```bash
while read ep; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE$ep")
  echo "$code $ep"
done < endpoints.txt | sort -n
```

- `200`/`401`/`403` → a real endpoint (401/403 = exists but gated)
- `404` → a dead client route — record as negative
- a `200` that is the SPA index → a catch-all, not an endpoint

## The param-endpoint priority

| Endpoint shape | Priority | Route |
|---|---|---|
| `/api/x/{id}`, `?id=` | high — an IDOR probe | `web-idor` |
| `/search?q=`, `/filter?` | high — injection probe | `web-sqli`/`web-nosqli` |
| `/file/`, `/download`, `/read` | high — file read | `file-read-primitives` |
| `/proxy?url=`, `/fetch?` | high — SSRF | `web-ssrf` |
| `/admin`, `/internal`, `/debug` | high — gated surface | `web-logic-flaw`/`web-idor` |
| `/graphql` | high | `web-graphql` |
| `/upload` | medium | `web-file-upload` |
| `/login`, `/public` | low — public by design | recon only |

## The deduped route table

The final inventory is a deduped, live-verified route table — the real
surface the challenge exposes, built from the client's own code rather
than guessed.
