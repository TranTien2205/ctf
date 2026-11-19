# Frameworks deep — the cache layer per stack, exhaustively

The cache surface per framework — where the keying and the unkeyed input live.

---

## 1. nginx + app — the dominant CTF shape

```text
an nginx proxy_cache in front of a Rails/Django/Flask/Express app —
the default key is the URL — headers are unkeyed unless the config
adds them — a wide unkeyed-input surface.
```

```nginx
proxy_cache_key $scheme$proxy_host$request_uri;   # the URL (scheme+host+URI)
proxy_cache_valid 200 60m;                        # a 60-minute TTL
add_header X-Cache-Status $upstream_cache_status; # the status header
```

## 2. Varnish + app — the VCL-keyed cache

```vcl
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

## 3. Rails + a cache — the app-level cache

```text
Rails's fragment/page cache — a Rails.cache or a caches_page — the
key is the URL or a configured template — an unkeyed input is a
request part the key doesn't carry.
```

## 4. Django + a cache — the per-URL cache

```text
Django's cache_page — a per-URL cache — the key is the URL + the
Vary'd headers — an unkeyed input is a request part not in Vary.
```

## 5. Flask + a cache — the flask_caching cache

```text
Flask's flask_caching — a make_cache_key — the key is the URL or a
configured template — an unkeyed input is a request part the key
doesn't carry.
```

## 6. Express + a cache — a middleware cache

```text
an Express middleware cache (apicache, a custom cache) — the key is
the URL or a configured template — an unkeyed input is a request
part the key doesn't carry.
```

## 7. Cloudflare + app — the CDN edge

```text
Cloudflare's edge cache — a cache rule per URL — the edge caches by
the URL + a configured set of headers/cookies/query — an unkeyed
input is a request part the rule ignores.
```

## 8. CloudFront + app — the AWS edge

```text
CloudFront's edge cache — a cache policy per URL — the edge caches
by the URL + the policy's headers/cookies/query strings — an unkeyed
input is a request part the policy ignores.
```

## 9. Fastly + app — the VCL edge

```text
Fastly's edge cache — a VCL-based cache — the key is built by the
VCL's hash — an unkeyed input is a request part the VCL doesn't hash.
```

## 10. Akamai + app — the enterprise edge

```text
Akamai's edge cache — a cache key per URL — the edge caches by the
URL + the configured parts — an unkeyed input is a request part the
key ignores.
```

## 11. The per-stack unkeyed-input map — which inputs are usually unkeyed

```text
nginx (default)    → any header (the key is the URL) — a wide surface
Varnish            → any header not in vcl_hash — a wide surface
Rails              → any part not in the key template — a configured surface
Django             → any header not in Vary — a configured surface
Flask              → any part not in make_cache_key — a configured surface
Express            → any part not in the cache key — a configured surface
Cloudflare         → any header not in the cache rule — a configured surface
CloudFront         → any part not in the cache policy — a configured surface
Fastly             → any part not in the VCL hash — a configured surface
Akamai             → any part not in the cache key — a configured surface
```

## 12. The per-stack falsifier — when the stack's keying is correct

```text
every candidate input IS keyed (in the proxy_cache_key, the vcl_hash,
the cache rule, the policy, the template) → no unkeyed input → no
poisoning vector → a different class.
```
