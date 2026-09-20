# SSOS (HackTheBox) — verified 2026-09-15

Chain: OAuth2 SSO startup race — win the `student@edulearn.htb` registration
race, then swap the shared Puppeteer cookie jar to our session with a
text/plain JSON CSRF delivered through `/submit-url`.

## Evidence ancestry (live target this session)
- First instance `154.57.164.82:32495` was actually a Java login app
  (jsessionid) — unrelated; the edulearn challenge is host-routed on nginx.
- Stack fingerprint: `edulearn.htb` = Express/EJS/passport-oauth2 on
  127.0.0.1:3000, `sso.edulearn.htb` = Go/Gin on 127.0.0.1:3002, nginx routes
  by Host header.
- Walked the full OAuth flow by hand: register on SSO, login (JWT `token`
  cookie, HS256, HttpOnly, no SameSite), consent approve, exchange code for
  client `connect.sid`.
- Enumerated client surface: /assignment/:id, /submission/:id, /profile
  (displayName/avatar/bio, sanitized), /submit-url (report to teacher bot),
  /api/reactions|bookmarks|user/stats|assignments/search.
- chain_match: 0 stored candidates; web-triage routed; writeup search found
  ctfbase.com SSOS writeup. Solve is writeup-assisted (recorded).
- Confirmed dead paths: JWT secret not in common wordlists (all secrets
  openssl-random); sanitize-html 2.17.4 blocks stored XSS; code exchange needs
  random client_secret; non-edulearn.htb redirect_uri → 400.
- Instance 1 (port 32061) was already consumed: assignments created at
  12:35:30Z, checked at 12:58Z, so the startup bot had run and the flag sat in
  `student@edulearn.htb` under a random password — unreachable.
- Instance 2 (port 31650): ran `/tmp/opencode/ssos_exploit.py` within seconds.
  - Phase 0: WON the registration race (student@edulearn.htb / KnownPass123!).
  - Phase 1: client session + OAuth approval for the owned student account.
  - Phase 2: waited for the 3 teacher assignments.
  - Phase 3: sprayed `/submit-url` with a `data:text/html` form doing a
    text/plain JSON CSRF login to `sso.edulearn.htb:1337/api/login`
    (Gin `ShouldBindJSON` parses JSON regardless of Content-Type; input name is
    the JSON prefix, value is the closing brace) — this overwrote the bot's
    shared SSO `token` cookie with our student session.
  - Bot `loginSSO(student)` ignores its credentials and authorizes using the
    swapped cookie → client session becomes our student.
  - Flag landed in submission 1789477504377 on assignment 1789477346815.
  - Flag read from `/submission/1789477504377` (author = us).
- Flag: `HTB{REDACTED}`

## Traps
- Registration race alone is dead: without the cookie swap the bot authorizes
  as teacher and the flag is written to an unreadable teacher account.
- The CSRF must use `enctype="text/plain"` with the JSON-name trick, not
  url-encoded data, because the binder needs a raw JSON body.
- The bot resolves hosts to 127.0.0.1 on internal nginx port 1337 — the data
  URL must target `sso.edulearn.htb:1337`, not the external port.
- The Host header must include the external port for redirect_uri port
  validation to pass.
- A consumed instance (startup already run) is unrecoverable: the student has
  a random password and the flag is in an account that is neither ours nor
  readable by us.
- Solver: /tmp/opencode/ssos_exploit.py (must run within ~15s of fresh spawn).