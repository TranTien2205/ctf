# Cache status deep — every header's interpretation, exhaustively

The cache-status signals — what each one means for the attack.

---

## 1. The X-Cache-Status family — nginx's status

```text
X-Cache-Status: HIT          — the stored copy served the request —
                               a cacheable URL (and possibly already
                               stored by a prior request).
X-Cache-Status: MISS         — the request went to the origin — the
                               stored copy doesn't exist yet — a
                               first-request or an uncached URL.
X-Cache-Status: EXPIRED      — the stored copy expired — a fresh
                               fetch happened — the TTL passed.
X-Cache-Status: STALE        — the stored copy served a stale entry —
                               the TTL passed but the proxy served
                               the old copy.
X-Cache-Status: BYPASS       — the cache was bypassed — the request
                               went to the origin regardless.
```

## 2. The CF-Cache-Status — Cloudflare's status

```text
CF-Cache-Status: HIT         — Cloudflare served the stored copy.
CF-Cache-Status: MISS        — Cloudflare fetched the origin.
CF-Cache-Status: DYNAMIC     — the page is dynamic — not cached by
                               Cloudflare (a cache-bypass or a rule).
CF-Cache-Status: EXPIRED     — the stored copy expired.
```

## 3. The Age header — the stored copy's age

```bash
curl -sI "$BASE/page?cb=<unique>" | grep -i 'age:'
#   Age: 45 — the stored copy is 45 seconds old — the TTL's remaining
#             window is (TTL - 45)
```

```text
a stored copy's age tells you how long it's been stored — a high
Age on a poisoned page means the deception persists; a low Age is
a fresh store.
```

## 4. The Via / X-Varnish — the proxy chain

```text
Via: 1.1 varnish              — a Varnish cache in the path
X-Varnish: 12345 12344        — a Varnish hit (two IDs = a stored copy)
Via: 1.1 vegur                — a Caddy/vegar proxy
X-Cache: Hit from cloudfront  — a CloudFront cache
X-Cache: Hit                  — a generic cache hit
```

## 5. The cacheable-signal map — which pages are cached

```text
a cacheable page    — a Cache-Control: public, max-age or a static
                      URL — the cache stores it.
an uncached page    — a Cache-Control: no-store/private or a 302 —
                      the cache doesn't store it.
a per-session page  — a Vary: Cookie — the cache keys on the cookie
                      — a per-session copy, not a shared one.
```

## 6. The stored-response confirm — the two-request test

```bash
# the probe request — a HIT on the second identical request
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'  # first — MISS
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'  # second — HIT?
#   the second request's cache-status shows HIT — the stored copy served it
```

```text
the confirm: the probe request STORES — a second identical request
shows a cache HIT — the stored copy served YOUR input.
```

## 7. The MISS-vs-HIT distinction — a reflection vs a store

```text
a marker reflected on a MISS — the response came from the origin —
a REFLECTION, not a poisoning.
a marker reflected on a HIT — the stored copy served it — the
stored copy carries YOUR input — a poisoning.
```

## 8. The cache-key check — is the input keyed

```bash
# send the input → check the stored copy serves it to a clean request
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'  # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   <marker> reflected → unkeyed → poisonable
#   <marker> NOT reflected → keyed → a different class
```

## 9. The deception confirm — the wrong-context serve

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'  # MISS — stores
# an anonymous GET — the stored copy serves it
curl "$BASE/settings.html?cb=<unique>"   # anonymous — HIT + the privileged page
```

```text
the deception's confirm: the anonymous request returns the privileged
page (a 200 with the content, not a 302 to login) AND a cache HIT —
the stored copy served the privileged content to a different context.
```

## 10. The TTL question — the deception's persistence

```bash
# the stored entry's age — the TTL's remaining window
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'age|cache-control|expires|max-age'
#   the Age + the max-age → the TTL's remaining window
```

## 11. The per-proxy status map — which header for which layer

```text
nginx        → X-Cache-Status: HIT/MISS/EXPIRED/STALE/BYPASS
Varnish      → X-Varnish: <two IDs> (a hit) or <one ID> (a miss)
Cloudflare   → CF-Cache-Status: HIT/MISS/DYNAMIC/EXPIRED
CloudFront   → X-Cache: Hit from cloudfront / Miss
generic      → Via, Age, X-Cache
```

## 12. The falsifier — when a status is misleading

```text
a HIT on a different-keyed URL → a stored copy, but keyed per-input →
a different class.
a HIT on the same URL but a keyed input → a per-input copy → a
different class.
a MISS → no stored copy → no poisoning.
```
