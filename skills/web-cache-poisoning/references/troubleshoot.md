# Troubleshoot — when the cache-poisoning doesn't work

Each symptom, its cause, and the fix.

---

## 1. The marker doesn't persist — a MISS, not a poisoning

```text
cause: the marker reflected on a MISS — the response came from the
origin, not the cache.
fix: check the cache-status — a HIT or an Age header proves the
stored copy served it — a MISS is a reflection.
```

## 2. The input is keyed — a keyed input isn't poisonable

```text
cause: the input IS part of the cache key — the stored copy is
keyed per-input — the stored response serves YOUR input only to
YOUR requests.
fix: the unkeyed-input check — a keyed input's marker doesn't reach
a different requester — a different class.
```

## 3. No cache — no stored-response surface

```text
cause: no front-end cache — no stored copy to poison.
fix: grep for the cache config — proxy_cache, vcl_hash, cache_page,
flask_caching — a cache may exist without a status header.
```

## 4. The Vary keys the input — a keyed header

```text
cause: a Vary: Cookie header keys the entry on the cookie — a per-
session copy — YOUR input's effect is in YOUR copy only.
fix: check the Vary header — a Vary'd header is keyed; an unkeyed
one isn't.
```

## 5. The anonymous request 302s — a redirect to login

```text
cause: an anonymous request that 302s to /login isn't a deception —
the cache didn't serve the privileged page.
fix: the anonymous request must return the privileged page (a 200
with the content) — a 302 is the safe behavior.
```

## 6. The path-normalization doesn't route — a routing bug

```text
cause: a path the app routes differently without a cache is a
routing bug, not a cache-poisoning.
fix: a stored copy must serve the confusion to a different requester
— a routing bug alone isn't a deception.
```

## 7. The TTL expired — a short-lived deception

```text
cause: the stored entry's TTL expired — the deception's window
closed.
fix: measure the TTL — the deception persists for the TTL — a
short TTL needs a fast attack.
```

## 8. The cache-buster defeated it — a keyed param

```text
cause: a keyed param the app ignores keys the entry per-value — the
stored response is YOUR requests only.
fix: a cache-buster defeats the poisoning — a keyed param isn't
poisonable.
```

## 9. The marker doesn't reach the clean request — a keyed input

```text
cause: the marker doesn't reflect in the clean request's response —
the input IS keyed.
fix: the unkeyed-input check — a keyed input's marker doesn't reach
a different requester.
```

## 10. The blast-radius — a shared-store write

```text
cause: a poisoned entry is served to EVERY requester of the URL —
a public URL poisons every visitor.
fix: use a harmless marker; keep the time-window short; clean up.
```

## 11. The authenticated page isn't stored — a no-store directive

```text
cause: the app sends a Cache-Control: no-store or private — the
authenticated page isn't cached.
fix: check the response's Cache-Control — a no-store/private page
isn't cached — a different class.
```

## 12. The host-header is keyed — a keyed host

```text
cause: the cache keys on the Host — a per-host entry — YOUR host's
effect is in YOUR copy only.
fix: check the key — a keyed host isn't poisonable; an unkeyed
X-Forwarded-Host may be.
```

## 13. The scheme-header is keyed — a keyed scheme

```text
cause: the cache keys on the scheme — a per-scheme entry.
fix: check the key — a keyed scheme isn't poisonable.
```

## 14. The deception needs a bot — a privileged-viewer case

```text
cause: the deception stores YOUR content but no privileged bot
views the stored copy — the poisoned page needs a victim viewer.
fix: a bot that requests the poisoned URL — the stored copy reaches
the privileged context.
```

## 15. The input isn't reflected — a non-reflected input

```text
cause: the app doesn't reflect the unkeyed input — the stored copy
doesn't carry it.
fix: the unkeyed input must be REFLECTED (or otherwise affect the
response) — a non-reflected input doesn't poison the copy.
```
