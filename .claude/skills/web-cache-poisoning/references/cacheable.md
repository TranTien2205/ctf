# Cacheable — the page's cacheability, exhaustively

The cacheable-signal map — which pages are cached and which aren't.

---

## 1. The Cache-Control header — the cacheability signal

```bash
curl -sI "$BASE/" | grep -i 'cache-control'
#   Cache-Control: public, max-age=300 → a cacheable page
#   Cache-Control: no-store → a non-cached page
#   Cache-Control: private → a per-user page (not shared)
#   Cache-Control: no-cache → a revalidate-every-request page
```

## 2. The cacheable signals — which pages are cached

```text
a Cache-Control: public, max-age → a cacheable page → a shared store
a Cache-Control: private → a per-user page → not a shared store
a Cache-Control: no-store → a non-cached page → no stored copy
a Cache-Control: no-cache → a revalidate page → a fresh fetch each time
an ETag / a Last-Modified → a cacheable page → a revalidation surface
```

## 3. The per-status cacheability — which statuses are cached

```text
a 200 → usually cached → a shared store
a 301/302 → sometimes cached → a redirect store
a 404 → sometimes cached → a cached error
a 500 → rarely cached → a fresh fetch
```

## 4. The per-method cacheability — which methods are cached

```text
a GET → usually cached → the shared store
a HEAD → usually cached → a per-method store
a POST → rarely cached → a per-method entry or uncached
an OPTIONS → rarely cached → a per-method entry
```

## 5. The per-URL cacheability — which URLs are cached

```text
a static URL (.css, .js, .png) → usually cached → a shared store
a dynamic URL (.php, a route) → sometimes cached → a configured store
a parameterized URL → keyed per-param → a per-param store
an authenticated URL → usually keyed per-session or uncached
```

## 6. The Vary's effect — the keyed-header cacheability

```text
a Vary: Cookie → a per-session entry → a keyed cookie
a Vary: Accept-Encoding → a per-encoding entry → a keyed encoding
a Vary: X-Custom → a per-input entry → a keyed header
```

## 7. The cacheability check — is the page cached

```bash
# the page's cacheability — the Cache-Control + the status
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'cache-control|x-cache|cf-cache|age|etag'
#   a Cache-Control: public, max-age + a HIT → a cacheable page
#   a Cache-Control: no-store → a non-cached page
```

## 8. The cacheability's falsifier — a non-cached page

```text
a Cache-Control: no-store/private → the page isn't cached → no
stored copy → a different class.
```

## 9. The cacheability's use — the shared store

```text
a cacheable page → a stored copy → the poisoning surface.
a non-cached page → no stored copy → a different class.
```

## 10. The per-stack cacheability — which stacks cache

```text
nginx proxy_cache → a configured TTL → a shared store
Varnish → a configured TTL → a shared store
Cloudflare → a cache rule → a configured store
CloudFront → a cache policy → a configured store
app-level → a configured key → a configured store
```
