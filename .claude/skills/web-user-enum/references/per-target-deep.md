# Per-target (deep) — the full target-type adjustments

## A monolithic server-rendered app

The `POST` form re-renders the page with an error — the body channel
(raw diff + masked) is first, the status/redirect second. A server-side
template (`{% if error %}`) may carry a `data-`/class/comment residual.
Timing is the fallback — the app's `verify()` runs on the same request.

## A SPA + JSON API

`POST /api/login` JSON — the body channel is a `{"error"}`/`{"code"}`/
`{"exists"}` field. The bundle (`web-source-map`) names the check-
username/reset/reset-token endpoints. `/api/users/{name}` `200`/`404` —
enum + `web-idor`. The API may hash only real users → a timing oracle.

## A GraphQL backend

`POST /graphql` — `userByEmail`/`checkUser`/`userExists`/`login`
resolvers. `{"data":{"userByEmail":null}}` vs `{id:N}`; a `login`
mutation's `errors[].extensions.code` `"USER_NOT_FOUND"` vs
`"INVALID_CREDENTIALS"`. Introspection reveals the resolvers. The
strongest direct oracle when the schema exposes it.

## An OAuth/SSO-backed app

`POST /oauth/token` — `invalid_grant` vs `invalid_client`; a `Sign in
with X` flow returns `account_not_found` on an unlinked email (also
`web-oauth-sso` for the pre-hijack). A SAML `user@external` vs
`user@local` redirect leaks the directory.

## An LDAP/AD-backed app

A `POST` bind — the typed bind error distinguishes `user_not_found` vs
`invalid_credentials` (the `htb-phonebook` shape). An LDAP-injection
payload in the username is `web-sqli`-family, not this class — the
existence differential on a normal name is this class.

## A basic-auth app

`Authorization: Basic {U}:x` — a `401` with a differing
`WWW-Authenticate` realm/message, a `403` vs `401`, or a body
difference. Rare — the realm/message is the channel.

## A websocket/realtime app

A `ws://` auth frame — `{"type":"auth_error","reason":"no_user"}` vs
`"bad_pass"` — a typed-frame oracle. `web-websocket` for the channel.

## A microservice/gateway app

Multiple auth paths behind a gateway — `/auth/login`, `/users/login`,
`/api/v1/login` — each a separate form. A gateway `X-RateLimit-Remaining`
header reveals the counter-key; a per-service limiter leaves a route-
gap the alias bypasses.

## A cached/CDN-fronted app

A cached login response busts the timing oracle and may cache the body
— vary a throwaway param to bust the cache, or the cache invalidates
the measurement.
