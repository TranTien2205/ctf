# Stored content — the deception's stored copy, exhaustively

The stored response's content — what the cache keeps and what it serves.

---

## 1. The stored response — the cached copy

```text
a cache stores a response per-key — the stored copy is the origin's
response at the time it was cached — every requester of the same key
gets the same stored copy — the shared copy is the vulnerability.
```

## 2. The stored content — what the copy carries

```text
the stored copy carries the origin's response:
- the body (the HTML, the JSON, the bytes)
- the headers (the Content-Type, the Set-Cookie, the cacheable signals)
- the status (the 200, the 302, the 404)
every requester gets the same stored content.
```

## 3. The stored personalized content — the per-user leak

```text
a personalized page cached under a shared URL — the stored copy
carries YOUR session's content — every requester's copy has YOUR
personalized data — a session-data leak.
```

## 4. The stored privileged content — the deception

```text
an authenticated page cached under a shared URL — the stored copy
carries the privileged content — an anonymous requester's copy has
the privileged page — a privileged-content deception.
```

## 5. The stored injected content — the payload

```text
an unkeyed reflected input carries a payload — a JS, a redirect, a
host-rewrite — the stored copy carries YOUR injected content — every
requester's copy serves it — a stored-XSS-like effect.
```

## 6. The stored URL-rewrite — the host-rewrite content

```text
an unkeyed X-Forwarded-Host — the app's absolute URLs use YOUR host —
the stored copy's links/scripts point to YOUR domain — every
requester's copy has the rewritten URLs.
```

## 7. The stored charset content — the charset injection

```text
an unkeyed reflected charset — an injected charset XSS stored in the
page — the stored copy carries the charset-decoded payload — every
requester's page has the XSS.
```

## 8. The stored scheme content — the downgrade

```text
an unkeyed X-Forwarded-Scheme — the app's absolute URLs use YOUR
scheme — the stored copy's links point to http — every requester's
copy has the downgraded URLs.
```

## 9. The stored per-UA content — a UA-dependent response

```text
an unkeyed User-Agent — the app personalizes on the UA — the stored
copy carries YOUR UA's response — every requester's copy has the
per-UA content.
```

## 10. The stored per-language content — a localized response

```text
an unkeyed Accept-Language — the app localizes on it — the stored
copy carries YOUR language's response — every requester's copy has
the localized content.
```

## 11. The stored per-cookie content — a cookie-dependent response

```text
an unkeyed cookie — the app personalizes on it — the stored copy
carries the per-cookie response — every requester's copy has it.
```

## 12. The stored-content confirm — the stored copy's content

```bash
# the stored copy's content — the poisoned page's links/content
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
curl "$BASE/page?cb=<unique>" | grep 'attacker.com'   # the stored copy carries it
```

## 13. The stored-content falsifier — a keyed input

```text
a keyed input → a per-input entry → YOUR content is in YOUR copy only
→ a different class.
```

## 14. The stored-content falsifier — a MISS reflection

```text
a marker reflected on a MISS → the response came from the origin —
a REFLECTION, not a poisoning — the stored copy didn't serve it.
```
