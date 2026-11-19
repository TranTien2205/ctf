# Detection matrix — the artifact → mechanism → probe map

Every artifact in the OAuth transcript maps to a mechanism and a probe. This
matrix is the lookup — find the artifact, name the mechanism, run the probe.

## The artifact map

| Artifact | Mechanism | Probe | Confirmation | Falsifier |
|---|---|---|---|---|
| `state` in authorize URL | CSRF binding | callback with mismatched state | session issued | `400 state mismatch` |
| `state` in callback URL | CSRF binding | cross-session replay | session issued | `400 state mismatch` |
| `redirect_uri` in authorize URL | code delivery target | authorize with wrong URI | code delivered | `400 invalid redirect_uri` |
| `code` in callback URL | replay surface | replay the code | session issued | `400 invalid_grant` |
| `code` in fragment | leak surface | read `window.location.hash` | token in DOM | not in fragment |
| `access_token` in fragment | leak surface | Referer on subresource | token in Referer | no subresource |
| `id_token` in fragment | leak surface | decode + forge | accepted | signature verified |
| `nonce` in authorize URL | replay binding | replay the id_token | accepted | `nonce` validated |
| `scope` in authorize URL | permission surface | broader scope | granted | `400 scope not allowed` |
| `code_challenge` in authorize URL | PKCE binding | authorize without it | accepted | `400` or required |
| `code_challenge_method` in authorize URL | PKCE method | `plain` method | accepted | only `S256` |
| `code_verifier` in token request | PKCE verifier | wrong verifier | token issued | `400 invalid_grant` |
| `client_id` in authorize URL | client identity | second client | code cross-client | `aud` verified |
| `client_secret` in token request | client credential | leaked secret | exchange possible | not leaked |
| `response_type` in authorize URL | flow shape | `token`/`id_token` | fragment | `400` or code-only |
| `response_mode` in authorize URL | delivery mode | `form_post`/`web_message` | delivered | `400` or query-only |
| `prompt` in authorize URL | consent behavior | `none` | silent re-auth | `400` |
| `max_age` in authorize URL | re-auth window | stale session | accepted | `400` |
| `login_hint` in authorize URL | prefilled username | reflected | DOM sink | encoded |
| `id_token_hint` in authorize URL | previous id_token | replay | accepted | `nonce` validated |
| `request`/`request_uri` in authorize URL | JAR request | forged JWT / SSRF URI | accepted / fetched | signature verified / URI allowlisted |
| `claims` in authorize URL | requested claims | broader claims | granted | `400` |
| `resource` in authorize URL | resource indicator | different resource | token for it | `400` |
| `acr_values` in authorize URL | auth level | lower acr | accepted | enforced |
| `aud` in id_token | token audience | different client | accepted | `aud` verified |
| `iss` in id_token | token issuer | different IdP | accepted | `iss` verified |
| `exp` in id_token | token expiry | expired token | accepted | `exp` validated |
| `sub` in id_token | subject identifier | user-controlled | linked | `sub` assigned |
| `email` in id_token | email claim | linking field | linked | `sub` linking |
| `email_verified` in id_token | verification flag | unverified link | linked | `email_verified` enforced |
| `preferred_username` in id_token | username claim | linking field | linked | `sub` linking |
| `groups`/`roles` in id_token | permission claims | broader | granted | `400` |
| `SameSite` on IdP token | cross-site write | text/plain JSON login | Set-Cookie lands | `Lax`/`Strict` |
| `HttpOnly` on IdP token | JS readability | read via JS | readable | `HttpOnly` |
| `Secure` on IdP token | transport | over HTTP | accepted | `Secure` required |
| `Domain` on IdP token | scope | parent domain | shared | app domain |
| `Path` on IdP token | scope | `/` | readable everywhere | restricted |
| `device_code` in token request | device flow | poll faster | token issued | `400` |
| `refresh_token` in token request | refresh artifact | replay | token issued | `400` |
| `logout_token` in backchannel | session teardown | forged JWT | session terminated | signature verified |
| `sid` in logout | session ID | forged sid | wrong session terminated | `sid` validated |

## The mechanism map

| Mechanism | Artifacts | The probe |
|---|---|---|
| state CSRF | `state` in authorize + callback | cross-session replay |
| redirect interception | `redirect_uri` in authorize | authorize with wrong URI |
| code interception | `code` in callback + `redirect_uri` loose | replay stolen code |
| cookie swap | `SameSite` on IdP token + `loginSSO` ignores credentials | text/plain JSON login |
| account linking | `email`/`username`/`sub` in id_token | pre-registration race |
| implicit leak | `response_type` + `access_token` in fragment | coerce to implicit |
| PKCE bypass | `code_challenge` + `code_verifier` | wrong verifier |
| cross-client | `client_id` + `aud` in id_token | exchange as different client |
| scope escalation | `scope` in authorize + token | broader scope |
| registration race | `email`/`username` in registration | pre-register the target |
| device flow | `device_code` + `user_code` | poll faster |
| refresh replay | `refresh_token` in token request | replay the refresh token |
| logout forge | `logout_token`/`sid` in backchannel | forged JWT |
