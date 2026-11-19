# Detection surface — the OAuth artifacts that name the mechanism

Every artifact in the OAuth transcript names a mechanism. This module is the
surface map — find the artifact, name the mechanism, run the probe.

## The artifact surface

| Artifact | Where it lives | The mechanism it names |
|---|---|---|
| `state` in authorize URL | `Location` header on `GET /login` | CSRF binding |
| `state` in callback URL | `Location` header on `GET /callback` | CSRF binding |
| `redirect_uri` in authorize URL | `Location` header on `GET /login` | code delivery target |
| `code` in callback URL | `Location` header on `GET /callback` | replay surface |
| `code` in fragment | `Location` header on `GET /callback` | leak surface |
| `access_token` in fragment | `Location` header on `GET /callback` | leak surface |
| `id_token` in fragment | `Location` header on `GET /callback` | leak surface |
| `nonce` in authorize URL | `Location` header on `GET /login` | replay binding |
| `scope` in authorize URL | `Location` header on `GET /login` | permission surface |
| `code_challenge` in authorize URL | `Location` header on `GET /login` | PKCE binding |
| `code_challenge_method` in authorize URL | `Location` header on `GET /login` | PKCE method |
| `code_verifier` in token request | `POST /token` body | PKCE verifier |
| `client_id` in authorize URL | `Location` header on `GET /login` | client identity |
| `client_secret` in token request | `POST /token` body | client credential |
| `response_type` in authorize URL | `Location` header on `GET /login` | flow shape |
| `response_mode` in authorize URL | `Location` header on `GET /login` | delivery mode |
| `prompt` in authorize URL | `Location` header on `GET /login` | consent behavior |
| `max_age` in authorize URL | `Location` header on `GET /login` | re-auth window |
| `login_hint` in authorize URL | `Location` header on `GET /login` | prefilled username |
| `id_token_hint` in authorize URL | `Location` header on `GET /login` | previous `id_token` |
| `request`/`request_uri` in authorize URL | `Location` header on `GET /login` | JAR request |
| `claims` in authorize URL | `Location` header on `GET /login` | requested claims |
| `resource` in authorize URL | `Location` header on `GET /login` | resource indicator |
| `acr_values` in authorize URL | `Location` header on `GET /login` | auth level |
| `aud` in `id_token` | `id_token` JWT claim | token audience |
| `iss` in `id_token` | `id_token` JWT claim | token issuer |
| `exp` in `id_token` | `id_token` JWT claim | token expiry |
| `sub` in `id_token` | `id_token` JWT claim | subject identifier |
| `email` in `id_token` | `id_token` JWT claim | email claim |
| `email_verified` in `id_token` | `id_token` JWT claim | verification flag |
| `preferred_username` in `id_token` | `id_token` JWT claim | username claim |
| `groups`/`roles` in `id_token` | `id_token` JWT claim | permission claims |
| `SameSite` on IdP token | `Set-Cookie` header | cross-site write |
| `HttpOnly` on IdP token | `Set-Cookie` header | JS readability |
| `Secure` on IdP token | `Set-Cookie` header | transport |
| `Domain` on IdP token | `Set-Cookie` header | scope |
| `Path` on IdP token | `Set-Cookie` header | scope |
| `device_code` in token request | `POST /token` body | device flow |
| `refresh_token` in token request | `POST /token` body | refresh artifact |
| `logout_token` in backchannel | `POST /logout` body | session teardown |
| `sid` in logout | `POST /logout` body | session ID |

## The mechanism surface

| Mechanism | The artifact | The probe |
|---|---|---|
| state CSRF | `state` in authorize + callback | cross-session replay |
| redirect interception | `redirect_uri` in authorize | authorize with wrong URI |
| code interception | `code` in callback + `redirect_uri` loose | replay stolen code |
| cookie swap | `SameSite` on IdP token + `loginSSO` ignores credentials | text/plain JSON login |
| account linking | `email`/`username`/`sub` in `id_token` | pre-registration race |
| implicit leak | `response_type` + `access_token` in fragment | coerce to implicit |
| PKCE bypass | `code_challenge` + `code_verifier` | wrong verifier |
| cross-client | `client_id` + `aud` in `id_token` | exchange as different client |
| scope escalation | `scope` in authorize + token | broader scope |
| registration race | `email`/`username` in registration | pre-register the target |
| device flow | `device_code` + `user_code` | poll faster |
| refresh replay | `refresh_token` in token request | replay the refresh token |
| logout forge | `logout_token`/`sid` in backchannel | forged JWT |

## The cookie surface

| Cookie | The mechanism | The probe |
|---|---|---|
| app `session` | session issuance | `GET /dashboard` — is the session valid? |
| IdP `token`/`sso`/`auth` | token issuance | `GET /userinfo` — is the token valid? |
| IdP `refresh_token` | refresh artifact | `POST /token` — is the refresh token valid? |
| IdP `device_code` | device flow | `POST /token` — is the device code valid? |
| IdP `state` | CSRF binding | `GET /callback` — is the state bound? |
| IdP `nonce` | replay binding | `GET /callback` — is the nonce bound? |
| IdP `code_verifier` | PKCE verifier | `POST /token` — is the verifier re-validated? |
