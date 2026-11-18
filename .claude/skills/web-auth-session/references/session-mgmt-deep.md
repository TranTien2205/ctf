# Session management deep — lifecycle, stores, and the edge cases

`session-analysis.md` covers id entropy and formats; this file is the
*operational* depth — how stores differ, what the lifecycle rules really
are, and the edge cases that produce bugs.

---

## 1. The three session-store shapes

| Shape | Where data lives | What's in the cookie | Attack |
|---|---|---|---|
| **server-side id** | DB/Redis keyed by id | random lookup key only | guess id, fixate id, steal id |
| **signed blob** | the cookie itself | serialized session + HMAC | forge the blob (leak `SECRET_KEY`) |
| **encrypted blob** | the cookie itself | encrypted serialized session | leak key, decrypt, re-encrypt |

Flask `session`, `connect.sid` (signed), Laravel `laravel_session`
(encrypted), Django `sessionid` (server-side, unless
`SESSION_ENGINE='django.contrib.sessions.backends.signed_cookies'` — then
it's a signed blob), ASP.NET `.AspNetCore.Session` (data-protection
encrypted), Rails `_app_session` (encrypted Marshal or JSON).

## 2. The lifecycle rules — what SHOULD happen

| Event | Expected | Bug when absent |
|---|---|---|
| login | rotate id, bind to user | fixation |
| logout | invalidate + client-clear | replay-after-logout |
| password change | invalidate all sessions | old sessions survive |
| privilege change | rotate + re-bind | pre-escalation session persists |
| expiry | hard `Max-Age` + idle timeout | replay forever |
| concurrent login | optional limit or notify | session sprawl |
| "remember me" | separate longer-lived token, revocable | one token for everything |

## 3. The in-memory store trap

```python
sessions = {}
sid = request.cookies.get('sid') or secrets.token_hex(16)
if sid not in sessions:
    sessions[sid] = {}
sessions[sid]['user'] = user.id
resp.set_cookie('sid', sid)
```

The bug: `sid not in sessions` — the attacker picks the sid, the store
creates it, login binds it. Fixation is *structural*.

## 4. The DB-store trap

```sql
SELECT user_id FROM sessions WHERE sid = ? AND expires_at > now()
```

Bugs:

- `sid` is `md5(username)` or `md5(username + time)` — computable.
- `expires_at` never checked — replay forever.
- `DELETE FROM sessions WHERE sid = ?` missing on logout — replay.
- `user_id` not bound — the sid authenticates *anyone* whose sid you know.
- `UNIQUE(sid)` but the `INSERT` is `ON CONFLICT REPLACE` — fixate a
  sid by re-registering it.

## 5. The signed-blob trap (Flask/itsdangerous)

```
session = {"_user_id": "42", "_fresh": true, "csrf": "..."}
cookie = base64(session) . timestamp . HMAC-SHA1(body+ts, SECRET_KEY)
```

- Leak `SECRET_KEY` (`app.py`, `.env`, `config.py`, `git log`) →
  `flask-unsign --sign` or stdlib `itsdangerous` → `{"_user_id": "1"}`.
- `itsdangerous` accepts *multiple* algorithms — `sha1`/`sha256`/`sha512`
  — a downgrade isn't useful unless the verifier accepts one you can
  trick (rare; the digest matters).
- The session content is *readable* — `{"_user_id":"42"}` tells you the
  claim name to forge.

## 6. The encrypted-blob trap

Laravel `laravel_session`: `encrypt(json(session), APP_KEY)` — the key
in `.env` → decrypt, modify `user_id`, re-encrypt. `.env` is the most
common `APP_KEY` leak; also `config/app.php` `key` field.

ASP.NET `.AspNetCore.Session`: data-protection key ring in
`keys/` dir or in registry — usually not leakable without a file-read
primitive (`skills/file-read-primitives/SKILL.md` chain).

Rails `_app_session`: `secret_key_base` in `config/secrets.yml` or
`Rails.application.credentials` — Marshal or JSON inside.

## 7. The fixation deep-dive

Fixation variants by *carrier*:

- **`?sid=` URL parameter** — the app reads `sid` from the query string;
  attacker sends `https://target/?sid=EVIL`. Confirmed when the app
  `Set-Cookie: sid=EVIL` on the response AND binds it on login.
- **Subdomain cookie plant** — `attacker.example.com` sets
  `Domain=.example.com` — parent's cookie jar accepts it.
- **`Set-Cookie` injection** via a response you influence (CRLF, header
  injection) — `web-request-smuggling` surface.
- **localStorage**: `localStorage.setItem('token', 'EVIL')` via XSS or a
  sibling-frame write — then the SPA sends it as `Authorization`.

## 8. The hijack channels — ordered by reliability

| Channel | Requirements | Reliability |
|---|---|---|
| `Referer` leak | `?sid=` in URL + external resource | high in CTF |
| Missing `Secure` + network | attacker on same network / http link | medium |
| Missing `HttpOnly` + XSS | XSS in the app | high (if XSS exists) |
| `Domain` too broad | sibling subdomain XSS/takeover | medium |
| localStorage + XSS | XSS | high |
| `?sid=` in `Location` 302 to third party | redirect to attacker | high |
| log leak (`/logs` endpoint) | debug endpoint exposed | CTF-high |
| session in `Set-Cookie` on GET | Referer on external resources | medium |

## 9. The binding checks — and how to fool them

- **IP binding** reads `request.remote_addr` — spoofable via
  `X-Forwarded-For` IF the app trusts the header; test by replaying your
  own session with `X-Forwarded-For: <victim-ip>`.
- **UA binding** reads `User-Agent` — trivially spoofable; not a control.
- **Device fingerprint** (UA + accept headers hash) — you need the same
  browser profile; skip unless the app leaks it.
- **Cookie-channel binding** (session only valid on the Cookie path it
  was set on) — rare; test by replaying the id under a different path.

## 10. The "remember me" class

- `remember_me` = separate token, should be `selector:validator` —
  `selector` locates the row, `validator` is compared hashed. Bugs:
  `selector` predictable, `validator` in `Set-Cookie` plaintext, token
  not rotated per use.
- `remember_me` = `username + ":" + md5(username + secret)` — if
  `secret` leaks → forge any user's remember-me.
- `remember_me` sets a *second* cookie on the *same* domain — a weaker
  cookie becomes a parallel session.

## 11. The two-device test

```
device 1: login as A → sid_A → logout
device 2: login as A → sid_B
replay sid_A → ?
```

- sid_A still works → logout didn't invalidate (bug).
- sid_A returns 401 → fine.
- sid_A returns *B's* session → id reuse (very rare, very bad).

## 12. CTF shorthand

- `flask` + `session` cookie → look for `SECRET_KEY` in source first.
- `express-session` + `connect.sid` → the `secret` in `app.js`/`.env`.
- `django` + `sessionid` → check `SESSION_ENGINE`; if
  `signed_cookies` → `SECRET_KEY`; else look for `django_session` table
  access (file-read primitive).
- `laravel` + `laravel_session` → `APP_KEY` in `.env`.
- `rails` + `_session` → `secret_key_base` in `config/secrets.yml` /
  `credentials.yml.enc` (if `master.key` leaks too).
- `php` + `PHPSESSID` → the id is usually good; look at session
  *content* on disk via file-read (`/var/lib/php/sessions/sess_<id>`).
