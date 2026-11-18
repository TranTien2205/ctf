# Session token analysis — entropy, prediction, fixation

Opaque session ids, `sessionid`/`PHPSESSID`/`JSESSIONID`/`connect.sid` —
when the token is not a JWT, the attack surface is the *id itself*: its
entropy, its lifecycle, and who gets to choose it.

---

## 1. The id-format table

| Shape | Likely | Entropy clue |
|---|---|---|
| `JSESSIONID=ABCD1234...` | Java servlet | check for sequential suffix |
| `PHPSESSID=a1b2c3...` | PHP | `session.hash_function`, entropy bits in ini |
| `connect.sid=s%3A<jwt>.<sig>` | express-session | signed JWT or HMAC'd value |
| `sessionid=hex` | Django | `django.contrib.sessions` — random, but check `SESSION_ENGINE` |
| `rack.session=BAh7...` | Ruby/Rack | Marshal-serialized + HMAC — see web-deserialization |
| `laravel_session=eyJ...` | Laravel | encrypted (APP_KEY!) — web-deserialization if key leaks |
| `.AspNetCore.Session=...` | ASP.NET | encrypted data-protection |
| `auth_token=...` | custom | whatever the dev wrote — decode it |
| 24/32/40 hex | custom | `secrets.token_hex` or `md5(user+time)` — check |
| `uuid4` / `uuid1` | custom | uuid1 embeds MAC+timestamp — predictable |
| base64 of `user:timestamp` | homemade | forge trivially |
| base64 of JSON | homemade unsigned | forge trivially |
| increasing int | **game over** | `tools/web/id_sweep.py` |

## 2. The two-token diff (collect A and B)

```
A: session=aaaa...1   B: session=aaaa...2
A: sid=1699999999_x   B: sid=1699999984_x    # timestamp visible
A: t=VXNlcjox         B: t=VXNlcjoy         # b64("User:1") vs ("User:2")
```

Decode both halves as text, as b64, as hex-of-timestamp. If two tokens
differ only in a short suffix, the id is `timestamp + counter` — guessable
inside a small range. `id_sweep.py --url` walks a numeric id range.

## 3. Entropy tests

- **Length**: <64 bits → brute-forceable offline (<2^64), <80 bits
  borderline, 128 bits safe.
- **Alphabet**: hex only (16^N), b64 (64^N), digits only (10^N) — digits
  at length ≤10 is a phone-number range, not a secret.
- **Charset per position**: if chars 1-8 are always `[0-9a-f]` and 9+ are
  `x`, the secret is only the second part.
- **Time correlation**: mint two tokens 1s apart; if a prefix differs by
  a tiny delta, it's a timestamp.
- **PRNG**: PHP `mt_rand`/`rand` seeded by pid+time is recoverable —
  tools/crypto covers PRNG state recovery.

## 4. Session fixation

1. Attacker mints a session id by visiting the login page *without* logging
   in → `sid=EVIL`.
2. Attacker hands victim a link `https://target/?sid=EVIL` or plants the
   cookie via subdomain.
3. Victim logs in; the app **keeps `sid=EVIL`** and binds it to the
   victim's account.
4. Attacker replays `sid=EVIL` → is the victim.

**Confirm**: send your own unauthenticated cookie to the login endpoint,
log in as victim, replay your cookie — if it still maps to your chosen
value AND now returns the victim's session, fixation is confirmed.

**Falsifier**: the app issues a fresh id on login (the standard fix) —
the attacker's `EVIL` no longer resolves.

## 5. Session hijacking primitives

- Missing `Secure` + same-network HTTP → sniffed.
- Missing `HttpOnly` + XSS → stolen.
- `Domain` too broad → readable from sibling subdomain.
- Token in URL (`?sid=`) → `Referer`, logs, browser history.
- Token in `localStorage` → XSS-readable.
- IP/UA binding **absent** → replayed from anywhere.
- IP/UA binding **present** but forgeable via `X-Forwarded-For` →
  check if binding reads the spoofable header.

## 6. Lifecycle bugs

| Bug | Test |
|---|---|
| Logout doesn't invalidate | capture token, `POST /logout`, replay |
| "Log out everywhere" doesn't | same, with `logout_all` |
| Password change keeps old session | change pw, replay old token |
| `remember me` cookie never expires | check `Max-Age`, then forge |
| Concurrent-session limit absent | many logins, all still valid |
| Session survives `DELETE /user` | deleted account's token still works |
| Session id reused after logout | the SAME id string comes back |
| Long-lived session without rotation | no `sensitive`-op re-issue |

## 7. Cookie-vs-header decisions

`Authorization: Bearer` + `localStorage` → XSS-readable but CSRF-immune
(header isn't attached automatically). Cookie + `SameSite=None` →
CSRF-vulnerable. Cookie + `Lax` → only top-level GET CSRF.

A token in **both** cookie and `Authorization` — the app may prefer the
header; a fixated cookie won't help if the header wins.

## 8. Server-side store classes

- **In-memory dict** — dies on restart; fixation not checked if the dict
  is `sid→user` without login-time re-issue.
- **DB row** — `DELETE FROM sessions` actually kills it; look for the
  `ON DELETE`/`expiry` logic.
- **Signed blob** (Flask `session` cookie) — the whole session lives in
  the cookie; forge = sign with `SECRET_KEY`; see `jwt-deep.md`/deser.
- **Encrypted blob** (Laravel `APP_KEY`, ASP.NET data-protection) —
  leak the key → decrypt + re-encrypt; treat as deserialization surface.

## 9. `session_dissect.py` output — what to record

```bash
python3 tools/web/session_dissect.py --token "$T" --challenge "$C"
python3 tools/web/session_dissect.py --cookie 'session=...; other=...' --challenge "$C"
python3 tools/web/session_dissect.py --url "$BASE" -H 'Cookie: session=...' --challenge "$C"
```

It prints `format`, decoded claims (where free), `weakness` (the named
class), and the next `http_probe`/`jwt_forge` command. Record the
`weakness` line — it routes the rest of the work.
