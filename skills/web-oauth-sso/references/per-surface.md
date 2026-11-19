# Per-surface — the OAuth attack surfaces, with the full mechanics

The per-surface module names each attack surface. This module carries the
full mechanics — the artifact, the probe, the confirmation, the falsifier,
and the escalation.

## Surface 1 — the `authorize` endpoint

**The artifact**: `GET /authorize?client_id=...&redirect_uri=...&response_type=...&state=...`

**The probe**: `authorize?...&redirect_uri=https://evil.com/callback` — a
URI not in the registered allowlist.

**The confirmation**: a `302` + `Location: https://evil.com/callback?code=ABC` —
the code is delivered to the attacker.

**The falsifier**: `400 invalid redirect_uri` — the `redirect_uri` is
validated exactly.

**The escalation**: code-interception — the code is delivered to the
attacker's endpoint; replay it against the app's callback.

## Surface 2 — the `callback` endpoint

**The artifact**: `GET /callback?code=...&state=...`

**The probe**: `callback?code=ABC&state=DIFFERENT` — a `state` the session
never stored.

**The confirmation**: a `302` + `Set-Cookie: session=...` — the session is
issued on the victim's account.

**The falsifier**: `400 state mismatch` — the `state` is bound to the session.

**The escalation**: login-CSRF or linking-CSRF — the victim visits the
attacker's authorize URL; the callback accepts the code and issues a session
on the victim's account.

## Surface 3 — the `token` endpoint

**The artifact**: `POST /token {grant_type=authorization_code, code=..., client_id=..., client_secret=..., redirect_uri=...}`

**The probe**: `token` request with `client_id=B` — a code minted for client
A exchanged as client B.

**The confirmation**: a `200` + `{"access_token": "AT"}` — the token is issued
for client B.

**The falsifier**: `400 invalid_client` — the `client_id` is bound to the code.

**The escalation**: code replay — a code minted for client A is replayable
by client B; the `id_token` with `aud=B` is accepted.

## Surface 4 — the `login` endpoint

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

## Surface 5 — the `register` endpoint

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

## Surface 6 — the `authorize` `state` parameter

**The artifact**: `authorize?...&state=STATE` — the `state` is not bound to
the session.

**The probe**: `callback?code=ABC&state=DIFFERENT` — a `state` the session
never stored.

**The confirmation**: a `302` + `Set-Cookie: session=...` — the session is
issued on the victim's account.

**The falsifier**: `400 state mismatch` — the `state` is bound to the session.

**The escalation**: login-CSRF or linking-CSRF — the victim visits the
attacker's authorize URL; the callback accepts the code and issues a session
on the victim's account.

## Surface 7 — the `authorize` `redirect_uri` parameter

**The artifact**: `authorize?...&redirect_uri=https://evil.com/callback` —
the `redirect_uri` is not validated.

**The probe**: `authorize?...&redirect_uri=https://evil.com/callback` — a
URI not in the registered allowlist.

**The confirmation**: a `302` + `Location: https://evil.com/callback?code=ABC` —
the code is delivered to the attacker.

**The falsifier**: `400 invalid redirect_uri` — the `redirect_uri` is
validated exactly.

**The escalation**: code-interception — the code is delivered to the
attacker's endpoint; replay it against the app's callback.

## Surface 8 — the `authorize` `response_type` parameter

**The artifact**: `authorize?...&response_type=token` — the implicit flow is
accepted.

**The probe**: `authorize?...&response_type=token` — an implicit-flow request.

**The confirmation**: a `302` + `Location: https://app/callback#access_token=ABC` —
the token is in the fragment.

**The falsifier**: `400 response_type not allowed` — the `response_type` is
allowlisted to `code`.

**The escalation**: fragment-harvest — the callback page loads a subresource;
the `Referer` carries the fragment; the token is leaked.

## Surface 9 — the `authorize` `code_challenge` parameter

**The artifact**: `authorize?...&code_challenge_method=plain` — the verifier
is sent in the clear.

**The probe**: `authorize?...&code_challenge_method=plain` — the `plain`
method is accepted.

**The confirmation**: a `302` + `Location: https://app/callback?code=ABC` —
the `plain` method is accepted.

**The falsifier**: `400 code_challenge_method must be S256` — the `plain`
method is rejected.

**The escalation**: stolen-code exchange — the verifier is captured from
the URL or the browser history; the code is exchangeable.

## Surface 10 — the `token` `code_verifier` parameter

**The artifact**: `POST /token {..., code_verifier: ...}` — the verifier is
not re-validated.

**The probe**: `token` request with a wrong `code_verifier` — the verifier
is not re-validated.

**The confirmation**: a `200` + `{"access_token": "AT"}` — the token is issued.

**The falsifier**: `400 invalid_grant` — the `code_verifier` is re-validated.

**The escalation**: stolen-code exchange — a code minted with a challenge is
exchangeable with a wrong verifier.
