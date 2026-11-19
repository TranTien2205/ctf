# Detection checklist — a self-audit for finding the cache surface

The checklist that confirms each surface before building the attack.

---

## The cache — does one exist

```text
[ ] a cache-status header — X-Cache-Status, CF-Cache-Status, Age
[ ] a proxy_cache config — an nginx cache
[ ] a vcl_hash config — a Varnish cache
[ ] a cf-cache/cloudflare — a CDN cache
[ ] a Rails.cache/cache_page/flask_caching — an app-level cache
[ ] no status header — check the config anyway
```

## The key — what's keyed

```text
[ ] a Vary header — which headers vary the cache
[ ] a proxy_cache_key template — the configured key parts
[ ] a vcl_hash — the hashed request parts
[ ] a make_cache_key — the app's key builder
[ ] the default key — the URL (scheme + host + URI)
```

## The unkeyed input — the poisoning vector

```text
[ ] an unkeyed header — the app reflects, the cache ignores
[ ] an unkeyed param — a utm, fbclid, a tracking param
[ ] an unkeyed cookie — a cookie not in Vary
[ ] a path-normalization boundary — a URL the cache and app
    normalize differently
[ ] the unkeyed-input check — send it → the stored copy serves it
    to a clean request
```

## The deception surface — the privileged page

```text
[ ] an authenticated page + a shared cache — the URL both the
    privileged and anonymous fetch
[ ] a personalized page + a shared cache — a per-user leak
[ ] a Cache-Control — the page IS cached (a public max-age)
```

## The confirm — the three-part evidence

```text
[ ] the probe request STORED — a HIT on the second identical request
[ ] the keyed input left OUT of the cache key — the unkeyed input
[ ] the reflected value reaching a response the victim receives —
    the clean request reflects the marker
[ ] a reflected header on a MISS is not a poisoning
```

## The blast radius — the shared-store effect

```text
[ ] the URL's requester base — a public URL poisons every visitor
[ ] the TTL — the deception's persistence
[ ] a harmless marker — no destructive payload on a shared store
```

## The confusables — is it really a cache-poisoning

```text
[ ] a fetch READS bytes — web-cors
[ ] a WRITE — web-csrf
[ ] a desync — web-request-smuggling
[ ] a parser diff — web-parser-differential
[ ] an opaque response + a side-channel — web-xs-leaks
[ ] a stored response served to others — web-cache-poisoning
```

## The falsifier — is the surface dead

```text
[ ] the input IS part of the cache key — a keyed input isn't poisonable
[ ] no front-end cache — no stored response
[ ] a Cache-Control: no-store/private — the page isn't cached
[ ] a reflected marker on a MISS — a reflection, not a poisoning
```
