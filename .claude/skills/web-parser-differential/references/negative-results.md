# Negative results — recording a dead parser-differential surface

What a failed probe actually proves, and how to record it.

---

## 1. The non-header-check negative — a trust check that reads a different input

```text
the trust check doesn't read the proxy header — a session, a token,
a signature — the header isn't the check's input → a different class.
record it: 'the trust check reads <different-input> — the header
isn't the check's input — a different class'.
```

## 2. The keyed-header negative — a proxy that strips a client header

```text
a proxy that strips a client-supplied proxy header → the client-
supplied header doesn't reach the app → the client-supplied bypass
fails.
record it: 'the proxy strips the client-supplied <header> — the
client-supplied bypass fails — the hop-by-hop bypass is the vector'.
```

## 3. The verified-header negative — a proxy that verifies

```text
a proxy that verifies the header it added → a client-supplied header
is rejected → the client-supplied bypass fails.
record it: 'the proxy verifies the header — the client-supplied
bypass fails — the hop-by-hop bypass is the vector'.
```

## 4. The no-strip negative — a proxy that doesn't strip

```text
a proxy that doesn't honor Connection's strip → the header passes
through → the app's check reads it → the hop-by-hop bypass fails.
record it: 'the proxy doesn't strip <header> — the hop-by-hop bypass
fails — a different class'.
```

## 5. The no-fallback negative — no missing-header fallback

```text
an app that requires the proxy header → a missing header → a 400/401
→ no missing-header fallback → the hop-by-hop bypass fails.
record it: 'no missing-header fallback — a missing header is a 400/401
— the hop-by-hop bypass fails — a different class'.
```

## 6. The no-proxy negative — no front-end in the path

```text
no reverse proxy in the path → no proxy header to abuse → a different
class.
record it: 'no proxy in the path — no proxy-header surface — a
different class'.
```

## 7. The reflection negative — a client-supplied header that isn't trusted

```text
a client-supplied header reflected but not trusted — the app echoes
it but doesn't use it for the trust check → a reflection, not a
trust bypass.
record it: 'the <header> is reflected but not trusted — a reflection,
not a trust bypass'.
```

## 8. The reach negative — a bypass without reach

```text
a differential that doesn't reach a gated route → a wrong-context
case → the bypass's reach is the gated route.
record it: 'no gated route reachable — the bypass's reach is empty —
a different class'.
```

## 9. The cache-confusion negative — a stored copy, not a parse

```text
a stored copy that serves YOUR input → a cache-poisoning (a store),
not a parser-differential (a parse).
record it: 'a stored copy, not a parse — a cache-poisoning'.
```

## 10. The smuggling-confusion negative — a desync, not a parse

```text
a desync front-end/back-end → a request-smuggling (a desync), not a
parser-differential (a parse).
record it: 'a desync, not a parse — a request-smuggling'.
```

## 11. The falsifier check — the dead surface

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
record it: 'the trust check doesn't depend on <header> — a different
class'.
```

## 12. The dead-surface map — every dead end, mapped

```text
a non-header check        → a different class
a keyed header            → the hop-by-hop bypass is the vector
a verified header         → the hop-by-hop bypass is the vector
a proxy that doesn't strip→ a different class
no fallback               → a different class
no proxy                  → a different class
a reflection              → a reflection, not a trust bypass
no reach                  → a wrong-context case → a different class
a stored copy             → a cache-poisoning
a desync                  → a request-smuggling
```
