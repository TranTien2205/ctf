# Extended corpus — the OAuth shapes that are not on the standard checklist

The extended corpus names the unusual shapes — the ones that look like they
are validated but are not, and the ones that look broken but are correct.

## The extended map

| Shape | The mechanism | The probe |
|---|---|---|
| `state` bound to code, not session | a mismatched `state` is rejected because the `state` in the callback does not match the `state` in the code's binding | `callback?code=STOLEN_CODE&state=STOLEN_STATE` |
| `redirect_uri` validated on authorize, not on exchange | the `token` step does not re-validate `redirect_uri` | `token` request with `redirect_uri=https://evil.com` |
| `SameSite=Lax` but the delivery is a top-level GET | `Lax` allows top-level GET navigations — a `<img src=...>` or a `<a href=...>` cross-site GET carries the cookie | a cross-site `<img src=...>` to the IdP's login endpoint |
| `response_type` allowlisted to `code` but `response_mode` is not | `response_mode=form_post` or `web_message` delivers the code to a different surface | `authorize?...&response_mode=web_message` |
| `code_challenge` required but `code_verifier` not re-validated | the `token` step does not re-validate `code_verifier` | `token` request with a wrong `code_verifier` |
| `client_id` bound to the code but `aud` not verified | the `id_token` is not verified for `aud` | `id_token` with `aud=B` |
| `scope` allowlisted but `offline_access` accepted | the `token` endpoint issues a `refresh_token` | `authorize?...&scope=openid+offline_access` |
| `nonce` validated but bound to the `id_token`, not the request | a replayed `id_token` carries its own `nonce` | a replayed `id_token` |
| `login_hint` reflected but not injectable | the reflection is HTML-encoded, not a DOM sink | `login_hint=<script>` — is it HTML-encoded? |
| `id_token_hint` replayable but bound to `client_id` | a replayed `id_token` minted for client A is rejected by client B | `id_token_hint=ID_TOKEN_FOR_A` in client B's authorize |
| `request`/`request_uri` SSRF but the URI is allowlisted | only a registered URI is fetched | `request_uri=https://evil.com/jwt` |
| `claims` broader but the app does not use them | the `id_token` carries the broader claims but the app's endpoints do not check them | `claims={"groups":["admin"]}` |

## The extended mechanics

### Extended 1 — `state` bound to code, not session

The `state` is bound to the `code` — a mismatched `state` is rejected because
the `state` in the callback does not match the `state` in the code's binding.
But a stolen code is replayable with its own `state` — the `state` is bound
to the code, not to the session.

The evidence: `callback?code=ABC&state=DIFFERENT` returns `400 state mismatch`;
`callback?code=STOLEN_CODE&state=STOLEN_STATE` is accepted.

### Extended 2 — `redirect_uri` validated on authorize, not on exchange

The `authorize` step validates `redirect_uri` — a `400` on a wrong URI. But
the `token` step does not re-validate it — a code minted for `redirect_uri=A`
is exchangeable with `redirect_uri=B`.

The evidence: `authorize?...&redirect_uri=https://evil.com` returns `400`;
`token` request with `redirect_uri=https://evil.com` returns `200` + token.

### Extended 3 — `SameSite=Lax` but the delivery is a top-level GET

`SameSite=Lax` allows top-level GET navigations — a `<img src=...>` or a
`<a href=...>` cross-site GET carries the cookie. The cookie-swap shape is
live via a GET delivery — not a POST.

The evidence: `SameSite=Lax` on the IdP token; a cross-site `<img src=...>`
to the IdP's login endpoint issues a `302` + `Set-Cookie` — the cookie is
set because `Lax` allows top-level GETs.

### Extended 4 — `response_type` allowlisted to `code` but `response_mode` is not

`response_type` is allowlisted to `code` — the implicit flow is not accepted.
But `response_mode` is not validated — `response_mode=form_post` delivers
the code to a POST endpoint, `response_mode=web_message` delivers it to a
`postMessage` target.

The evidence: `response_type=token` returns `400`; `response_mode=web_message`
delivers the code to the attacker's frame.

### Extended 5 — `code_challenge` required but `code_verifier` not re-validated

`code_challenge` is required — the PKCE shape is not dead. But the `token`
step does not re-validate `code_verifier` — a code minted with a challenge
is exchangeable with a wrong verifier.

The evidence: `authorize` without `code_challenge` returns `400`; `token`
request with a wrong `code_verifier` returns `200` + token.

### Extended 6 — `client_id` bound to the code but `aud` not verified

The code is bound to `client_id` — the exchange fails on a different
`client_id`. But `aud` in the `id_token` is not verified — a code minted for
client A is exchangeable by client B if client B's `aud` is accepted.

The evidence: `token` request with a code minted for client A exchanged as
client B returns `400 invalid_client`; the `id_token` with `aud=B` is
accepted.

### Extended 7 — `scope` allowlisted but `offline_access` accepted

`scope` is allowlisted — `admin` is rejected. But `offline_access` is
accepted — the token endpoint issues a `refresh_token` alongside the
`access_token`.

The evidence: `authorize?...&scope=openid+admin` returns `400`;
`authorize?...&scope=openid+offline_access` returns `200` + `refresh_token`.

### Extended 8 — `nonce` validated but bound to the `id_token`, not the request

`nonce` is validated — a mismatched `nonce` is rejected. But it is bound to
the `id_token` it was minted for, not to the request's `nonce` — a replayed
`id_token` carries its own `nonce`.

The evidence: `authorize` with `nonce=N` returns an `id_token` with `nonce=N`;
a replayed `id_token` with a different `nonce` is accepted.
