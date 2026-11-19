# Framework matrix — the cache-poisoning surface per stack

Each framework's cache, its keying, and the greps that find it.

---

## 1. nginx proxy_cache — the dominant CTF cache

```nginx
# a typical nginx config — the cache + the key
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
proxy_cache my_cache;
proxy_cache_key $scheme$proxy_host$request_uri;
#   the key = scheme + host + URI — headers are unkeyed unless
#   the config adds them or the response carries Vary
add_header X-Cache-Status $upstream_cache_status;
```

```bash
# the nginx config surface
grep -rnoiE 'proxy_cache|cache_key|proxy_cache_key|fastcgi_cache|keys_zone|X-Cache-Status' <src> | head -20
```

```text
the nginx shape — a proxy_cache + a key template — the verified
card's cache. the key is the URI; the headers are unkeyed unless
the config adds them.
```

## 2. Varnish — the other reverse-proxy cache

```vcl
# a Varnish config — the cache + the key
sub vcl_hash {
  hash_data(req.url);
  hash_data(req.http.Host);  # the host is keyed
  # a header NOT hashed is unkeyed
}
```

```bash
# the Varnish config surface
grep -rnoiE 'vcl_hash|hash_data|Varnish|X-Varnish|varnish' <src> | head -10
```

## 3. Cloudflare — the CDN cache

```text
# a CF-Cache-Status header — a Cloudflare cache
# the cache rules — which URLs and headers are cached
# an unkeyed input — a header/parameter the edge ignores
```

```bash
# the Cloudflare surface
curl -sI "$BASE/" | grep -iE 'cf-cache|cf-ray|server: cloudflare'
```

## 4. Rack::Cache / Rails — an app-level cache

```ruby
# a Rails cache — a fragment/page cache
Rails.cache.fetch(key) { render }
#   the key is the app's choice — an unkeyed input is a header/param
#   the cache ignores
```

```bash
# the Rails cache surface
grep -rnoiE 'Rails.cache|cache|fragment|page_cache|action_cache' <src> | head -10
```

## 5. Django — a per-view cache

```python
# a Django per-view cache — a cache_page decorator
@cache_page(60)
def view(request): ...
#   the key is the URL — headers are unkeyed unless Vary'd
```

```bash
# the Django cache surface
grep -rnoiE 'cache_page|cache|Vary|@cache' <src> | head -10
```

## 6. Flask — a flask_caching cache

```python
# a flask_caching — a cached decorator
@cache.cached(timeout=60)
def view(): ...
#   the key is the URL + the make_cache_key — headers unkeyed
```

```bash
# the Flask cache surface
grep -rnoiE 'flask_caching|@cache|cache.cached|make_cache_key' <src> | head -10
```

## 7. The per-stack keying — the unkeyed-input surface

```text
stack        the key                      the unkeyed-input surface
nginx        $scheme$proxy_host$request_uri headers, params (if stripped)
Varnish      req.url + req.http.Host       headers not in vcl_hash
Cloudflare   the URL + the cache rules     headers/params the edge ignores
Rails        the app's cache key           headers/params not in the key
Django       the URL + Vary                headers not in Vary
Flask        the URL + make_cache_key      headers/params not in the key
```

## 8. The per-stack deception surface — the stored-response confusion

```text
nginx        — an authenticated page served anonymously (the card)
Varnish      — a stored copy served to the wrong context
Cloudflare   — an edge-cached page served to the wrong session
Rails/Django — a personalized page served publicly
Flask        — a cached page served to the wrong requester
```

## 9. The per-stack grep-map — finding the surface

```bash
# nginx
grep -rnoiE 'proxy_cache|cache_key|X-Cache-Status|keys_zone' <src>
# Varnish
grep -rnoiE 'vcl_hash|hash_data|Varnish|X-Varnish' <src>
# Cloudflare
curl -sI "$BASE/" | grep -iE 'cf-cache|cf-ray|cloudflare'
# Rails
grep -rnoiE 'Rails.cache|cache_page|fragment|action_cache' <src>
# Django
grep -rnoiE 'cache_page|@cache|Vary' <src>
# Flask
grep -rnoiE 'flask_caching|@cache|cache.cached' <src>
```
