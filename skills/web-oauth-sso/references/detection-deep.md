# Detection deep — the full artifact inventory

The detection module names the walk and the inventory. This module carries
the full artifact inventory — every parameter, cookie, endpoint, and claim
that carries the attack surface.

## The authorize-request inventory

Every parameter in the `authorize` URL is a testable surface:

| Parameter | The surface | The check |
|---|---|---|
| `client_id` | the registered client | enumerate — sequential? predictable? |
| `redirect_uri` | the code delivery target | exact match? prefix? wildcard? |
| `response_type` | the flow shape | `code` only? `token`? `id_token`? hybrid? |
| `scope` | the permissions | broader than requested? `offline_access`? |
| `state` | the CSRF binding | bound to session? single-use? predictable? |
| `nonce` | the replay binding | present? validated? |
| `code_challenge` | the PKCE binding | required? `S256` or `plain`? |
| `code_challenge_method` | the PKCE method | `S256` enforced? `plain` accepted? |
| `prompt` | the consent behavior | `none` → silent re-auth; `consent` → forced |
| `max_age` | the re-auth window | required? enforced? |
| `login_hint` | the prefilled username | reflected? injectable? |
| `id_token_hint` | a previous `id_token` | replayable? |
| `request`/`request_uri` | a JWT carrying the whole request | signature verified? URI SSRF-able? |
| `response_mode` | the delivery mode | `query`? `fragment`? `form_post`? `web_message`? |
| `claims` | the requested claims | a `claims` parameter names specific claims |
| `aud` | the token audience | present? validated? |
| `resource` | the resource indicator (RFC 8707) | a resource URI the token is for |

## The callback-request inventory

Every parameter in the `callback` URL is a testable surface:

| Parameter | The surface | The check |
|---|---|---|
| `code` | the authorization code | bound to `client_id`? `redirect_uri`? `state`? single-use? expiry? |
| `state` | the CSRF binding | echoed back? validated? bound to session? |
| `error` | the error response | `access_denied`? `invalid_request`? |
| `error_description` | the error detail | reflected? injectable? |
| `iss` | the issuer | present? validated? |

## The token-request inventory

Every parameter in the `token` request is a testable surface:

| Parameter | The surface | The check |
|---|---|---|
| `grant_type` | the grant shape | `authorization_code`? `refresh_token`? `client_credentials`? `password`? `device_code`? |
| `code` | the authorization code | re-validated? bound to `client_id`? `redirect_uri`? `code_verifier`? |
| `client_id` | the client | re-validated? bound to the code? |
| `client_secret` | the client credential | required? in the body? in the header? |
| `redirect_uri` | the code delivery target | re-validated against the authorize step's? |
| `code_verifier` | the PKCE verifier | required? re-validated? |
| `refresh_token` | the refresh artifact | single-use? bound to `client_id`? `scope`? |
| `scope` | the permissions | re-validated? broader than authorize's? |
| `aud` | the token audience | re-validated? |

## The cookie inventory

Every `Set-Cookie` in the transcript is a testable surface:

| Cookie | The surface | The check |
|---|---|---|
| app session | the app's session | `SameSite`? `HttpOnly`? `Secure`? `Domain`? `Path`? |
| IdP token | the delegated identity | `SameSite`? `HttpOnly`? `Secure`? `Domain`? `Path`? |
| `state` cookie | the CSRF binding | `SameSite`? `HttpOnly`? `Secure`? single-use? |
| `nonce` cookie | the replay binding | `SameSite`? `HttpOnly`? `Secure`? single-use? |
| `code_verifier` cookie | the PKCE binding | `SameSite`? `HttpOnly`? `Secure`? |
| `id_token` cookie | the identity token | `SameSite`? `HttpOnly`? `Secure`? |
| `refresh_token` cookie | the refresh artifact | `SameSite`? `HttpOnly`? `Secure`? |

## The endpoint inventory

Every endpoint in the flow is a testable surface:

| Endpoint | The surface | The check |
|---|---|---|
| `/authorize` or `/oauth/authorize` | the IdP entry point | `redirect_uri` variations? `response_type` coercion? `scope` escalation? |
| `/token` or `/oauth/token` | the code exchange | `redirect_uri` re-validated? `code_verifier` re-validated? `client_secret` required? |
| `/callback` or `/oauth/callback` | the app's entry point | `state` validated? `code` bound? |
| `/login` or `/sso/login` | the app's login | credentials ignored? jar's token used? |
| `/register` or `/signup` | the account creation | idempotent? raceable? email allowlisted? |
| `/link` or `/connect` | the account linking | authenticated? `sub`-bound? |
| `/submit-url` or `/visit` | the bot's rendering endpoint | user-supplied URLs? delivery channel? |
| `/userinfo` or `/me` | the identity endpoint | what claims? `email_verified`? `sub`? |
| `/logout` | the session teardown | backchannel? frontchannel? |
| `/introspect` | the token introspection | `active`? `scope`? `aud`? |
| `/revoke` | the token revocation | bound to `client_id`? |
| `/.well-known/openid-configuration` | the discovery document | what endpoints? what algorithms? what claims? |

## The claim inventory

Every claim in the `id_token` or `userinfo` is a testable surface:

| Claim | The surface | The check |
|---|---|---|
| `sub` | the subject identifier | user-controlled? assigned? stable? |
| `iss` | the issuer | validated? |
| `aud` | the audience | validated? single or list? |
| `exp` | the expiry | validated? |
| `iat` | the issued-at | validated? |
| `nbf` | the not-before | validated? |
| `nonce` | the replay binding | validated? |
| `email` | the email claim | the linking field? |
| `email_verified` | the verification flag | enforced? |
| `preferred_username` | the username claim | the linking field? |
| `name` | the display name | reflected? |
| `groups`/`roles` | the permission claims | broader than requested? |
| `scope` | the granted scope | broader than requested? |
| `at_hash`/`c_hash` | the token hash | validated? |

## The discovery-document inventory

`/.well-known/openid-configuration` names the IdP's capabilities — every
field is a testable surface:

| Field | The surface | The check |
|---|---|---|
| `authorization_endpoint` | the authorize URL | the real endpoint? |
| `token_endpoint` | the token URL | the real endpoint? |
| `userinfo_endpoint` | the userinfo URL | the real endpoint? |
| `jwks_uri` | the signing keys | the real keys? |
| `response_types_supported` | the accepted flows | `code` only? `token`? `id_token`? |
| `grant_types_supported` | the accepted grants | `authorization_code`? `refresh_token`? `client_credentials`? `password`? |
| `subject_types_supported` | the `sub` types | `public`? `pairwise`? |
| `id_token_signing_alg_values_supported` | the accepted algorithms | `RS256`? `ES256`? `none`? `HS256`? |
| `scopes_supported` | the accepted scopes | the allowlist? |
| `claims_supported` | the accepted claims | the allowlist? |
| `code_challenge_methods_supported` | the accepted PKCE methods | `S256` only? `plain`? |
