# Endpoint playbook — the mined-endpoint runbook

## Step 1: build the inventory

```bash
# every endpoint-shaped literal
grep -oE '"/(api|v[0-9]+|internal|admin|graphql|auth|user|file|upload|export|debug)[^"]*"' *.js | tr -d '"' | sort -u > eps.txt
grep -oE '(fetch|axios\.[a-z]+)\s*\(["'"'"'`][^"'"'"'`]+' *.js | grep -oE '["'"'"'`][^"'"'"'`]+' | tr -d '"'"'"'`' | sort -u >> eps.txt
sort -u eps.txt -o eps.txt
```

## Step 2: classify each

| Shape | Class |
|---|---|
| `{id}`/`?id=`/`/:id` | `web-idor` |
| `?q=`/`?search=`/`?filter=`/`?sort=` | `web-sqli`/`web-nosqli` |
| `?url=`/`?target=`/`?callback=`/`/proxy` | `web-ssrf` |
| `/file/`/`?file=`/`?path=`/`?name=` | `file-read-primitives` |
| `?template=`/`?render=`/`?message=` | `web-ssti`/`web-xss` |
| `/admin`/`/internal`/`/debug`/`/actuator` | `web-logic-flaw`/`web-info-disclosure` |
| `/login`/`/auth`/`/token`/`/reset`/`/oauth` | `web-auth-session`/`web-oauth-sso` |
| `/graphql` | `web-graphql` |
| `/upload`/`/import` | `web-file-upload` |
| `?redirect=`/`?next=`/`?return=` | `web-open-redirect` |
| `/export`/`/dump`/`/backup` | `web-logic-flaw`/`file-read` |
| `/transfer`/`/pay`/`/redeem`/`/bet` | `web-logic-flaw`/`web-race-condition` |
| `ws://`/`wss://`/`/socket.io` | `web-websocket` |

## Step 3: verify each

```bash
while read ep; do
  code=$(curl -s -o "$tmp" -w '%{http_code}' "$BASE$ep")
  idx=$(grep -c '<div id="root"\|<div id="app"' "$tmp" 2>/dev/null)
  printf '%-40s %s %s\n' "$ep" "$code" "$([ "$idx" -gt 0 ] && echo CATCHALL)"
done < eps.txt
```

- `200`/`401`/`403`/`405` non-index → real → route
- `404` → dead client route → record
- `200` serving the index → catch-all → record

## Step 4: probe the live ones

Each live endpoint gets its class's first probe — an `?id=` gets
`web-idor`'s existence oracle, a `?q=` gets `web-sqli`'s injection
oracle, a `?url=` gets `web-ssrf`'s reach probe.

## Step 5: record

Each endpoint: `string, source_file, verify_result, class_route`. The
live-verified route table is the deliverable — the real surface the
client's own code named.
