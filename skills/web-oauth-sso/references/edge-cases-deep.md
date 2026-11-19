# Edge cases deep — the OAuth surfaces that are easy to miss

The edge-cases module names the unusual shapes. This module carries the
full mechanics — the surfaces that look like they are validated but are
not, and the ones that look broken but are correct.

## Edge 1 — `state` bound to the code, not the session

The `state` is not bound to the session — it is bound to the `code`. A
mismatched `state` is rejected because the `state` in the callback does not
match the `state` in the code's binding — not because it does not match the
session's stored `state`.

The evidence: `callback?code=ABC&state=DIFFERENT` returns `400 state
mismatch` — but `callback?code=STOLEN_CODE&state=STOLEN_STATE` is accepted.
The `state` is bound to the code — a stolen code is replayable with its own
`state`.

## Edge 2 — `redirect_uri` validated on authorize but not on exchange

The `authorize` step validates `redirect_uri` — a `400` on a wrong URI. But
the `token` step does not re-validate it — a code minted for `redirect_uri=A`
is exchangeable with `redirect_uri=B`.

The evidence: `authorize?...&redirect_uri=https://evil.com` returns `400`;
`token` request with `redirect_uri=https://evil.com` returns `200` + token.
The `redirect_uri` is validated on authorize but not on exchange — the
code-interception shape is live on the token step.

## Edge 3 — `SameSite=Lax` but the delivery is a top-level GET

`SameSite=Lax` allows top-level GET navigations — a `<img src=...>` or a
`<a href=...>` cross-site GET carries the cookie. The cookie-swap shape is
live via a GET delivery — not a POST.

The evidence: `SameSite=Lax` on the IdP token; a cross-site `<img src=...>`
to the IdP's login endpoint issues a `302` + `Set-Cookie` — the cookie is
set because `Lax` allows top-level GETs.

## Edge 4 — `response_type` allowlisted to `code` but `response_mode` is not

`response_type` is allowlisted to `code` — the implicit flow is not accepted.
But `response_mode` is not validated — `response_mode=form_post` delivers
the code to a POST endpoint, `response_mode=web_message` delivers it to a
`postMessage` target.

The evidence: `response_type=token` returns `400`; `response_mode=web_message`
delivers the code to the attacker's frame. The `response_mode` is the
delivery mechanism — the code is delivered to a different surface.

## Edge 5 — `code_challenge` required but `code_verifier` not re-validated

`code_challenge` is required — the PKCE shape is not dead. But the `token`
step does not re-validate `code_verifier` — a code minted with a challenge
is exchangeable with a wrong verifier.

The evidence: `authorize` without `code_challenge` returns `400`; `token`
request with a wrong `code_verifier` returns `200` + token. The `code_challenge`
is required but the `code_verifier` is not re-validated — the PKCE shape is
live on the token step.

## Edge 6 — `client_id` bound to the code but `aud` not verified

The code is bound to `client_id` — the exchange fails on a different
`client_id`. But `aud` in the `id_token` is not verified — a code minted for
client A is exchangeable by client B if client B's `aud` is accepted.

The evidence: `token` request with a code minted for client A exchanged as
client B returns `400 invalid_client`; the `id_token` with `aud=B` is
accepted. The `client_id` is bound but `aud` is not verified — the
cross-client shape is live on the `id_token` step.

## Edge 7 — `scope` allowlisted but `offline_access` accepted

`scope` is allowlisted — `admin` is rejected. But `offline_access` is
accepted — the token endpoint issues a `refresh_token` alongside the
`access_token`.

The evidence: `authorize?...&scope=openid+admin` returns `400`;
`authorize?...&scope=openid+offline_access` returns `200` + `refresh_token`.
The `scope` is allowlisted but `offline_access` is accepted — the
refresh-token shape is live.

## Edge 8 — `nonce` validated but bound to the `id_token`, not the request

`nonce` is validated — a mismatched `nonce` is rejected. But it is bound to
the `id_token` it was minted for, not to the request's `nonce` — a replayed
`id_token` carries its own `nonce`.

The evidence: `authorize` with `nonce=N` returns an `id_token` with `nonce=N`;
a replayed `id_token` with a different `nonce` is accepted. The `nonce` is
bound to the `id_token` — a replayed `id_token` is replayable.

## Edge 9 — `login_hint` reflected but not injectable

`login_hint` is reflected in the authorize page — the prefilled username is
in the HTML. But it is not injectable — the reflection is HTML-encoded, not
a DOM sink.

The evidence: `login_hint=<script>` returns the HTML-encoded reflection;
the DOM does not execute it. The `login_hint` is reflected but not
injectable — the sink is not reached.

## Edge 10 — `id_token_hint` replayable but bound to `client_id`

`id_token_hint` is replayable — a previous `id_token` is accepted. But it is
bound to `client_id` — a replayed `id_token` minted for client A is rejected
by client B.

The evidence: `id_token_hint=ID_TOKEN_FOR_A` in client B's authorize request
returns `400`; `id_token_hint=ID_TOKEN_FOR_B` in client B's authorize request
returns `200`. The `id_token_hint` is bound to `client_id` — the replay is
dead.

## Edge 11 — `request`/`request_uri` SSRF but the URI is allowlisted

`request_uri` is fetched — the IdP's `request_uri` endpoint is SSRF-able. But
the URI is allowlisted — only a registered URI is fetched.

The evidence: `request_uri=https://evil.com/jwt` returns `400`;
`request_uri=https://registered.com/jwt` returns `200` + JWT. The
`request_uri` is allowlisted — the SSRF shape is dead.

## Edge 12 — `claims` broader but the app does not use them

`claims` is broader — `acr_values` and `groups`/`roles` are accepted. But
the app does not use them — the `id_token` carries the broader claims but
the app's endpoints do not check them.

The evidence: `claims={"groups":["admin"]}` returns an `id_token` with
`groups:["admin"]`; the app's endpoint does not check `groups`. The `claims`
are broader but unused — the sink is not reached.
