# Input deep — the unkeyed-input mechanics, exhaustively

Every way an input becomes an unkeyed poisoning vector.

---

## 1. The unkeyed input — the poisoning vector

```text
the vulnerability's precondition: a request part the app READS
(reflects, redirects on, personalizes on) but the cache key IGNORES.
the stored copy carries the unkeyed input's effect — every requester's
copy serves it.
```

## 2. The header input — an unkeyed header

```text
an unkeyed header — the app reads it, the cache ignores it — the
stored copy carries the header's effect — a reflected-header surface.
```

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # stores it
curl "$BASE/page?cb=<unique>"   # <marker> reflected? → unkeyed → poisonable
```

## 3. The param input — an unkeyed param

```text
an unkeyed param — the app reads it, the cache ignores it — the
stored copy carries the param's effect — a stripped-param surface.
```

## 4. The cookie input — an unkeyed cookie

```text
an unkeyed cookie — the app reads it, the cache ignores it — the
stored copy carries the cookie's effect — a per-cookie surface.
```

## 5. The path input — a normalization boundary

```text
a path the cache and the app normalize differently — the stored copy's
URL is the victim's URL, the response is YOUR request's — a route-
confusion surface.
```

## 6. The auth input — the deception surface

```text
the auth state — the cache keys on the URL, not the auth — the stored
copy is the privileged page — a deception surface.
```

## 7. The input's effect — what the app does with it

```text
the app reads the input and produces an effect:
- a reflection (the input echoed in the response)
- a URL-rewrite (the app's links use the input's value)
- a personalization (the app's content varies on the input)
- a redirect (the app redirects on the input)
- a decode (the app decodes the input's charset)
every effect the stored copy carries is the poisoning.
```

## 8. The input's keyedness — the unkeyed check

```bash
# send the input → check the stored copy serves it to a clean request
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   reflected → unkeyed → poisonable; NOT reflected → keyed → a different class
```

## 9. The input's falsifier — a keyed input

```text
a keyed input → a per-input entry → YOUR input's effect is in YOUR
copy only → the clean request doesn't reflect → a different class.
```

## 10. The input's falsifier — a MISS reflection

```text
a marker reflected on a MISS → the response came from the origin —
a REFLECTION, not a poisoning — the stored copy didn't serve it.
```

## 11. The input's falsifier — a no-cache surface

```text
no front-end cache → no stored copy → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
```

## 12. The input's dictionary — the unkeyed-input corpus

```text
headers:  X-Forwarded-Host, X-Original-URL, X-Rewrite-URL, X-Forwarded-Scheme,
          X-Forwarded-Proto, X-Host, X-Forwarded-Server, User-Agent, Referer,
          Accept-Language, Accept-Charset, Accept-Encoding, X-Real-IP,
          X-HTTP-Method-Override, X-Forwarded-Port, X-Forwarded-Uri, Origin,
          X-Requested-With, Forwarded, X-Forwarded-Domain, X-Forwarded-Ssl
params:   a stripped param (a utm, a fbclid, a custom param the cache drops)
cookies:  an unkeyed cookie (a theme, a lang, a custom cookie)
paths:    a normalization boundary (/static/../admin, /%2e%2e/admin, /Page)
auth:     the auth state (a session cookie, an auth header)
```
