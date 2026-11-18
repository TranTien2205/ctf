# CSRF token defenses — and every way they fail

A CSRF token is a session-bound secret the form must echo. The
class's real question isn't "is there a token" but "is it
VERIFIED against the session" — and a dozen partial checks aren't.

---

## 1. The token shapes

```text
synchronizer token   — server stores token in session; form echoes;
                       server compares echo to stored
double-submit cookie — server sets token in cookie AND in form;
                       request must echo both; server compares
                       cookie-value to form-value (no session store)
HMAC token           — token = HMAC(session-id|user, secret);
                       server re-derives and compares — stateless
encrypted token      — token = Encrypt(session-data); server decrypts
per-request token    — rotated each request; replay fails
```

Each has a distinct failure surface — the verification is the
question, not the presence.

## 2. The verification gaps — the corpus of what fails

```text
1. no verification at all
   token field present in the form, never checked server-side —
   send any value or omit it
2. token accepted from ANY session
   the server stores token-per-request but doesn't bind it to the
   session — YOUR session's token validates THEIR request
3. token replayable
   same token reused indefinitely — grab it once from your own
   session's page and replay it in the CSRF payload
4. token not session-bound
   the token is a global/static value or derived from public data —
   guessable, not secret
5. token field optional
   omitting the field skips the check entirely — send no token
6. empty token accepted
   "" or null or the literal string 'undefined'/'null' validates
7. token checked only on some methods
   POST checked, PUT/PATCH/DELETE not — or GET not
8. token checked only on some routes
   a sibling unguarded route does the same write
9. token compared with == on different types
   "0" == 0 coercion — send a coercible value
10. timing-unsafe compare leaks the token
    a char-by-char compare that exits early — oracle to recover
11. double-submit without binding
    cookie and form compared to each other but NOT to the session —
    set BOTH to a value you choose: cookie via a cookie-setting
    vector (a subdomain, a header-injection) + form value matching
12. token in the URL/referer leaks
    a GET-form's token rides the URL — Referer/referrer leaks it
    to a cross-origin page — then it's replayable
13. per-request token's PRIOR token still valid
    rotation doesn't invalidate the old — replay the previous
14. token derived from guessable material
    HMAC of a KNOWN value with a weak secret — brute the secret
15. token endpoint leaks it
    a /api/token or page-source read that returns the token to any
    caller — the attacker page fetches it (needs CORS or a
    JSONP/proxy to read cross-origin)
16. token only verified when PRESENT
    the check 'if token: verify' — absent skips — send none
17. cookie-name confusion in double-submit
    the comparison reads the WRONG cookie/field — a value mismatch
    the server never compares correctly
18. token verified but NOT the session it binds
    token X valid for session A also accepted for session B
19. token accepted cross-method
    a GET-param token validates a POST — or a body token validates
    a header check that reads the wrong source
20. JSON-vs-form confusion
    the token check reads form['csrf'] but the CSRF sends JSON —
    the check sees an absent field and skips
```

## 3. The double-submit-cookie attack — the most-CTF shape

```text
defense: cookie csrf=<T> + form field csrf=<T> — server compares
         cookie value to form value
attack:  set the cookie YOURSELF — then the form's value matches
         it trivially
carrier: a subdomain cookie-set, a header-injection cookie-set,
         a same-site lax cookie write, a cookie-bombing overflow,
         or the app sets the csrf cookie from a request param
<form action="https://target/change" method="POST">
  <input name="csrf" value="x">     ← matches the cookie you set
</form>
<!-- the cookie csrf=x set via <img src="https://sub.target/set-cookie?csrf=x">
     or a cookie-injection, or a subdomain you control -->
```

The double-submit check is `cookie == form`, not `token == session`
— control both sides and it validates.

## 4. The token-replay via your own session

```text
1. log in as yourself → GET the form → extract your CSRF token
2. the CSRF page embeds YOUR token
3. the victim's submission carries YOUR token + THEIR session cookie
4. if the token isn't session-bound — the server accepts it
```

The classic brokenness: the token validates globally, not per-
session. Test: grab your token, replay it in a request under a
DIFFERENT session — does it validate?

## 5. The token-in-URL leak

```html
<!-- the form GETs — the token rides the URL -->
<form action="https://target/search" method="GET">
  <input name="csrf" value="<victim-token>">
<!-- the response page's Referer to ANY external resource leaks it
     — or the attacker page reads location.href if same-origin -->
```

