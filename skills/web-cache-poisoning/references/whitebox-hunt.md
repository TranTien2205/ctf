# Whitebox hunt — where the cache-poisoning surface lives in source

The grep paths that find each surface.

---

## The cache — the front-end layer

```bash
# an nginx proxy_cache — the dominant CTF cache
grep -rnoiE 'proxy_cache|cache_key|proxy_cache_key|fastcgi_cache|keys_zone|X-Cache-Status|proxy_cache_valid' <src> | head -20
# a Varnish — the other reverse-proxy
grep -rnoiE 'vcl_hash|hash_data|Varnish|X-Varnish|varnish|sub vcl' <src> | head -10
# an app-level cache — Rails/Django/Flask
grep -rnoiE 'Rails.cache|cache_page|@cache|flask_caching|fragment|action_cache|make_cache_key' <src> | head -20
# a CDN — Cloudflare/edge
grep -rnoiE 'cf-cache|cloudflare|edge|cdn' <src> | head -10
```

## The key — the unkeyed-input surface

```bash
# the key's config — which request parts key the entry
grep -rnoiE 'proxy_cache_key|cache_key|vcl_hash|hash_data|make_cache_key|Vary|vary' <src> | head -20
# the unkeyed-input surface — the app reads, the cache ignores
grep -rnoiE 'X-Forwarded|X-Original|X-Rewrite|Referer|User-Agent|Accept-Language|Accept-Charset|Accept|header|reflection|echo|request.headers|request\.META|request\.env' <src> | head -30
```

## The path-normalization surface — the route confusion

```bash
# a path the cache and the app normalize differently
grep -rnoiE 'normalize|redirect|rewrite|path|decode|urldecode|canonical|URI|uri|route|url_for' <src> | head -15
```

## The authenticated/deception surface — the privileged page

```bash
# the privileged page — a settings/profile/dashboard
grep -rnoiE 'settings|profile|dashboard|admin|authenticated|session|personalized|login|logout|private' <src> | head -20
# a Cache-Control — the cacheable surface
grep -rnoiE 'Cache-Control|no-store|private|public|max-age' <src> | head -10
```

## The per-stack surface map — where each layer lives

```text
nginx        — a proxy_cache + a proxy_cache_key + an X-Cache-Status
Varnish      — a vcl_hash + a hash_data + an X-Varnish
Cloudflare   — a CF-Cache-Status + a cache rule
Rails        — a Rails.cache + a fragment/page cache
Django       — a cache_page + a Vary
Flask        — a flask_caching + a make_cache_key
```

## The unkeyed-input greps — the poisoning vector

```bash
# an X-Forwarded-Host — a host-rewrite
grep -rnoiE 'X-Forwarded-Host|X-Forwarded-Server|X-Host' <src> | head -10
# an X-Original-URL/X-Rewrite-URL — a path-rewrite
grep -rnoiE 'X-Original-URL|X-Rewrite-URL|X-Original' <src> | head -10
# an X-Forwarded-Scheme — a scheme-downgrade
grep -rnoiE 'X-Forwarded-Scheme|X-Forwarded-Proto' <src> | head -10
# a reflected header — a Referer/User-Agent/Accept
grep -rnoiE 'Referer|User-Agent|Accept-Language|Accept-Charset|Accept' <src> | head -10
# a reflection surface — the app echoes the header
grep -rnoiE 'request.headers|request\.META|request\.env|echo|reflect' <src> | head -10
```

## The deception-surface greps — the stored-response confusion

```bash
# an authenticated page — a privileged URL
grep -rnoiE 'settings|profile|dashboard|admin|authenticated|session' <src> | head -20
# a shared cache — the URL both the privileged and anonymous fetch
grep -rnoiE 'cache|proxy_cache|cache_page|flask_caching' <src> | head -10
```

## The signal-to-surface map — what each grep names

```text
a 'proxy_cache|cache_key|X-Cache-Status' → an nginx cache — the keying question
a 'vcl_hash|hash_data|Varnish'           → a Varnish cache
a 'cf-cache|cloudflare'                  → a Cloudflare cache
a 'Rails.cache|cache_page|flask_caching' → an app-level cache
a 'Vary|vary'                            → the key's discriminator
a 'X-Forwarded|X-Original|X-Rewrite'     → an unkeyed-header surface
a 'Referer|User-Agent|Accept'            → a reflected-header surface
a 'normalize|redirect|rewrite|path'      → a path-normalization boundary
a 'settings|profile|dashboard|admin'     → an authenticated/deception surface
a 'Cache-Control|no-store|private'       → a cacheable surface
```

## The falsifier — when the surface is dead

```text
every candidate input IS keyed → no unkeyed input → no poisoning
vector → a different class.
no front-end cache → no stored response → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
```
