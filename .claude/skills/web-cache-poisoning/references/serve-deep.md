# Serve deep — the stored copy's serve, exhaustively

How the stored copy reaches a requester — the serve's mechanics.

---

## 1. The serve — the stored copy's request

```text
a request for a key the cache has stored → the cache serves the
stored copy → a HIT — the origin isn't fetched.
a request for a key the cache hasn't stored → the origin is fetched
→ a MISS — the response is stored for the next request.
```

## 2. The serve's confirm — the HIT signal

```bash
curl -sI "$BASE/page?cb=<unique>" | grep -i 'x-cache'
#   X-Cache-Status: HIT → the stored copy served it
```

## 3. The serve's edge — a MISS reflection

```text
a marker reflected on a MISS → the response came from the origin —
a REFLECTION, not a poisoning — the stored copy didn't serve it.
```

## 4. The serve's keyedness — the per-input entry

```text
a keyed input → a per-input entry → the serve is YOUR copy, not a
shared one — a different requester gets a different key — a keyed
input isn't poisonable.
```

## 5. The serve's deception — the wrong-context serve

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # stores it
# an anonymous GET — the stored copy serves it to a different context
curl "$BASE/settings.html?cb=<unique>"   # the privileged page → deception
```

## 6. The serve's blast — the requester base

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — the deception's blast is the URL's requester base — a
public URL poisons every visitor.
```

## 7. The serve's TTL — the serve's window

```text
a stored entry lives until its TTL — the serve's window is the TTL —
a short TTL is a short-lived deception; a long TTL is a persistent
one.
```

## 8. The serve's cachebuster — the same-key check

```bash
# the stored copy is keyed per-cachebuster — the clean request MUST
# use the same key
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # stored under /page?cb=<unique>
curl "$BASE/page?cb=<unique>"   # the stored copy serves it
curl "$BASE/page?cb=<other>"    # a different key — the clean copy
```

## 9. The serve's check — the two-request test

```bash
# the store+serve check — the second request's HIT
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # first — MISS
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # second — HIT?
#   a HIT → the stored copy served it
```

## 10. The serve's falsifier — a keyed input

```text
a keyed input → a per-input entry → YOUR input's effect is in YOUR
copy only → the clean request doesn't reflect → a different class.
```

## 11. The serve's falsifier — a no-cache surface

```text
no front-end cache → no stored copy → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
```

## 12. The serve's status — the cache-status signals

```text
X-Cache-Status: HIT → the stored copy served it
X-Cache-Status: MISS → the origin served it → a fresh fetch
X-Cache-Status: EXPIRED → the stored copy expired → a fresh fetch
X-Cache-Status: STALE → the proxy served a stale copy
X-Cache-Status: BYPASS → the cache was bypassed → the origin served it
```
