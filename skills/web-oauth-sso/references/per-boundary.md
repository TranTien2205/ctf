# Per-boundary — the OAuth trust boundaries, with the full mechanics

The per-boundary module names each trust boundary. This module carries the
full mechanics — where the trust breaks, what the evidence looks like, and
what the falsifier is.

## Boundary 1 — user → browser → app

The user's browser issues the `GET /login` — the app `302`s to the IdP's
`authorize` endpoint. The trust: the app trusts the browser to carry the
redirect. The break: the browser carries a `state` that is not bound to the
session — the CSRF shape.

The evidence: `callback?code=ABC&state=DIFFERENT` returns `302` + `Set-Cookie:
session=...` — the session is issued on the victim's account.

The falsifier: `400 state mismatch` — the `state` is bound to the session.

## Boundary 2 — app → IdP → app

The app `302`s to the IdP's `authorize` endpoint — the IdP `302`s back to
the app's `callback` endpoint with a `code`. The trust: the IdP trusts the
`redirect_uri` to be the registered URI. The break: the `redirect_uri` is
not validated — the code is delivered to an attacker URI.

The evidence: `authorize?...&redirect_uri=https://evil.com/callback` returns
`302` + `Location: https://evil.com/callback?code=ABC` — the code is delivered
to the attacker.

The falsifier: `400 invalid redirect_uri` — the `redirect_uri` is validated
exactly.

## Boundary 3 — app → IdP → app → session

The app exchanges the `code` for a `token` — the IdP issues the `token`; the
app issues a `session`. The trust: the app trusts the `id_token` to carry
the identity. The break: the `id_token` is not verified — the `signature`,
`alg`, `aud`, `iss`, or `nonce` is not validated.

The evidence: `id_token` with `alg=none` is accepted — the `id_token` is
forgeable.

The falsifier: `400` on `alg=none` — the signature is verified.

## Boundary 4 — app → session → user

The app issues a `session` — the user's browser carries the `session` cookie
on every request. The trust: the app trusts the `session` to be the user's
identity. The break: the `session` is not bound to the `id_token` — a
replayed `id_token` is accepted.

The evidence: a replayed `id_token` is accepted — the `nonce` is not
validated.

The falsifier: `400` on `nonce` mismatch — the `nonce` is bound to the
`id_token`.

## Boundary 5 — IdP → cookie → app

The IdP issues a `token` cookie — the app's `loginSSO` step reads the jar's
token. The trust: the app trusts the jar's token to be the user's identity.
The break: the `SameSite` is missing or `None` — a cross-site write
overwrites the token.

The evidence: `POST /api/login` `Content-Type: text/plain` returns `200` +
`Set-Cookie: token=NEW` — the token is overwritten.

The falsifier: `SameSite=Lax|Strict` on the IdP token — the cross-site write
does not land.

## Boundary 6 — app → account → user

The app links the IdP's identity to a local account — the linking field is
`email`/`username`/`sub`. The trust: the app trusts the `id_token` to carry
the identity. The break: the linking is on `email`/`username` — the
pre-registration race lands on the attacker's account.

The evidence: `register` the target account returns `200` + `{"status":
"registered"}` — the account is registered; the OAuth login lands on the
attacker's account.

The falsifier: `409 Conflict` — the account is already registered; the
linking is on `sub`, not `email`.

## Boundary 7 — IdP → code → app

The IdP issues a `code` — the app exchanges it for a `token`. The trust: the
app trusts the `code` to be bound to the `client_id` and the `redirect_uri`.
The break: the `code` is not bound to `client_id` or `redirect_uri` — a
stolen code is exchangeable.

The evidence: `token` request with `client_id=B` returns `200` + `{"access_token":
"AT"}` — the token is issued for client B.

The falsifier: `400 invalid_client` — the `client_id` is bound to the code.

## Boundary 8 — IdP → token → app

The IdP issues an `access_token` — the app trusts it to authorize API calls.
The trust: the app trusts the `access_token` to carry the `scope` that was
requested. The break: the `scope` is not allowlisted — a broader scope is
accepted.

The evidence: `authorize?...&scope=openid+admin` returns `302` + `Location:
https://app/callback?code=ABC` — the broader scope is accepted.

The falsifier: `400 scope not allowed` — the `scope` is allowlisted.
