# Detection confirm — the cache-poisoning's three-part evidence, mapped

The complete confirm — the stored copy, the unkeyed input, the victim serve.

---

## 1. The proof standard — the three-part evidence

```text
the poison confirm requires three independent parts:
1. the probe request STORED — a cache HIT on the second identical request
2. the keyed input left OUT of the cache key — the unkeyed input
3. the reflected value reaching a response the victim receives — the
   clean request reflects the marker
a reflected header on a MISS is not a poisoning.
```

## 2. The stored copy — the HIT confirm

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # first — MISS
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # second — HIT?
curl -sI "$BASE/page?cb=<unique>" | grep -i 'x-cache'
#   X-Cache-Status: HIT → the stored copy served it
```

## 3. The unkeyed input — the keyedness confirm

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   reflected → unkeyed → poisonable; NOT reflected → keyed → a different class
```

## 4. The victim response — the clean-request confirm

```bash
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   <marker> reflected → the stored copy serves YOUR input to a different
#   requester → the poisoning confirm
```

## 5. The deception confirm — the wrong-context serve

```bash
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # stores the privileged copy
curl "$BASE/settings.html?cb=<unique>"   # the privileged page → deception
#   the anonymous request returns the privileged page (a 200 + the
#   content, not a 302) AND a HIT → confirmed
```

## 6. The injected-content confirm — the stored payload

```bash
curl "$BASE/page?cb=<unique>" -H 'User-Agent: <payload>'   # stores it
curl "$BASE/page?cb=<unique>" | grep '<payload>'   # the stored copy carries it
#   a clean request's copy carries YOUR payload → the poisoning confirm
```

## 7. The MISS-reflection edge — a reflection, not a store

```text
a marker reflected on a MISS → the response came from the origin —
a REFLECTION, not a poisoning — the stored copy didn't serve it.
```

## 8. The keyed-input edge — a per-input entry

```text
a keyed input → a per-input entry → YOUR input's effect is in YOUR
copy only → the clean request doesn't reflect → a different class.
```

## 9. The cachebuster edge — the same key

```text
the stored copy is keyed per-cachebuster — a clean request for the
same key reflects; a different key doesn't — the clean request MUST
use the same cachebuster key.
```

## 10. The falsifier — when the surface is dead

```text
every candidate input IS keyed → no unkeyed input → a different class.
no front-end cache → no stored response → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
a reflected marker on a MISS → a reflection, not a poisoning → a
different class.
```
