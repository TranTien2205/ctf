# CDN and proxy — the cache layers, per vendor

The cache layer per proxy — where the keying and the unkeyed input live.

---

## 1. nginx — the dominant CTF cache

```text
nginx's proxy_cache — the default key is the URL (scheme + host + URI)
— headers are unkeyed unless the config adds them or the response
carries Vary.
```

```nginx
# a typical nginx config — the key template
proxy_cache_key $scheme$proxy_host$request_uri;   # the URL (scheme+host+URI)
proxy_cache_valid 200 60m;                        # a 60-minute TTL
add_header X-Cache-Status $upstream_cache_status; # the status header
```

```text
the unkeyed input: a header the app reads but $request_uri doesn't
carry — a X-Forwarded-* or a reflected header.
```

## 2. Varnish — the other reverse-proxy

```vcl
# a Varnish config — the cache + the key
sub vcl_hash {
  hash_data(req.url);
  hash_data(req.http.Host);
  # a header NOT hashed is unkeyed
}
```

```text
Varnish's key is built by vcl_hash — the hashed parts are keyed —
the rest are unkeyed — a hash_data(req.http.X-Forwarded-Host) keys it.
```

## 3. Cloudflare — the CDN edge

```text
Cloudflare's cache — a CF-Cache-Status header — a cache rule per URL —
the edge caches by the URL + a set of configured headers — an unkeyed
input is a header the edge ignores.
```

```text
CF-Cache-Status: HIT/MISS/DYNAMIC — Cloudflare's status.
a DYNAMIC page isn't cached — a cache-bypass or a rule.
```

## 4. CloudFront — AWS's CDN

```text
CloudFront's cache — an X-Cache: Hit from cloudfront — a cache policy
per URL — the edge caches by the URL + the policy's headers/cookies/
query strings — an unkeyed input is a request part the policy ignores.
```

## 5. Akamai — the enterprise CDN

```text
Akamai's cache — an X-Cache header — a cache key per URL — the edge
caches by the URL + the configured parts — an unkeyed input is a
request part the key ignores.
```

## 6. Fastly — the Varnish-based CDN

```text
Fastly's cache — an X-Served-By / X-Cache — a VCL-based cache like
Varnish — the key is built by the VCL's hash — an unkeyed input is a
request part the VCL doesn't hash.
```

## 7. The app-level cache — Rails/Django/Flask

```text
Rails    — a Rails.cache / a fragment/page cache — a make_cache_key
           or a cache_key — the key is the URL or a configured template.
Django   — a cache_page / a Vary — the key is the URL + the Vary'd
           headers.
Flask    — a flask_caching / a make_cache_key — the key is the URL or
           a configured template.
```

## 8. The per-layer status map — which header names which layer

```text
nginx        → X-Cache-Status: HIT/MISS/EXPIRED/STALE/BYPASS
Varnish      → X-Varnish: <two IDs> (a hit) or <one ID> (a miss)
Cloudflare   → CF-Cache-Status: HIT/MISS/DYNAMIC/EXPIRED
CloudFront   → X-Cache: Hit from cloudfront / Miss
Fastly       → X-Served-By: cache-<id> / X-Cache: HIT
Akamai       → X-Cache: TCP_HIT / TCP_MISS
generic      → Via, Age, X-Cache
```

## 9. The per-layer key-source — where the key's config lives

```text
nginx        → proxy_cache_key in the conf
Varnish      → vcl_hash's hash_data calls
Cloudflare   → a cache rule in the dashboard/API
CloudFront   → a cache policy's headers/cookies/query
Fastly       → the VCL's hash
app-level    → the app's make_cache_key / cache_page / Vary
```

## 10. The per-layer unkeyed-input surface — which inputs are usually unkeyed

```text
nginx (default)   → any header (the key is the URL) — a wide surface
Varnish           → any header not in vcl_hash — a wide surface
Cloudflare        → any header not in the cache rule — a configured surface
CloudFront        → any part not in the cache policy — a configured surface
app-level         → any part not in the key template — a configured surface
```

## 11. The per-layer detection — which layer you're facing

```bash
# the status + the via — which layer
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age|via|x-varnish|x-served-by|server'
#   X-Cache-Status + Server: nginx → an nginx cache
#   CF-Cache-Status + Server: cloudflare → a Cloudflare cache
#   X-Varnish → a Varnish cache
```

## 12. The per-layer falsifier — when the layer's keying is correct

```text
every candidate input IS keyed (in the proxy_cache_key, the vcl_hash,
the cache policy) → no unkeyed input → no poisoning vector → a
different class.
```
