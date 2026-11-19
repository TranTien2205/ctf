# Detection deep — the cache-poisoning signals, exhaustively

Every signal that names the class, ordered by how cheap it is to find.

---

## The cache — the front-end layer is the entry

```bash
# the cache status — a HIT/MISS/AGE header
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age:|via:|x-served-by|server:|x-varnish|cache-status|x-cache-hits'
#   X-Cache-Status: HIT/MISS — an nginx proxy_cache
#   CF-Cache-Status: HIT    — a Cloudflare cache
#   Age: N                  — a cached copy's age
#   X-Served-By: cache      — a Varnish/CDN cache
#   X-Cache-Hits: N         — a hit count
```

```text
a cache-status header → a front-end cache exists → the keying
question is live. no cache-status header doesn't mean no cache —
check the source/config.
```

## The cache-config — which parts of the request are in the key

```bash
# the proxy's cache-key config — which request parts key the entry
grep -rnoiE 'proxy_cache|cache_key|cache_key_string|proxy_cache_key|vary|cache.*vary|Vary:|vcl_hash|hash_data|make_cache_key' <src> | head -30
#   proxy_cache_key — the nginx key template
#   vcl_hash — the Varnish key builder
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
grep -rnoiE 'X-Forwarded|X-Original|X-Rewrite|Referer|User-Agent|Host|X-Forwarded-Host|X-Forwarded-Scheme|X-Original-URL|X-Host|X-Forwarded-Server|Accept-Language|Accept-Charset|Accept' <src> | head -30
# a reflection surface — the app echoes the header back
grep -rnoiE 'header|reflection|echo|reflect|user_agent|referer|request.headers|request\.META|request\.env' <src> | head -30
```

```text
the unkeyed input: a request part the app READS (reflects, redirects
on, personalizes on) but the cache key IGNORES. the stored response
carries YOUR input — every requester's copy serves it.
```

## The normalization-boundary surface — the path confusion

```bash
# a path the cache and the app normalize differently
grep -rnoiE 'normalize|normaliz|redirect|rewrite|path|decode|urldecode|canonical|URI|uri' <src> | head -15
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
#   Vary: Accept-Encoding — per-compression entries
#   Vary: Authorization — per-auth entries
#   (no Vary) — the cache ignores those headers → a shared entry
```

```text
a Vary header names the request headers that determine the stored
entry — a header NOT in Vary is an unkeyed input — the stored
response serves YOUR input to every requester.
```

## The authenticated-page-served-anonymously — the deception shape

```bash
# the authenticated-page surface — a privileged page + a shared cache
grep -rnoiE 'settings|profile|dashboard|admin|authenticated|session|personalized|login|logout' <src> | head -20
```

```text
the verified card's shape: an authenticated page cached under a URL
the anonymous requester also fetches — the cache keys on the URL,
not the auth state — the stored copy is the privileged page served
to anyone.
```

## The no-store surface — when the page isn't cacheable

```bash
# a Cache-Control: no-store or private — the page isn't cached
curl -sI "$BASE/settings.html" | grep -i 'cache-control'
#   Cache-Control: no-store/private — the page isn't cached
#   Cache-Control: public — the page IS cached → the deception surface
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
a Cache-Control: no-store/private  → the page isn't cached → a different class
a public Cache-Control             → the page IS cached → the deception surface
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
the input IS part of the cache key — the stored copy is keyed per-
input → no shared poisoning → a different class.
no front-end cache → no stored response → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
```
