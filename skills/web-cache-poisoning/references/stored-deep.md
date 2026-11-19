# Stored deep — the stored copy's every behavior, exhaustively

How the cache stores, serves, and expires a response — the complete mechanics.

---

## 1. The store — the cached response

```text
a cache stores a response per-key — the stored copy is the origin's
response at the time it was cached — every requester of the same key
gets the same stored copy.
```

## 2. The store's key — what determines the stored entry

```text
the key = the request parts that determine which stored copy serves
a request:
- the URL (the default key — scheme + host + path + query)
- the Vary'd headers
- the configured key parts
everything NOT in the key is an unkeyed input.
```

## 3. The store's content — what the copy carries

```text
the stored copy carries the origin's response:
- the body (the HTML, the JSON, the bytes)
- the headers (the Content-Type, the Set-Cookie, the cacheable signals)
- the status (the 200, the 302, the 404)
every requester gets the same stored content.
```

## 4. The serve — the stored copy's request

```text
a request for a key the cache has stored → the cache serves the
stored copy → a HIT — the origin isn't fetched.
a request for a key the cache hasn't stored → the origin is fetched
→ a MISS — the response is stored for the next request.
```

## 5. The serve's confirm — the HIT signal

```bash
curl -sI "$BASE/page?cb=<unique>" | grep -i 'x-cache'
#   X-Cache-Status: HIT → the stored copy served it
```

## 6. The serve's edge — a MISS reflection

```text
a marker reflected on a MISS → the response came from the origin —
a REFLECTION, not a poisoning — the stored copy didn't serve it.
```

## 7. The store's persistence — the TTL

```text
a stored entry lives until its TTL — the deception persists for the
TTL — a short TTL is a short-lived deception; a long TTL is a
persistent one.
```

## 8. The store's expiry — the TTL's end

```text
the stored copy expires on its TTL — a fresh fetch happens on the
next request — the deception's window closed.
```

## 9. The store's blast — the shared copy's reach

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — the deception's blast is the URL's requester base — a
public URL poisons every visitor.
```

## 10. The store's falsifier — a keyed input

```text
a keyed input → a per-input entry → YOUR input's effect is in YOUR
copy only → the clean request doesn't reflect → a different class.
```

## 11. The store's falsifier — a no-cache surface

```text
no front-end cache → no stored copy → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
```

## 12. The store's check — the two-request test

```bash
# the store+serve check — the second request's HIT
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # first — MISS
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # second — HIT?
#   a HIT → the stored copy served it
```
