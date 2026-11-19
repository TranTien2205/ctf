# Detection — the cache-poisoning signals

Each signal that names the class, ordered by how cheap it is to find.

---

## The cache — the front-end layer is the entry

```bash
# the cache status — a HIT/MISS/AGE header
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age:|via:|x-served-by|server:|x-varnish|cache-status'
#   X-Cache-Status: HIT/MISS — an nginx proxy_cache
#   CF-Cache-Status: HIT    — a Cloudflare cache
#   Age: N                  — a cached copy's age
#   X-Served-By: cache      — a Varnish/CDN cache
```

```text
a cache-status header → a front-end cache exists → the keying
question is live. no cache-status header doesn't mean no cache —
check the source/config.
```

## The cache-config — which parts of the request are in the key

```bash
# the proxy's cache-key config — which request parts key the entry
grep -rnoiE 'proxy_cache|cache_key|cache_key_string|proxy_cache_key|vary|cache.*vary|Vary:' <src> | head -20
#   proxy_cache_key — the nginx key template
#   Vary: <header> — a response-header that varies the cache
```

```text
the cache key = which request parts determine the stored entry.
the vulnerability: a request part the APPLICATION reads but the
cache DOESN'T key on — an 'unkeyed input'.
```

## The unkeyed-input surface — the poisoning vector

```bash
# an unkeyed header — the app reflects it, the cache ignores it
grep -rnoiE 'X-Forwarded|X-Original|X-Rewrite|Referer|User-Agent|Host|X-Forwarded-Host|X-Forwarded-Scheme|X-Original-URL|X-Host|X-Forwarded-Server' <src> | head -20
# a reflection surface — the app echoes the header back
grep -rnoiE 'header|reflection|echo|reflect|user_agent|referer|request.headers' <src> | head -20
```

```text
the unkeyed input: a request part the app READS (reflects, redirects
on, personalizes on) but the cache key IGNORES. the stored response
carries YOUR input — every other requester's copy serves it.
```

## The normalization-boundary surface — the path confusion

```bash
# a path the cache and the app normalize differently
grep -rnoiE 'normalize|normaliz|redirect|rewrite|path|decode|urldecode|canonical' <src> | head -10
```

```text
a path the cache and the app normalize differently — a static-looking
URL served the dynamic response. the cache stores YOUR request's
response under a URL the victim requests.
```

## The response-vary surface — the key's discriminator

```bash
# a Vary header — which request headers vary the cache
curl -sI "$BASE/" | grep -i 'vary'
#   Vary: Cookie — the cache keys on the cookie → per-session entries
#   Vary: Authorization — the cache keys on auth → per-auth entries
#   (no Vary) — the cache ignores those headers → a shared entry
```

```text
a Vary header names the request headers that determine the stored
entry — a header NOT in Vary is an unkeyed input — the stored
response serves YOUR input to every requester.
```

## The authenticated-page-served-anonymously — the deception shape

```text
the verified card's shape: an authenticated page cached under a URL
the anonymous requester also fetches — the cache serves the
authenticated copy anonymously. the cache keys on the URL, not the
auth state — the stored response is the privileged page.
```

## The signal-to-surface map — which observation names which vector

```text
a X-Cache-Status/CF-Cache header   → a front-end cache — the keying question
a Vary header                      → the key's discriminator — what's keyed
an unkeyed reflected header        → an unkeyed-input poisoning vector
a path normalization boundary      → a path-confusion poisoning
an authenticated page + a shared cache → an authenticated-page-served-
                                        anonymously deception
a cache-buster param               → a key that includes the param —
                                     a cache-buster defeats it
```

## The class-boundary signals — when it's NOT a cache-poisoning

```text
a fetch READS bytes                   → web-cors (a real read)
a server-side fetch                   → web-ssrf
a desync front-end/back-end           → web-request-smuggling
a parser difference on the URL        → web-parser-differential
an opaque response + a side-channel   → web-xs-leaks (a measure)
a stored response served to others    → web-cache-poisoning (a store)
```

## The falsifier — when the surface is dead

```text
the input IS part of the cache key — the poisoned copy is keyed
per-input — the stored response serves YOUR input only to YOUR
requests → no shared poisoning → a different class.
no front-end cache → no stored response → a different class.
```
