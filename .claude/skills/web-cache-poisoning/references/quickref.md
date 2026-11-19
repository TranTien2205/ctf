# Quickref — the cache-poisoning one-page reference

The whole class in one page — the cache, the key, the unkeyed input.

---

## The model — a stored response per-key

```text
a cache stores a response per-key — every requester of the same key
gets the same stored copy — the shared copy is the vulnerability.
the unkeyed input — a request part the app reads but the cache ignores
— the stored copy carries its effect to every requester.
```

## The probe — send-then-clean-request

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # <marker> reflected? → unkeyed → poisoned
```

## The confirm — the three-part evidence

```text
1. the probe request STORED — a cache HIT on the second identical request
2. the keyed input left OUT of the cache key — the unkeyed input
3. the reflected value reaching a response the victim receives — the
   clean request reflects the marker
a reflected marker on a MISS is not a poisoning.
```

## The deception — the authenticated-page-served-anonymously

```bash
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # stores the privileged copy
curl "$BASE/settings.html?cb=<unique>"   # the privileged page → deception
```

## The falsifier — when to move

```text
a keyed input → a per-input entry → a different class.
a MISS reflection → a reflection → a different class.
a no-store page → a non-cached page → a different class.
```