A GET-form token leaks via Referer to any external link on the
result page, via browser history, via a log. Then it's a known
value — replayable.

## 6. The `csrf_probe` token-arm

```bash
python3 tools/web/csrf_probe.py --url "$BASE/change" --method POST \
  --body 'name=x&csrf=T' --token-field csrf
# replays: 1. as-sent, 2. token-field stripped, 3. foreign-origin
# grade each: accepted-without-token = the candidate
```

`--token-field` names the field to strip — the stripped replay
accepted means the token isn't enforced.

## 7. The token-source audit — where it lives

```bash
# the token's carrier — how the page gets it
grep -rnoE 'csrf|_token|authenticity_token|__RequestVerificationToken|anticsrf|csrfmiddlewaretoken|nonce|xsrf|XSRF-TOKEN|X-CSRF|X-XSRF' \
  <src> --include='*.js' --include='*.py' --include='*.html' | head -40

# common carriers:
#   <input name="csrf" value="{{token}}">        — hidden field
#   <meta name="csrf-token" content="...">       — meta tag (JS reads)
#   X-CSRF-Token response header                  — JS reads
#   a cookie XSRF-TOKEN + Angular reads it        — cookie-based
#   /api/csrf-token endpoint                      — an API
```

The meta-tag/cookie/API carriers are the leakable ones — a page
that exposes the token to a fetch needs CORS to read it; a
JSONP/proxy/readable-endpoint leaks it without.

## 8. The token-source leak — reading it cross-origin

```text
the token is in a JSON endpoint     → CORS open = read it (different class)
the token is in a <meta> tag        → need same-origin read — XSS/proxy
the token is in a JSONP response    → JSONP leaks it cross-origin
the token is in a cookie            → JS can't read HttpOnly; a non-HttpOnly
                                       cookie is readable — but reading needs
                                       same-origin JS
the token is in the URL             → Referer/history leak
the token is a static/derivable     → guess it
the token is fetched by an iframe   → same-origin iframe read
```

A token you can't READ is the falsifier for CSRF — but check every
leak surface first: JSONP, a CORS-open endpoint, a subdomain read,
a proxy that returns it, a static value.

## 9. The framework-default token surfaces

| Framework | The token mechanism | The common hole |
|---|---|---|
| Django | `csrfmiddlewaretoken` — session-bound synchronizer | `CSRF_COOKIE_HTTPONLY` off → JS-read; `csrf_exempt` decorator |
| Rails | `authenticity_token` — meta-tag + field | `protect_from_forgery with: :null_session` on APIs — null_session SKIPS the check |
| Express `csurf` | `_csrf` — cookie+body double-submit | `csurf({ignoreMethods:['GET','HEAD']})` — GET writes unguarded; cookie not HttpOnly |
| Flask-WTF | `csrf_token` — session-bound | `WTF_CSRF_ENABLED=False` or an exempt blueprint |
| Spring | `_csrf` — synchronizer | `csrf().disable()` in security config |
| Laravel | `_token`/`X-XSRF-TOKEN` — session-bound | `$except` route list — a route exempted |
| ASP.NET | `__RequestVerificationToken` — cookie+field | `[IgnoreAntiforgeryToken]` attribute |
| Angular | `XSRF-TOKEN` cookie + `X-XSRF-TOKEN` header | the cookie isn't HttpOnly — a JS-read + header-set on the SAME page; cross-origin the page can't read it — but a subdomain XSS can |
| Gin/Go | no built-in — hand-rolled | whatever the app does |
| Tornado | `xsrf_cookies` — cookie+arg | `xsrf_cookies=False` or a `check_xsrf_cookie` bypass |

The Laravel `$except`/Rails `null_session`/Django `csrf_exempt`/
Express `ignoreMethods` are the "the developer exempted it" shapes —
grep for the exemption patterns.

## 10. The falsifier

```text
The token is session-bound, verified on every request and method,
required (absent fails), not replayable, and not readable cross-
origin. Every delivery fails — record refutes; the endpoint is not
CSRF-able.
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "token-def: double-submit cookie; set-both-sides bypass"
python3 tools/state.py <c> --hypothesis \
  "token-def: token not session-bound; replay own token"
```
