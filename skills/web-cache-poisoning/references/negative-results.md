# Negative results — recording a dead cache surface

What a failed cache-poisoning actually proves, and how to record it.

---

## 1. The keyed-input negative — a keyed input isn't poisonable

```text
an input that IS part of the cache key — the stored copy is keyed
per-input — the stored response serves YOUR input only to YOUR
requests.
record it: 'the <input> IS keyed — a per-input entry — not a shared
poisoning'.
```

## 2. The MISS negative — a reflection, not a poisoning

```text
a marker reflected on a MISS — the response came from the origin,
not the cache — a REFLECTION, not a poisoning.
record it: 'the <input> reflects on a MISS — a reflection, not a
stored-copy serve — the cache didn't store it'.
```

## 3. The no-cache negative — no stored-response surface

```text
no front-end cache — no stored copy to poison.
record it: 'no cache layer — no stored-response surface — a
different class'.
```

## 4. The no-store negative — a non-cacheable page

```text
a Cache-Control: no-store or private — the page isn't cached.
record it: 'the page sends Cache-Control: no-store — it isn't
cached — a different class'.
```

## 5. The Vary-keyed negative — a keyed header

```text
a Vary: Cookie header keys the entry on the cookie — a per-session
copy — YOUR input's effect is in YOUR copy only.
record it: 'the Vary: Cookie keys the input — a per-session entry —
not a shared poisoning'.
```

## 6. The 302 negative — a redirect to login

```text
an anonymous request that 302s to /login isn't a deception — the
cache didn't serve the privileged page.
record it: 'the anonymous request 302s to /login — the cache didn't
serve the privileged page — the falsifier is met'.
```

## 7. The keyed-host negative — a per-host entry

```text
the cache keys on the Host — a per-host entry — YOUR host's effect
is in YOUR copy only.
record it: 'the Host is keyed — a per-host entry — not a shared
poisoning'.
```

## 8. The cache-buster negative — a keyed param

```text
a keyed param the app ignores keys the entry per-value — the stored
response is YOUR requests only.
record it: 'a keyed param exists — a cache-buster — the stored copy
is keyed per-value — not poisonable'.
```

## 9. The non-reflected-input negative — a non-reflected input

```text
the app doesn't reflect the unkeyed input — the stored copy doesn't
carry it.
record it: 'the <input> isn't reflected — the stored copy doesn't
carry it — a non-poisonable input'.
```

## 10. The no-bot negative — a privileged-viewer miss

```text
the deception stores YOUR content but no privileged bot views the
stored copy — the poisoned page needs a victim viewer.
record it: 'no bot requests the poisoned URL — the stored copy
doesn't reach a privileged context — a wrong-context case'.
```

## 11. The expired-TTL negative — a short-lived deception

```text
the stored entry's TTL expired — the deception's window closed.
record it: 'the TTL is <N>s — the deception persisted only for the
window — a short-lived case'.
```

## 12. The dead-surface negative — no unkeyed input at all

```text
every candidate input IS keyed → no unkeyed input → no poisoning
vector → a different class.
record it: 'every candidate input IS keyed — the cache keys
correctly — no unkeyed-input surface — a different class'.
```
