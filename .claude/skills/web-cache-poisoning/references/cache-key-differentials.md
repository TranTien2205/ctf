# Cache-key differentials

The cache keys a request one way; the application personalizes it another. Any
input that changes the response but is absent from the cache key is a
poisonable slot — and any input in the key that should not be there is an
oracle.

## Auth state not in the key (EncoDecept — confirmed)

```text
GET /settings.html?cb=1    # authenticated, twice -> cached
GET /settings.html?cb=1    # anonymous
```

Expected: the anonymous fetch returns the authenticated page — the key covered
path+query but not the session, so the personalized response crossed users.
Falsifier: the anonymous fetch is denied or generic; auth state is keyed.

## Cache-key header injection (OmniWatch)

A path segment carrying `%0d%0a` was decoded into the cache's storability
header; a *CacheKey* header on the next request then named the poisoned entry:

```text
GET /path%0d%0aHeader:%20marker/...   # injects into storability handling
GET /other-path                       # CacheKey: <named-header>
```

Expected: the injected header alters what gets stored or keyed — a response
written under one key is served for another. Falsifier: the encoded CR/LF is
rejected or inert in key construction.

## Duplicated keyed argument (Pod Diagnostics)

After cache validity elapses, request the route with the keyed argument given
**twice**, then again with only the first value:

```text
GET /route?k=v1&k=v2    # front end keys on one position
GET /route?k=v1         # app reads the other
```

Expected: the cache stored the response for `k=v1` that was actually computed
from `k=v2` — duplicated parameters split which layer read which position.
Falsifier: both forms agree on which value is read and keyed.

## The check list for any keyed slot

- List what the response depends on: auth, Accept, Accept-Language, cookies,
  query params, headers.
- Diff that against the key: whatever differs is the slot.
- Verify poisoning by reading the entry **back with the key only** — the
  poison must be retrievable without re-sending the payload.

## Falsifier

Every response-affecting input is in the key, or the cache bypasses on the
route entirely. `Age`/`X-Cache` headers tell you whether entries exist at all;
no caching means no class.
