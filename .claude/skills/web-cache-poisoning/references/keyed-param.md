# Keyed param — the cache-buster and the param-keying question, exhaustively

The keyed vs unkeyed param distinction — a cache-buster vs a poisonable param.

---

## 1. The keyed param — a per-value entry

```text
a keyed param keys the cache entry per-value — YOUR param's effect
is in YOUR copy only — the stored response serves it to YOUR requests,
not a different requester.
```

```bash
# a keyed param — a utm/fbclid the cache includes in the key
curl "$BASE/page?utm=<payload>"   # stored under a per-utm key
# a clean request without the param — no <payload>
curl "$BASE/page"                # not poisoned
```

```text
a keyed param isn't poisonable — a different requester gets a
different key — the stored copy is yours.
```

## 2. The unkeyed param — a poisonable input

```text
an unkeyed param the app reflects but the cache ignores — the stored
copy carries YOUR param's effect under the shared URL — every
requester's copy serves it.
```

```bash
# an unkeyed param — the app reflects, the cache ignores
curl "$BASE/page?cb=<unique>&utm=<payload>"   # stored under /page?cb=<unique>
curl "$BASE/page?cb=<unique>"                 # <payload> reflected? → poisoned
```

## 3. The cache-buster — a keyed param the app ignores

```text
a keyed param the app ignores keys the entry per-value — the stored
response is YOUR requests only — a cache-buster defeats the poisoning.
a random keyed param is a cache-buster — a fresh entry each value.
```

```bash
# a cache-buster — a keyed param the app ignores
curl "$BASE/page?cb=<unique>&_=<random>" -H 'X-Forwarded-Host: <marker>'
# the stored copy is keyed per-_ — a fresh entry, not a poisoned one
```

## 4. The param-keying check — is the param in the key

```bash
# send the param → check the stored copy serves it to a clean request
curl "$BASE/page?cb=<unique>&utm=<marker>"   # store it
curl "$BASE/page?cb=<unique>"                # a clean request — does it reflect <marker>?
#   <marker> reflected → unkeyed param → poisonable
#   <marker> NOT reflected → keyed param → a different class
```

## 5. The default param-key — usually keyed

```text
the default nginx proxy_cache_key includes $request_uri — the full
URI including the query string — the params ARE keyed by default.
an UNKEYED param is the exception — a stripped param or a
normalization that drops it.
```

## 6. The param-stripping normalization — an unkeyed param

```nginx
# a config that strips a param — an unkeyed param
proxy_cache_key $scheme$proxy_host$uri;   # $uri drops the query → the params unkeyed
# or a map that drops a param — a stripped utm
```

```text
a param stripped from the key is an unkeyed input — the app reads it,
the cache ignores it — a poisonable param.
```

## 7. The tracked-param confusion — a utm/fbclid

```text
a tracking param the app reflects (a utm, fbclid, gclid) — usually
KEYED (in $request_uri) — but a config that strips it makes it
unkeyed — a poisonable param.
```

```bash
# the utm — check it's reflected and unkeyed
curl "$BASE/page?utm=<marker>"   # stored under a per-utm key?
curl "$BASE/page?utm=<marker>"   # HIT? the stored copy's effect?
```

## 8. The param-vs-header vector — which to poison

```text
a keyed param + an unkeyed header → poison the header.
a keyed param + a keyed header → no unkeyed input → a different class.
an unkeyed param → the param vector — a poisonable param.
```

## 9. The keyed-param falsifier — a per-value entry

```text
a keyed param isn't poisonable — a different requester gets a
different key — the stored copy is yours. record it: 'the <param>
IS keyed — a per-value entry — not a shared poisoning'.
```

## 10. The param-keying matrix — which params are usually keyed

```text
param              keyed?              the check
a query param      yes (in $request_uri)  — usually keyed
a stripped param   no                   → the param vector
a path segment     yes (in $uri)        — always keyed
a fragment         no (not sent)        — not a poisoning vector
```

## 11. The param-keying config — where the strip happens

```bash
# the nginx config — is the param in the key
grep -rnoiE 'proxy_cache_key|cache_key|\$uri|\$request_uri|map|rewrite' <src> | head -10
#   $uri (without the query) → the params unkeyed
#   $request_uri → the params keyed
```

## 12. The keyed-param's use — the cache-buster you control

```bash
# a cache-buster you control — a unique keyed param per probe
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'  # stored under /page?cb=<unique>
curl "$BASE/page?cb=<unique>"   # the stored copy serves it
```

```text
a keyed param you control is the cache-buster for the POISONING
request — a unique key per probe — the stored copy is YOUR probe's.
```
