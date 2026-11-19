# Troubleshoot deep — why the poisoning probe returned nothing

The failure modes and the re-probe for each.

---

## 1. The keyed-input miss — the marker didn't reach a clean request

```text
the marker was in YOUR response but not a clean request's — the
input IS keyed — a per-input entry, not a shared one.
re-probe: a different unkeyed input — sweep the header/param/cookie
dictionary.
```

## 2. The MISS reflection — a reflection, not a store

```text
the marker reflected on a MISS — the response came from the origin —
a REFLECTION, not a poisoning — the cache didn't store it.
re-probe: the second identical request — a HIT confirms the stored copy.
```

## 3. The no-cache miss — no stored-response surface

```text
no cache-status header and no proxy cache — no stored copy to poison.
re-probe: check the config for a cache layer; a Cache-Control:
no-store/private means the page isn't cached.
```

## 4. The keyed-param miss — a cache-buster defeat

```text
a keyed param the app ignores keys the entry per-value — the stored
copy is YOUR requests only.
re-probe: a different unkeyed input, or a param the cache strips.
```

## 5. The Vary-header miss — a keyed header

```text
a Vary: X-Custom — the cache keys on the header — a per-input entry.
re-probe: a different unkeyed input — a header not in Vary.
```

## 6. The deception miss — a 302 to login

```text
an anonymous request that 302s to /login — the cache didn't serve
the privileged page — the auth state WAS in the key or the page
isn't cached.
re-probe: a different privileged URL, or a personalized page.
```

## 7. The non-reflected-input miss — the app doesn't echo it

```text
the app doesn't reflect the unkeyed input — the stored copy doesn't
carry it.
re-probe: a different reflected input, or a URL-rewrite (the links
carry the host, not the input's echo).
```

## 8. The bot-viewer miss — no privileged render

```text
the deception stores YOUR content but no privileged bot views it —
a wrong-context case.
re-probe: confirm the bot's surface (a report/visit endpoint) and
the bot's visit.
```

## 9. The TTL miss — a short-lived deception

```text
the stored entry's TTL expired — the deception's window closed.
re-probe: re-poison + a quick confirm, or a longer-TTL URL.
```

## 10. The cache-buster miss — the wrong key

```text
the stored copy is keyed per-cachebuster — a clean request for the
same key reflects; a different key doesn't.
re-probe: the clean request MUST use the same cachebuster key.
```

## 11. The path-normalization miss — the cache and app agree

```text
a path the cache and the app normalize the same way — no route
confusion.
re-probe: a different normalization boundary (an encoded path, a
case difference, a double-slash).
```

## 12. The keyed-input sweep — when nothing is unkeyed

```text
every candidate input IS keyed → no unkeyed input → no poisoning
vector → a different class.
re-probe: the classifier's other candidates — a parser-differential,
a request-smuggling, a different class.
```

## 13. The cache-status miss — a misleading status

```text
a HIT on a different-keyed URL → a stored copy, but keyed per-input →
a different class.
a HIT on the same URL but a keyed input → a per-input copy → a
different class.
re-probe: the cachebuster on the same key, and the unkeyed-input check.
```

## 14. The falsifier check — is the surface dead

```text
every candidate input IS keyed → no unkeyed input → a different class.
no front-end cache → no stored response → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
a reflected marker on a MISS → a reflection, not a poisoning → a
different class.
```
