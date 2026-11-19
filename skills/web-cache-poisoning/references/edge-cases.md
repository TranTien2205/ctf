# Edge cases — the cache-poisoning corners that break a first probe

The boundaries where a naive probe misses the surface.

---

## 1. The keyed-input edge — a per-input entry

```text
an input that IS part of the cache key — the stored copy is keyed
per-input — YOUR input's effect is in YOUR copy only — a keyed input
isn't poisonable.
```

## 2. The MISS-reflection edge — a reflection, not a store

```text
a marker reflected on a MISS — the response came from the origin —
a REFLECTION, not a poisoning — the stored copy didn't serve it.
```

## 3. The Vary-header edge — a keyed header

```text
a Vary: X-Custom — the cache keys on the header — a per-input entry —
a Vary'd header is keyed.
```

## 4. The keyed-param edge — a cache-buster

```text
a keyed param the app ignores keys the entry per-value — the stored
response is YOUR requests only — a cache-buster defeats the poisoning.
```

## 5. The no-cache edge — no stored-response surface

```text
no front-end cache — no stored copy to poison — a different class.
a Cache-Control: no-store/private — the page isn't cached.
```

## 6. The non-reflected-input edge — the app doesn't echo it

```text
the app doesn't reflect the unkeyed input — the stored copy doesn't
carry it — a non-reflected input is a dead surface.
```

## 7. The bot-viewer edge — no privileged render

```text
a poisoned copy + no bot visits → the delivery needs a victim — a
wrong-context case. a URL no one fetches delivers nothing.
```

## 8. The TTL edge — a short-lived deception

```text
the stored entry's TTL expired — the deception's window closed — a
short-lived deception needs a quick confirm.
```

## 9. The cachebuster edge — the wrong key

```text
the stored copy is keyed per-cachebuster — a clean request for the
same key reflects; a different key doesn't — the clean request MUST
use the same cachebuster key.
```

## 10. The path-normalization edge — a case-sensitive key

```text
a path the cache stores case-sensitively but the app routes case-
insensitively — a case-normalization boundary — a /Page vs /page
confusion.
```

## 11. The method edge — a per-method entry

```text
a GET vs POST keyed separately — a per-method entry — a GET's stored
copy serves GETs only.
```

## 12. The keyed-host edge — a per-host entry

```text
the Host is in the key — a per-host entry — YOUR host's effect is in
YOUR copy only.
```

## 13. The keyed-cookie edge — a per-session entry

```text
a Vary: Cookie — the cache keys on the cookie — a per-session entry —
a session-cookie copy isn't shared.
```

## 14. The keyed-scheme edge — a per-scheme entry

```text
the scheme is in the key — a per-scheme entry — a http/https copy
isn't shared.
```

## 15. The stale-copy edge — a stale serve

```text
a stale copy — the TTL passed but the proxy served the old copy —
the deception persists past the TTL — a stale-while-revalidate.
```

## 16. The 404-cached edge — a cached error

```text
a cached 404 — the proxy caches errors too — a stored 404 served to
every requester — a different deception surface.
```

## 17. The keyed-method edge — a per-method copy

```text
a POST cached separately — a per-method copy — a POST's stored copy
serves POSTs only.
```

## 18. The falsifier — when the surface is dead

```text
every candidate input IS keyed → no unkeyed input → a different class.
no front-end cache → no stored response → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
a reflected marker on a MISS → a reflection, not a poisoning → a
different class.
```
