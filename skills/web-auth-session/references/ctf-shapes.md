# CTF shapes — name the challenge, pick the file

Recurring auth-challenge archetypes from the solved corpus and public
writeups. Match the handout to a row → open the file → run the first probe.

---

## 1. "Decode me" — the JWT is already broken

**Signals**: token handed out at registration or a `/token` endpoint;
decodes to `{"user":"x","role":"user"}`. The verify call is missing,
`verify=False`, or `decode()` is used for authz.

**Play**: `jwt-deep.md §2` — `jwt_forge --claims '{"role":"admin"}' --alg ''`
→ replay. Most common single-step CTF auth solve.

## 2. "The hardcoded secret" — HS256 + weak key

**Signals**: `HS256` token; the repo config has `JWT_SECRET=changeme` or
the secret is the app name; or `session_dissect --try-keys` cracks it.

**Play**: `jwt-deep.md §6` — crack, forge, replay. Look for the secret in
`.env`, `docker-compose.yml`, the bundle source map, or `git log`.

## 3. "kid is a path" — key-lookup injection

**Signals**: header has `kid`; server reads the key from a file/DB by
`kid` name.

**Play**: `jwt-deep.md §5` — `kid=/dev/null` (empty secret),
`kid=/proc/sys/kernel/randomize_va_space` (known bytes), `kid' UNION SELECT 'x'`
(SQL into key query), `kid=x|id` (cmdi).

## 4. "Fetch my JWKS" — jku injection

**Signals**: header has `jku` or the verifier fetches remote JWKS based
on the header; or the app has a hardcoded JWKS URL you can't reach but a
*secondary* key-fetch path exists.

**Play**: `jwt-deep.md §5` — host `jwks.json` on your host, point `jku`
at it, sign with your own key.

## 5. "Same id twice" — session fixation

**Signals**: register a session before login; log in; the `Set-Cookie`
doesn't re-issue a new id — the *same* sid you planted now maps to a
user.

**Play**: `session-fixation.md §1` — the four-step probe.

## 6. "The id is a counter" — predictable session

**Signals**: `JSESSIONID=...A001`, `sid=1699999_<user>` or
`session=user:1699999999` — the id embeds username/time/sequence.

**Play**: `session-analysis.md §2-3` + `id_sweep` over the range.

## 7. "The token is in the URL" — reset-link leak

**Signals**: `GET /reset?token=T` page loads CDN analytics; the `Referer`
to the CDN carries `token=T`.

**Play**: `password-reset.md §5` — read the page source for external
resources; the token hits your log or the analytics provider's.

## 8. "Reset to anyone" — unbound reset token

**Signals**: `POST /reset {token, email}` — the token authenticates but
the `email` picks the row. Swap `email` to victim with your token.

**Play**: `password-reset.md §6` — verified HTB shape (nginxatsu).

## 9. "Register yourself an admin" — role in body

**Signals**: register endpoint accepts extra fields; the response or
`/api/me` echoes `role`; admin endpoints exist.

**Play**: `registration-abuse.md §1` — all-keys body, then verify the
role on `/api/me` and hit the admin endpoint.

## 10. "Verify is a suggestion" — MFA skip

**Signals**: login → pre-MFA session; `POST /mfa {code}`; the session is
already authenticated enough for `/api/me` or `/admin`.

**Play**: `mfa-bypass.md §2` — request the admin surface *before*
submitting a code.

## 11. "redirect_uri is a suggestion" — OAuth takeover

**Signals**: `/authorize` with `redirect_uri`; any allowlist bypass
(suffix, `@`, `.tld` trick) accepted.

**Play**: `oauth-flow-issues.md §2` — token lands on your host; replay
into `/callback` for the victim's session.

## 12. "Log in as them" — login CSRF via missing `state`

**Signals**: `/authorize` accepts no `state`; `/callback` binds the code
to whatever browser arrives.

**Play**: `oauth-flow-issues.md §3` — attacker-initiated code dropped in
victim's callback.

## 13. "Remember me" cookie is a forgeable blob

**Signals**: `remember_me` cookie `user_id|sig` or `md5(user_id+secret)`
with `secret` in source.

**Play**: recompute the signature; cookie becomes a forge-any-user
primitive.

## 14. "Impersonate anyone" — `?_switch_user=`/`?su=`/`?as=`

**Signals**: admin-panel style endpoints; the param isn't gated.

**Play**: `registration-abuse.md §8` — one query param becomes user
switching.

## 15. "The token is also the session" — itsdangerous/Flask

**Signals**: `session=eyJ....sig` Flask-style cookie; `SECRET_KEY` in
`.env`/`config.py`/`app.py`.

**Play**: `session_dissect` names it → `flask-unsign`/hand-signed with
the leaked key → session contains whatever the app stores (`user_id`,
`role`).

## 16. The verified local cards

| Card | The one line |
|---|---|
| htb-nginxatsu-alias-traversal-appkey-session-forge-blind-sqli | alias traversal → appkey leak → forge session → blind sqli |
| htb-tornadoservice-bot-csrf-class-pollution | bot + CSRF + class pollution — the session was the chain step |
| htb-ssos-oauth-registration-race-cookie-swap-json-csrf | OAuth registration race + cookie swap |

These are chain matches — run `chain_match --record <name>` first; the
card's `first_confirming_probe` is the authoritative probe.
