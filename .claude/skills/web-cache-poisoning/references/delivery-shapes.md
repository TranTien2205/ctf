# Delivery shapes — how the poisoned response reaches a victim

The delivery — the stored copy's serve to a different requester.

---

## 1. The stored copy's serve — the deception's mechanism

```text
a stored response is served to EVERY requester of the URL until it
expires — the deception delivers the poisoned content to any
requester — no delivery step needed — the cache IS the delivery.
```

## 2. The shared-URL delivery — the public serve

```text
a public URL (a real page) — a poisoned copy reaches every visitor —
the deception's delivery is automatic — the URL's requester base IS
the victim set.
```

```bash
# the poisoned copy's serve — any requester's fetch
curl "$BASE/page?cb=<unique>"   # a different requester — the stored copy serves it
```

## 3. The bot-viewer delivery — the privileged context

```text
the deception's goal is often a privileged bot/viewer — a stored
poisoned page the bot requests — the stored copy serves YOUR injected
content to the privileged context.
```

```bash
# a bot requests the poisoned URL — the stored copy serves YOUR content
# the bot's context is privileged — the injected content runs there
```

## 4. The authenticated-page delivery — the verified card's shape

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'  # stores the privileged copy
# an anonymous GET — the stored copy serves it to a different context
curl "$BASE/settings.html?cb=<unique>"   # anonymous — the privileged page delivered
```

```text
the delivery: the stored copy serves the privileged content to a
requester who isn't privileged — the auth state wasn't in the key.
```

## 5. The injected-content delivery — the stored XSS

```text
an unkeyed reflected input carries a payload — a JS, a redirect, a
host-rewrite — the stored copy serves it to every requester — a
stored-XSS-like delivery through the cache.
```

```bash
# a reflected payload — stored in the cached page
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <payload>'
# the stored copy's links/scripts carry YOUR payload — every requester gets it
```

## 6. The per-shape delivery-map — which shape for which surface

```text
a public URL + a poisoned copy       → every visitor (a broad delivery)
a cachebuster URL + a poisoned copy  → only your key's requests (a confined delivery)
a privileged page + a shared cache   → the privileged content to the anonymous (a deception)
a reflected payload + a stored copy  → the injected content to every requester
```

## 7. The delivery's window — the TTL's reach

```text
a short TTL → a short delivery window → the deception expires before
the bot views it.
a long TTL → a persistent delivery → the poisoned page stays.
a measured TTL → the window for the bot/viewer's visit.
```

## 8. The delivery's confirm — the wrong-context serve

```bash
# a clean request — a different session, the same URL
curl "$BASE/page?cb=<unique>"   # <marker> reflected? → the stored copy serves it
```

```text
the delivery's confirm is the WRONG-context serve — the poisoned
content in a different requester's response — not just a stored copy.
```

## 9. The delivery's falsifier — a keyed input

```text
a keyed input → a per-input entry → YOUR copy, not a shared one →
no shared delivery → a different class.
```

## 10. The delivery's edge — a bot that doesn't visit

```text
a poisoned copy + no bot visits → the delivery needs a victim —
a wrong-context case. the stored copy only delivers to a requester —
a URL no one fetches delivers nothing.
```

## 11. The delivery's blast — the requester base

```text
a public URL → every visitor (a broad blast).
a rare URL → only your key's requests (a confined blast).
a privileged URL → the privileged page's requester base (a deception).
```

## 12. The delivery's interplay — a stored payload's effect

```text
an unkeyed reflected header carries a payload — a JS, a redirect —
the stored copy serves it to every requester — the delivery IS the
deception — a stored-XSS-like effect through the cache.
```
