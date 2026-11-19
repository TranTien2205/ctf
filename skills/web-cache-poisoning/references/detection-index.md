# Detection index — every detection signal, indexed

The complete index of detection signals — the cache, the key, the unkeyed input.

---

## 1. The cache-presence signals — a cache exists

```bash
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age:|via:|x-varnish|x-served-by|server|x-cached'
#   X-Cache-Status: HIT/MISS — nginx
#   CF-Cache-Status: HIT/MISS/DYNAMIC — Cloudflare
#   X-Varnish: <two IDs> — Varnish
#   X-Served-By: cache-<id> — Fastly
#   X-Cache: Hit from cloudfront — CloudFront
#   Age: <n> — a stored copy's age
#   Via: 1.1 varnish — a proxy chain
```

## 2. The key signals — what's keyed

```bash
curl -sI "$BASE/" | grep -i 'vary'
#   Vary: Cookie → keyed on the cookie
#   Vary: Accept-Encoding → keyed on the encoding
#   Vary: X-Custom → keyed on X-Custom
#   (no Vary) → the headers unkeyed
```

## 3. The key-source signals — the configured key

```bash
grep -rnoiE 'proxy_cache_key|cache_key|vcl_hash|hash_data|make_cache_key|Vary' <src> | head -10
#   $uri → the params unkeyed; $request_uri → the params keyed
#   a hash_data(req.http.X-Forwarded-Host) → that header keyed
```

## 4. The unkeyed-input signals — the app's reflected headers

```bash
grep -rnoiE 'X-Forwarded|X-Original|X-Rewrite|Referer|User-Agent|Accept-Language|Accept-Charset|Accept|header|reflection|echo|request.headers|request\.META|request\.env' <src> | head -30
```

## 5. The deception signals — the privileged page

```bash
grep -rnoiE 'settings|profile|dashboard|admin|authenticated|session|personalized|login|private' <src> | head -20
```

## 6. The cacheable signals — the cached page

```bash
curl -sI "$BASE/" | grep -iE 'cache-control|etag|last-modified'
#   Cache-Control: public, max-age → a cacheable page
#   Cache-Control: no-store/private → a non-cached page
#   ETag / Last-Modified → a cacheable page
```

## 7. The per-surface signal map — which signals name which surface

```text
a 'proxy_cache|cache_key|X-Cache-Status' → an nginx cache
a 'vcl_hash|hash_data|Varnish'           → a Varnish cache
a 'cf-cache|cloudflare'                  → a Cloudflare cache
a 'Rails.cache|cache_page|flask_caching' → an app-level cache
a 'Vary|vary'                            → the key's discriminator
a 'X-Forwarded|X-Original|X-Rewrite'     → an unkeyed-header surface
a 'Referer|User-Agent|Accept'            → a reflected-header surface
a 'settings|profile|dashboard|admin'     → a deception surface
a 'Cache-Control|no-store|private'       → a cacheable surface
a 'normalize|redirect|rewrite|path'      → a normalization boundary
```

## 8. The detection's falsifier — when the surface is dead

```text
every candidate input IS keyed → no unkeyed input → a different class.
no front-end cache → no stored response → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
a reflected marker on a MISS → a reflection, not a poisoning → a
different class.
```
