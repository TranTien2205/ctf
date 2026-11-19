# Negative map — every dead surface, mapped

The map from the dead surface to the falsifier and the next move.

---

## 1. The keyed-input dead surface — a per-input entry

```text
an input that IS part of the cache key — the stored copy is keyed
per-input — YOUR input's effect is in YOUR copy only — a keyed input
isn't poisonable.
next: a different unkeyed input — sweep the dictionary.
```

## 2. The MISS-reflection dead surface — a reflection, not a store

```text
a marker reflected on a MISS — the response came from the origin —
a REFLECTION, not a poisoning — the stored copy didn't serve it.
next: the second identical request — a HIT confirms the stored copy.
```

## 3. The no-cache dead surface — no stored response

```text
no front-end cache — no stored copy to poison — a different class.
a Cache-Control: no-store/private — the page isn't cached.
next: a different class — a reflection, a parser-differential.
```

## 4. The Vary-header dead surface — a keyed header

```text
a Vary: X-Custom — the cache keys on the header — a per-input entry.
next: a different unkeyed input — a header not in Vary.
```

## 5. The keyed-param dead surface — a cache-buster

```text
a keyed param the app ignores keys the entry per-value — the stored
response is YOUR requests only.
next: a different unkeyed input, or a param the cache strips.
```

## 6. The 302 dead surface — a redirect to login

```text
an anonymous request that 302s to /login — the cache didn't serve
the privileged page — the auth state WAS in the key.
next: a different privileged URL, or a personalized page.
```

## 7. The non-reflected-input dead surface — the app doesn't echo it

```text
the app doesn't reflect the unkeyed input — the stored copy doesn't
carry it.
next: a different reflected input, or a URL-rewrite (the links carry
the host, not the input's echo).
```

## 8. The keyed-host dead surface — a per-host entry

```text
the Host is in the key — a per-host entry — YOUR host's effect is in
YOUR copy only.
next: a different unkeyed input — an X-Forwarded-Host the cache ignores.
```

## 9. The keyed-cookie dead surface — a per-session entry

```text
a Vary: Cookie — the cache keys on the cookie — a per-session entry.
next: a different unkeyed input — a cookie not in Vary.
```

## 10. The keyed-scheme dead surface — a per-scheme entry

```text
the scheme is in the key — a per-scheme entry — a http/https copy
isn't shared.
next: a different unkeyed input — an X-Forwarded-Scheme the cache ignores.
```

## 11. The bot-viewer dead surface — no privileged render

```text
a poisoned copy + no bot visits → the delivery needs a victim — a
wrong-context case.
next: confirm the bot's surface (a report/visit endpoint).
```

## 12. The TTL dead surface — a short-lived deception

```text
the stored entry's TTL expired — the deception's window closed.
next: re-poison + a quick confirm, or a longer-TTL URL.
```

## 13. The path-normalization dead surface — the cache and app agree

```text
a path the cache and the app normalize the same way — no route
confusion.
next: a different normalization boundary (an encoded path, a case
difference).
```

## 14. The dead-surface map — every dead end, mapped

```text
a keyed input           → a per-input entry → a different unkeyed input
a MISS reflection       → a reflection → a HIT-confirm probe
no cache                → no stored copy → a different class
a no-store page         → a non-cached page → a different class
a Vary'd header         → a keyed header → a different unkeyed input
a keyed param           → a cache-buster → a different unkeyed input
a 302 to login          → a keyed auth → a different privileged URL
a non-reflected input   → a dead surface → a different reflected input
a keyed host            → a per-host entry → a different unkeyed input
a keyed cookie          → a per-session entry → a different unkeyed cookie
a keyed scheme          → a per-scheme entry → a different unkeyed input
no bot                  → no privileged render → confirm the bot's surface
an expired TTL          → a short-lived deception → re-poison + quick confirm
a same-normalization    → no confusion → a different boundary
```
