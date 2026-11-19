# Common mistakes — the ways cache-poisoning analysis goes wrong

Each a real failure mode — what it looks like, why it fails, the fix.

---

## 1. The "reflected marker" misread — a MISS is not a poisoning

```text
a marker reflected on a MISS — the response came from the origin,
not the cache — a REFLECTION, not a poisoning. the whole class
requires the STORED copy to serve YOUR input to a different
requester.
```

```text
fix: check the cache-status — a HIT or an Age header proves the
stored copy served it — a MISS is a reflection.
```

## 2. The keyed-input misread — a keyed input isn't poisonable

```text
an input that IS part of the cache key — the stored copy is keyed
per-input — the stored response serves YOUR input only to YOUR
requests — a cache-buster defeats the poisoning.
```

```text
fix: the unkeyed-input check — send the input → check the stored
copy serves it to a CLEAN request — a keyed input's marker doesn't
reach a different requester.
```

## 3. The "no cache-status" misread — a cache may still exist

```text
no cache-status header doesn't mean no cache — the cache may not
add a status header — check the source/config for the cache layer.
```

```text
fix: grep for the cache config — proxy_cache, vcl_hash, cache_page,
flask_caching — a cache may exist without a status header.
```

## 4. The "the marker stored" over-claim — a stored marker isn't the whole

```text
a marker stored in the cache isn't the whole confirm — the stored
copy must SERVE it to a DIFFERENT requester — the marker must reach
a clean request's response.
```

```text
fix: the clean-request read — a different session's request of the
same URL must reflect the marker.
```

## 5. The Vary misread — a keyed header isn't poisonable

```text
a Vary: Cookie header keys the entry on the cookie — a per-session
copy — YOUR input's effect is in YOUR copy only — not a shared
poisoning.
```

```text
fix: check the Vary header — a Vary'd header is keyed; an unkeyed
one isn't.
```

## 6. The authenticated-page-served-anonymously misread — a 302 is a redirect

```text
an anonymous request that 302s to /login isn't a deception — the
cache didn't serve the privileged page — a redirect to login is the
safe behavior.
```

```text
fix: the anonymous request must return the privileged page (a 200
with the content) — a 302 to login is the falsifier.
```

## 7. The path-normalization misread — a route confusion isn't a cache

```text
a path the app routes differently without a cache is a routing bug,
not a cache-poisoning — the stored-copy requirement still holds.
```

```text
fix: a stored copy must serve the confusion to a different requester
— a routing bug alone isn't a cache deception.
```

## 8. The blast-radius misread — a shared-store write

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — a public URL poisons every visitor — a real blast radius.
```

```text
fix: use a harmless marker; keep the time-window short; clean up —
a destructive payload on a shared store is a real harm.
```

## 9. The TTL misread — a persistent deception

```text
a stored entry lives until its TTL — a long-TTL deception persists —
the blast radius lasts.
```

```text
fix: measure the TTL — the deception's persistence bounds the
attack's window.
```

## 10. The "the header reflected" over-claim — a reflection isn't a store

```text
a header reflected in the immediate response is a REFLECTION — a
stored copy that serves it to others is a POISONING.
```

```text
fix: the clean-request read — the marker must reach a different
session's response.
```

## 11. The "the app reads the header" misread — the key is what matters

```text
the app reading the header doesn't matter if the cache KEYS on it —
the key is the vulnerability, not the app's read.
```

```text
fix: the unkeyed-input check — the cache key, not the app's read,
is the poisoning vector.
```

## 12. The "the cache stored the page" misread — a store isn't a deception

```text
a stored page that serves correctly to each requester isn't a
deception — the stored copy must serve the WRONG context — a
privileged page to an anonymous requester, a personalized page to a
public requester.
```

```text
fix: the deception is the WRONG context — a stored copy that serves
correctly isn't a vulnerability.
```

## 13. The "the URL is cached" misread — a cache-key confusion

```text
a URL that's cached isn't poisonable just because it's cached — the
poisoning requires an unkeyed input — the URL alone doesn't carry
the deception.
```

```text
fix: find the unkeyed input — the URL is the key; the input is the
vector.
```

## 14. The "the response differed" misread — a personalization isn't a deception

```text
a response that differs per-requester is a personalization — a
stored copy that serves the WRONG personalization to a different
requester is a deception.
```

```text
fix: the deception is the stored copy serving the wrong context —
a correct personalization isn't a vulnerability.
```

## 15. The "the cache is the bug" misread — the key-mismatch is

```text
the cache isn't the bug — the key-mismatch is — the app reads what
the cache ignores — a correct cache with a wrong key is the
vulnerability.
```

```text
fix: the unkeyed-input surface is the finding — a correctly-keyed
cache isn't a vulnerability.
```
