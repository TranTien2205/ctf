# Per-mechanism — the OAuth mechanisms, with the full mechanics

The per-mechanism module names each mechanism. This module carries the full
mechanics — the artifact, the probe, the confirmation, the falsifier, and
the escalation.

## Mechanism 1 — state CSRF

**The artifact**: `state` in the `authorize` URL and the `callback` URL.

**The probe**: `callback?code=ABC&state=DIFFERENT` — a `state` the session
never stored.

**The confirmation**: a `302` + `Set-Cookie: session=...` — the session is
issued on the victim's account.

**The falsifier**: `400 state mismatch` — the `state` is bound to the session.

**The escalation**: login-CSRF or linking-CSRF — the victim visits the
attacker's authorize URL; the callback accepts the code and issues a session
on the victim's account.

## Mechanism 2 — redirect interception

**The artifact**: `redirect_uri` in the `authorize` URL.

**The probe**: `authorize?...&redirect_uri=https://evil.com/callback` — a
URI not in the registered allowlist.

**The confirmation**: a `302` + `Location: https://evil.com/callback?code=ABC` —
the code is delivered to the attacker.

**The falsifier**: `400 invalid redirect_uri` — the `redirect_uri` is
validated exactly.

**The escalation**: code-interception — the code is delivered to the
attacker's endpoint; replay it against the app's callback.

## Mechanism 3 — cookie swap

**The artifact**: `SameSite` on the IdP token + `loginSSO` ignores credentials.

**The probe**: `POST /api/login` `Content-Type: text/plain` — the raw JSON
lands; the `Set-Cookie` overwrites the shared jar's token.

**The confirmation**: a `200` + `Set-Cookie: token=NEW` — the token is
overwritten.

**The falsifier**: `SameSite=Lax|Strict` on the IdP token — the cross-site
write does not land.

**The escalation**: `data:text/html` URL carries a form that POSTs to the
IdP's `/api/login` — the `Set-Cookie` overwrites the shared jar's token;
the `loginSSO` step uses the swapped token.

## Mechanism 4 — account linking

**The artifact**: `email`/`username`/`sub` in the `id_token`.

**The probe**: `register` the target account — the account is registered
with the attacker's password.

**The confirmation**: a `200` + `{"status": "registered"}` — the account is
registered; the OAuth login lands on the attacker's account.

**The falsifier**: `409 Conflict` — the account is already registered; the
linking is on `sub`, not `email`.

**The escalation**: pre-registration race — the attacker hammers
`POST /api/register` for the bot's account before the bot's `registerUser`
step runs.

## Mechanism 5 — implicit leak

**The artifact**: `response_type` + `access_token` in the fragment.

**The probe**: `authorize?...&response_type=token` — an implicit-flow request.

**The confirmation**: a `302` + `Location: https://app/callback#access_token=ABC` —
the token is in the fragment.

**The falsifier**: `400 response_type not allowed` — the `response_type` is
allowlisted to `code`.

**The escalation**: fragment-harvest — the callback page loads a subresource;
the `Referer` carries the fragment; the token is leaked.

## Mechanism 6 — PKCE bypass

**The artifact**: `code_challenge` + `code_verifier`.

**The probe**: `authorize?...&code_challenge_method=plain` — the verifier
is sent in the clear.

**The confirmation**: a `302` + `Location: https://app/callback?code=ABC` —
the `plain` method is accepted.

**The falsifier**: `400 code_challenge_method must be S256` — the `plain`
method is rejected.

**The escalation**: stolen-code exchange — the verifier is captured from
the URL or the browser history; the code is exchangeable.

## Mechanism 7 — cross-client

**The artifact**: `client_id` + `aud` in the `id_token`.

**The probe**: `token` request with `client_id=B` — a code minted for client
A exchanged as client B.

**The confirmation**: a `200` + `{"access_token": "AT"}` — the token is issued
for client B.

**The falsifier**: `400 invalid_client` — the `client_id` is bound to the code.

**The escalation**: code replay — a code minted for client A is replayable
by client B; the `id_token` with `aud=B` is accepted.

## Mechanism 8 — scope escalation

**The artifact**: `scope` in the `authorize` URL + the token.

**The probe**: `authorize?...&scope=openid+admin` — a broader scope.

**The confirmation**: a `302` + `Location: https://app/callback?code=ABC` —
the broader scope is accepted; the token carries `scope=openid+admin`.

**The falsifier**: `400 scope not allowed` — the `scope` is allowlisted.

**The escalation**: broader token — the token carries a broader scope; check
what the broader scope unlocks on the app's endpoints.

## Mechanism 9 — registration race

**The artifact**: `email`/`username` in the registration endpoint.

**The probe**: `register` the same account twice — the account is registered
with the attacker's password.

**The confirmation**: a `200` + `{"status": "registered"}` — the account is
registered; the OAuth login lands on the attacker's account.

**The falsifier**: `409 Conflict` — the account is already registered; the
registration is idempotent.

**The escalation**: pre-registration race — the attacker hammers
`POST /api/register` for the bot's account before the bot's `registerUser`
step runs.
