# Glossary — the OAuth/SSO vocabulary

## The actors

| Term | The meaning |
|---|---|
| **IdP** | Identity Provider — the server that authenticates the user and issues the token |
| **RP** | Relying Party — the app that trusts the IdP's token |
| **Client** | the app that requests the authorization — the RP |
| **Resource Owner** | the user — the owner of the identity |
| **User-Agent** | the browser — the vehicle that carries the redirects |
| **Authorization Server** | the IdP — the server that issues the code and the token |
| **Resource Server** | the API — the server that accepts the token |

## The artifacts

| Term | The meaning |
|---|---|
| `authorize` | the endpoint that starts the flow — `GET /authorize?client_id=...&redirect_uri=...&response_type=...&state=...` |
| `callback` | the endpoint that receives the code — `GET /callback?code=...&state=...` |
| `token` | the endpoint that exchanges the code — `POST /token {grant_type=authorization_code, code=..., client_id=..., client_secret=..., redirect_uri=...}` |
| `code` | the authorization code — a short-lived, single-use artifact minted by the IdP |
| `access_token` | the bearer token — the artifact that authorizes API calls |
| `refresh_token` | the refresh artifact — a long-lived token that issues new `access_token`s |
| `id_token` | the OIDC JWT — the artifact that carries the identity (`sub`, `email`, `nonce`, `aud`, `iss`, `exp`) |
| `state` | the CSRF binding — the random value that binds the authorize to the callback |
| `nonce` | the replay binding — the random value that binds the `id_token` to the request |
| `redirect_uri` | the delivery target — the URI the code is delivered to |
| `client_id` | the client identity — the registered app's identifier |
| `client_secret` | the client credential — the registered app's secret |
| `scope` | the permissions — the claims the token carries (`openid`, `profile`, `email`, `admin`, `offline_access`) |
| `code_challenge` | the PKCE binding — the SHA256 of the `code_verifier` |
| `code_challenge_method` | the PKCE method — `S256` (hashed) or `plain` (clear) |
| `code_verifier` | the PKCE verifier — the random value the `code_challenge` is derived from |
| `response_type` | the flow shape — `code`, `token`, `id_token`, `code token`, `code id_token`, `token id_token`, `code token id_token` |
| `response_mode` | the delivery mode — `query`, `fragment`, `form_post`, `web_message` |
| `prompt` | the consent behavior — `none`, `login`, `consent`, `select_account` |
| `max_age` | the re-auth window — the maximum age of the session |
| `login_hint` | the prefilled username — the username the authorize page pre-fills |
| `id_token_hint` | a previous `id_token` — the `id_token` the authorize request carries |
| `request` | a JWT carrying the request — the JAR (JWT Authorization Request) |
| `request_uri` | a URI carrying the request — the URI the IdP fetches the JAR from |
| `claims` | the requested claims — the `id_token` claims the app requests |
| `resource` | the resource indicator — the API the token is for |
| `acr_values` | the auth level — the authentication context class reference |
| `aud` | the token audience — the `id_token` claim naming the client |
| `iss` | the token issuer — the `id_token` claim naming the IdP |
| `exp` | the token expiry — the `id_token` claim naming the expiry |
| `sub` | the subject identifier — the `id_token` claim naming the user |
| `email` | the email claim — the `id_token` claim naming the email |
| `email_verified` | the verification flag — the `id_token` claim naming whether the email is verified |
| `preferred_username` | the username claim — the `id_token` claim naming the username |
| `groups`/`roles` | the permission claims — the `id_token` claims naming the permissions |
| `device_code` | the device flow code — the code the device polls |
| `user_code` | the user code — the code the user enters |
| `logout_token` | the logout JWT — the backchannel logout artifact |
| `sid` | the session ID — the logout claim naming the session |

## The cookie attributes

| Term | The meaning |
|---|---|
| `SameSite` | the cross-site write control — `Lax` (top-level GETs), `Strict` (no cross-site), `None` (all cross-site), missing (all cross-site) |
| `HttpOnly` | the JS readability control — missing → readable by `document.cookie` |
| `Secure` | the transport control — missing → over plain HTTP |
| `Domain` | the scope control — the cookie's domain |
| `Path` | the scope control — the cookie's path |
| `Max-Age`/`Expires` | the lifetime control — the cookie's expiry |

## The mechanisms

| Term | The meaning |
|---|---|
| **state CSRF** | `state` not bound to session — the code is replayable against a different session |
| **redirect interception** | `redirect_uri` not validated — the code is delivered to an attacker URI |
| **cookie swap** | `SameSite` missing or `None` + `loginSSO` ignores credentials — a cross-site write overwrites the token |
| **account linking** | linking on `email`/`username` — the pre-registration race lands on the attacker's account |
| **implicit leak** | `response_type` not allowlisted — the token is in the fragment |
| **PKCE bypass** | `code_challenge` not required or `code_verifier` not re-validated — a stolen code is exchangeable |
| **cross-client** | `client_id` not bound to the code or `aud` not verified — a code minted for one client works on another |
| **scope escalation** | `scope` not allowlisted — the token carries broader permissions |
| **registration race** | registration not idempotent — the attacker pre-registers the bot's account |
| **device flow** | `device_code` polling — the attacker polls faster than the device |
| **refresh replay** | `refresh_token` not bound — a stolen refresh token is replayable |
| **logout forge** | `logout_token` signature not verified — a forged logout terminates a session |
