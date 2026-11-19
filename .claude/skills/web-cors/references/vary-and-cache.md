# Vary and cache — the caching surface around the CORS response

`Vary: Origin` decides whether a cached response is per-origin — and
the cache's own CORS handling is a separate misconfig layer.

---

## 1. `Vary: Origin` — the per-origin cache key

```text
a dynamic ACAO (reflected or computed) should carry `Vary: Origin` —
it tells caches the response differs by Origin. without it, a shared
cache may serve a response cached for a DIFFERENT origin — a cache
poisoning surface where a permissive ACAO for one origin serves
another.
```

## 2. The cache-poisoning interplay — a fixed-ACAO cache

```bash
# request with an attacker Origin — if the cache stores it and
# serves it to other origins, the permissive ACAO poisons the cache
curl -s -i "$BASE/api/x" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control|vary|cache|age|cf-|x-cache'
```

## 3. The Max-Age preflight cache — a stale permission

```text
a long Access-Control-Max-Age caches the preflight — a later
'tightened' CORS still uses the cached permissive answer. a real
browser test sees the stale cache — a fresh context/incognito is
the clean test.
```

## 4. The CDN/proxy CORS layer — the response that isn't the app's

```text
a CDN/reverse-proxy may inject or override the CORS headers — the
app's actual ACAO may differ from what you see. check the response
headers end-to-end — cf-*, x-cache, via — the CORS config may live
on the proxy, not the app.
```

```bash
curl -s -i "$BASE/api/x" -H 'Origin: https://evil.com' | \
  grep -iE 'cf-|x-cache|via|age|server|x-served|access-control'
```

## 5. The cache-bypass — a unique Origin per test

```bash
# a unique Origin per request — defeats a cached response
curl -s -i "$BASE/api/x" -H "Origin: https://evil-$RANDOM.com" | \
  grep -i 'access-control-allow-origin'
```

## 6. The Vary-analysis — does the cache key on Origin

```bash
curl -s -i "$BASE/api/x" -H 'Origin: https://a.com' | grep -i 'vary'
#   Vary: Origin → per-origin — clean test each time
#   no Vary → a shared cache may serve a cross-origin response
```

## 7. The reflected-Origin cache-poison shape

```text
a reflected ACAO WITHOUT Vary: Origin — a shared cache keyed only
on the URL — an attacker Origin's reflected ACAO poisons the cache
for every subsequent request — a cache-poison+CORS blend.
```

## 8. The `private`/`no-store` bypass — a response that shouldn't cache

```text
an authenticated endpoint should be Cache-Control: private/no-store —
if it's cached, a session-scoped response serves cross-origin — a
separate (non-CORS) leak, but confusable.
```

## 9. The cache-layer greps

```bash
# the app's cache headers + the proxy's CORS
grep -rnoiE 'Cache-Control|Vary|Expires|ETag|cache|Access-Control' <src> | head -20
# the proxy config — nginx/Apache/CDN CORS
grep -rnoiE 'add_header|Access-Control|if.*origin|map.*origin' <src>/nginx.conf <src>/*.conf 2>/dev/null
```

## 10. The Vary/cache decision table

```text
reflected ACAO + Vary:Origin      → per-origin — clean, the vuln is in the check
reflected ACAO + no Vary          → cache-poison surface — a cross-origin ACAO
a cached `*` response             → public — not the vuln
a proxy-overridden ACAO           → the proxy's config is the gate, not the app's
a Max-Age cache                   → a stale permissive preflight persists
```
