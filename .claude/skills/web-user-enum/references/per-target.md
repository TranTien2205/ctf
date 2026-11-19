# Per-target — the target-type adjustments

## A server-rendered form app

The `POST` form re-renders an HTML error — the body channel is the
first read (raw diff + masked). The status/redirect is second. Timing
is the fallback. Check `data-`, hidden inputs, comments.

## A SPA + JSON API

`POST /api/login` JSON — the body channel is the JSON error-code/boolean
field. Check `{"error"}`, `{"code"}`, `{"reason"}`, `{"exists"}`.
`/api/users/{name}` `200`/`404` — enum + `web-idor`. The SPA's front-end
bundle (`web-source-map`) may name the check-username endpoint.

## A GraphQL app

`POST /graphql` — `userByEmail`/`checkUser`/`login` resolver typed
errors. `{"data":{"userByEmail":null}}` vs an object; a `login`
mutation's `"USER_NOT_FOUND"` vs `"INVALID_CREDENTIALS"` in
`errors[].extensions.code`.

## An OAuth/SSO app

`POST /oauth/token` — `invalid_grant` vs `invalid_client`. A `Sign in
with Google` flow — `account_not_found` on an unlinked email (also
`web-oauth-sso`). A SAML `user@external` vs `user@local` redirect.

## An LDAP-backed app

A `POST` bind attempt — the typed bind error distinguishes
`user_not_found` vs `invalid_credentials` (the `htb-phonebook` analogue).
`ldap_search`/`bind` error text is the oracle.

## A basic-auth app

`Authorization: Basic {U}:x` — a `401` with a `WWW-Authenticate` realm
that differs, or a `403` vs `401`, or a body difference. Rare; the
realm/message is the channel.

## A websocket app

A `ws://` auth frame — a typed `{"type":"auth_error","reason":"no_user"}`
vs `"bad_pass"`. `web-websocket` for the channel protocol.

## An API-gateway/microservice

Multiple auth paths behind the gateway — `/auth/login`, `/users/login`,
`/api/v1/login` — each a separate form; the gateway may add a
`X-RateLimit-Remaining` header that leaks the counter-key.
