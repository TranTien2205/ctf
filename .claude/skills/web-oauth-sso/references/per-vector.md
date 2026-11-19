# Per-vector — the OAuth attack vectors, with the full mechanics

The per-vector module names each attack vector. This module carries the full
mechanics — the entry point, the chain, the sink, and the falsifier.

## Vector 1 — the `state` CSRF vector

**The entry**: `authorize?...&state=STATE` — the `state` is not bound to the
session.

**The chain**: the victim visits the attacker's `authorize` URL; the IdP
issues a code for the victim's account; the callback accepts the `state` and
issues a session on the victim's account.

**The sink**: the victim's account — the session is issued on the victim's
account.

**The falsifier**: `400 state mismatch` — the `state` is bound to the session.

## Vector 2 — the `redirect_uri` interception vector

**The entry**: `authorize?...&redirect_uri=https://evil.com/callback` — the
`redirect_uri` is not validated.

**The chain**: the IdP `302`s to `https://evil.com/callback?code=ABC` — the
code is delivered to the attacker; the attacker replays it against the app's
callback.

**The sink**: the attacker's account — the session is issued on the
attacker's account.

**The falsifier**: `400 invalid redirect_uri` — the `redirect_uri` is
validated exactly.

## Vector 3 — the cookie-swap vector

**The entry**: `POST /api/login` `Content-Type: text/plain` — the raw JSON
lands; the `Set-Cookie` overwrites the shared jar's token.

**The chain**: the `data:text/html` URL carries a form that POSTs to the
IdP's `/api/login` — the `Set-Cookie` overwrites the shared jar's token;
the `loginSSO` step uses the swapped token.

**The sink**: the attacker's account — the session is issued on the
attacker's account.

**The falsifier**: `SameSite=Lax|Strict` on the IdP token — the cross-site
write does not land.

## Vector 4 — the account-linking vector

**The entry**: `register` the target account — the account is registered
with the attacker's password.

**The chain**: the attacker pre-registers the bot's account; the bot's
`registerUser` step fails; the OAuth login lands on the attacker's account.

**The sink**: the flag submission — the bot's `submitAssignment` step writes
the flag to `/submission/1`.

**The falsifier**: `409 Conflict` — the account is already registered; the
linking is on `sub`, not `email`.

## Vector 5 — the implicit-leak vector

**The entry**: `authorize?...&response_type=token` — the implicit flow is
accepted.

**The chain**: the `302` carries `#access_token=ABC` — the callback page
loads a subresource; the `Referer` carries the fragment; the token is leaked.

**The sink**: the victim's account — the token is replayable.

**The falsifier**: `400 response_type not allowed` — the `response_type` is
allowlisted to `code`.

## Vector 6 — the PKCE-bypass vector

**The entry**: `authorize?...&code_challenge_method=plain` — the verifier
is sent in the clear.

**The chain**: the verifier is captured from the URL or the browser history;
the code is exchangeable with the captured verifier.

**The sink**: the attacker's account — the session is issued on the
attacker's account.

**The falsifier**: `400 code_challenge_method must be S256` — the `plain`
method is rejected.

## Vector 7 — the cross-client vector

**The entry**: `token` request with `client_id=B` — a code minted for client
A exchanged as client B.

**The chain**: the code is minted for client A; the attacker exchanges it
as client B; the `id_token` with `aud=B` is accepted.

**The sink**: the attacker's account — the session is issued on the
attacker's account.

**The falsifier**: `400 invalid_client` — the `client_id` is bound to the code.

## Vector 8 — the scope-escalation vector

**The entry**: `authorize?...&scope=openid+admin` — a broader scope.

**The chain**: the `authorize` request carries `scope=openid+admin`; the
`id_token` carries `scope=openid+admin`; the app's endpoints check `scope`.

**The sink**: the admin endpoint — the `admin` scope unlocks the endpoint.

**The falsifier**: `400 scope not allowed` — the `scope` is allowlisted.

## Vector 9 — the registration-race vector

**The entry**: `register` the target account — the account is registered
with the attacker's password.

**The chain**: the attacker hammers `POST /api/register` for the bot's
account before the bot's `registerUser` step runs; the OAuth login lands
on the attacker's account.

**The sink**: the flag submission — the bot's `submitAssignment` step writes
the flag to `/submission/1`.

**The falsifier**: `409 Conflict` — the account is already registered; the
registration is idempotent.
