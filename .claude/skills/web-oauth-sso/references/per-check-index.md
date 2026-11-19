# Per-check index — the OAuth checks, indexed

The index is the lookup — the check, the artifact, the probe, the
confirmation, the falsifier.

## The check index

| Check | Artifact | Probe | Confirmation | Falsifier |
|---|---|---|---|---|
| `state` bound to session | `state` in authorize + callback | `callback?code=ABC&state=DIFFERENT` | `302` + `Set-Cookie: session=...` | `400 state mismatch` |
| `redirect_uri` exact match | `redirect_uri` in authorize | `authorize?...&redirect_uri=https://evil.com` | `302` + `Location: https://evil.com?code=ABC` | `400 invalid redirect_uri` |
| `SameSite` on IdP token | `Set-Cookie` header | `POST /api/login` `Content-Type: text/plain` | `200` + `Set-Cookie: token=NEW` | `SameSite=Lax|Strict` |
| `response_type` allowlist | `response_type` in authorize | `authorize?...&response_type=token` | `302` + `Location: ...#access_token=ABC` | `400 response_type not allowed` |
| `code_challenge` required | `code_challenge` in authorize | `authorize?...` without `code_challenge` | `302` + `Location: ...?code=ABC` | `400 code_challenge required` |
| `code_challenge_method` S256 | `code_challenge_method` in authorize | `authorize?...&code_challenge_method=plain` | `302` + `Location: ...?code=ABC` | `400 code_challenge_method must be S256` |
| `code_verifier` re-validated | `code_verifier` in token request | `token` request with wrong `code_verifier` | `200` + `{"access_token": "AT"}` | `400 invalid_grant` |
| `client_id` bound to code | `client_id` in authorize + token | `token` request with `client_id=B` | `200` + `{"access_token": "AT"}` | `400 invalid_client` |
| `aud` verified | `aud` in `id_token` | `id_token` with `aud=B` | `200` + session | `400` |
| `scope` allowlisted | `scope` in authorize + token | `authorize?...&scope=openid+admin` | `302` + `Location: ...?code=ABC` | `400 scope not allowed` |
| `sub` linking | `sub` in `id_token` | `register` the target account | `200` + `{"status": "registered"}` | `409 Conflict` |
| `email_verified` enforced | `email_verified` in `id_token` | `register` the target account | `200` + `{"status": "registered"}` | `400 email not verified` |
| registration idempotent | `email`/`username` in registration | `register` the same account twice | `200` + `{"status": "registered"}` | `409 Conflict` |
| `nonce` validated | `nonce` in `id_token` | replayed `id_token` | `200` + session | `400` |
| `signature` verified | `signature` in `id_token` | `id_token` with `alg=none` | `200` + session | `400` |
| `loginSSO` reads jar token | `loginSSO` step | `POST /api/login` `Content-Type: text/plain` | `200` + `Set-Cookie: token=NEW` | `loginSSO` reads credentials |

## The check mechanics

### Check 1 — `state` bound to session

The `state` is bound to the session — the callback verifies that the `state`
in the callback matches the `state` stored in the session. The falsifier:
`callback?code=ABC&state=DIFFERENT` returns `400 state mismatch`.

### Check 2 — `redirect_uri` exact match

The `redirect_uri` is validated exactly — a `400` on a wrong URI. The
falsifier: `authorize?...&redirect_uri=https://evil.com` returns `400
invalid redirect_uri`.

### Check 3 — `SameSite` on the IdP token

The `SameSite` controls whether the cookie is sent on cross-site requests.
The falsifier: `SameSite=Lax|Strict` on the IdP token — the cross-site write
does not land.

### Check 4 — `response_type` allowlist

The `response_type` is allowlisted to `code` — the implicit flow is not
accepted. The falsifier: `authorize?...&response_type=token` returns `400
response_type not allowed`.

### Check 5 — `code_challenge` required

The `code_challenge` is required — the PKCE shape is not dead. The
falsifier: `authorize?...` without `code_challenge` returns `400
code_challenge required`.

### Check 6 — `code_challenge_method` S256

The `code_challenge_method` is `S256` — the `plain` method is rejected. The
falsifier: `authorize?...&code_challenge_method=plain` returns `400
code_challenge_method must be S256`.

### Check 7 — `code_verifier` re-validated

The `code_verifier` is re-validated on exchange — a stolen code is
exchangeable. The falsifier: `token` request with a wrong `code_verifier`
returns `400 invalid_grant`.

### Check 8 — `client_id` bound to code

The `client_id` is bound to the code — a code minted for one client works on
another. The falsifier: `token` request with `client_id=B` returns `400
invalid_client`.

### Check 9 — `aud` verified

The `aud` is verified — the `id_token` is for the correct client. The
falsifier: `id_token` with `aud=B` is rejected.

### Check 10 — `scope` allowlisted

The `scope` is allowlisted — a broader scope is rejected. The falsifier:
`authorize?...&scope=openid+admin` returns `400 scope not allowed`.

### Check 11 — `sub` linking

The linking is on `sub` — the `id_token` `sub` is the linking field. The
falsifier: `register` the target account returns `409 Conflict` — the
linking is on `sub`, not `email`.

### Check 12 — `email_verified` enforced

The `email_verified` is enforced — the `id_token` `email` is verified. The
falsifier: `register` the target account returns `400 email not verified`.

### Check 13 — registration idempotent

The registration is idempotent — a duplicate registration returns the same
account. The falsifier: `register` the same account twice returns `409
Conflict`.

### Check 14 — `nonce` validated

The `nonce` is validated — the `id_token` `nonce` is bound to the request.
The falsifier: a replayed `id_token` is rejected.

### Check 15 — `signature` verified

The `signature` is verified — the `id_token` `signature` is verified. The
falsifier: `id_token` with `alg=none` is rejected.

### Check 16 — `loginSSO` reads jar token

The `loginSSO` reads the jar's token — the `loginSSO` step ignores
credentials. The falsifier: `POST /api/login` `Content-Type: text/plain`
returns `200` + `Set-Cookie: token=NEW` — the `loginSSO` step reads the
jar's token.
