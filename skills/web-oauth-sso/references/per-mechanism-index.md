# Per-mechanism index — the OAuth mechanisms, indexed

The index is the lookup — the mechanism, the artifact, the probe, the
confirmation, the falsifier.

## The mechanism index

| Mechanism | Artifact | Probe | Confirmation | Falsifier |
|---|---|---|---|---|
| state CSRF | `state` in authorize + callback | `callback?code=ABC&state=DIFFERENT` | `302` + `Set-Cookie: session=...` | `400 state mismatch` |
| redirect interception | `redirect_uri` in authorize | `authorize?...&redirect_uri=https://evil.com` | `302` + `Location: https://evil.com?code=ABC` | `400 invalid redirect_uri` |
| cookie swap | `SameSite` on IdP token | `POST /api/login` `Content-Type: text/plain` | `200` + `Set-Cookie: token=NEW` | `SameSite=Lax|Strict` |
| account linking | `email`/`username`/`sub` in `id_token` | `register` the target account | `200` + `{"status": "registered"}` | `409 Conflict` |
| implicit leak | `response_type` + `access_token` in fragment | `authorize?...&response_type=token` | `302` + `Location: ...#access_token=ABC` | `400 response_type not allowed` |
| PKCE bypass | `code_challenge` + `code_verifier` | `authorize?...&code_challenge_method=plain` | `302` + `Location: ...?code=ABC` | `400 code_challenge_method must be S256` |
| cross-client | `client_id` + `aud` in `id_token` | `token` request with `client_id=B` | `200` + `{"access_token": "AT"}` | `400 invalid_client` |
| scope escalation | `scope` in authorize + token | `authorize?...&scope=openid+admin` | `302` + `Location: ...?code=ABC` | `400 scope not allowed` |
| registration race | `email`/`username` in registration | `register` the same account twice | `200` + `{"status": "registered"}` | `409 Conflict` |
| device flow | `device_code` + `user_code` | `POST /token` `grant_type=urn:ietf:params:oauth:grant-type:device_code` | `200` + `{"access_token": "AT"}` | `400` |
| refresh replay | `refresh_token` in token request | `POST /token` `grant_type=refresh_token` | `200` + `{"access_token": "AT"}` | `400` |
| logout forge | `logout_token`/`sid` in backchannel | `POST /logout` `logout_token=FORGED` | `200` + session terminated | `400` |

## The mechanism mechanics

### Mechanism 1 — state CSRF

The `state` is not bound to the session — the callback accepts a `state` that
was issued for a different session. The chain: the victim visits the
attacker's authorize URL; the IdP issues a code for the victim's account;
the callback accepts the `state` and issues a session on the victim's account.

### Mechanism 2 — redirect interception

The `redirect_uri` is not validated — the code is delivered to an attacker
URI. The chain: the IdP `302`s to `https://evil.com/callback?code=ABC` — the
code is delivered to the attacker; the attacker replays it against the app's
callback.

### Mechanism 3 — cookie swap

The `SameSite` is missing or `None` on the IdP token — a cross-site write
overwrites the token. The chain: a `data:text/html` URL carries a form that
POSTs to the IdP's `/api/login` — the `Set-Cookie` overwrites the shared
jar's token; the `loginSSO` step uses the swapped token.

### Mechanism 4 — account linking

The linking is on `email`/`username`/`sub` — the pre-registration race lands
on the attacker's account. The chain: the attacker pre-registers the bot's
account; the bot's `registerUser` step fails; the OAuth login lands on the
attacker's account.

### Mechanism 5 — implicit leak

The `response_type` is not allowlisted — the implicit flow is accepted. The
chain: the `302` carries `#access_token=ABC` — the callback page loads a
subresource; the `Referer` carries the fragment; the token is leaked.

### Mechanism 6 — PKCE bypass

The `code_challenge` is not required or `code_verifier` is not re-validated —
a stolen code is exchangeable. The chain: the verifier is captured from the
URL or the browser history; the code is exchangeable with the captured verifier.

### Mechanism 7 — cross-client

The `client_id` is not bound to the code or `aud` is not verified — a code
minted for one client works on another. The chain: the code is minted for
client A; the attacker exchanges it as client B; the `id_token` with `aud=B`
is accepted.

### Mechanism 8 — scope escalation

The `scope` is not allowlisted — a broader scope is accepted. The chain: the
`authorize` request carries `scope=openid+admin`; the `id_token` carries
`scope=openid+admin`; the app's endpoints check `scope`.

### Mechanism 9 — registration race

The registration is not idempotent — the attacker pre-registers the bot's
account. The chain: the attacker hammers `POST /api/register` for the bot's
account before the bot's `registerUser` step runs; the OAuth login lands on
the attacker's account.
