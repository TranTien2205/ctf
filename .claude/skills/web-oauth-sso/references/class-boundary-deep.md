# Class boundary deep — where web-oauth-sso ends and the sibling classes begin

The class-boundary module names the edges. This module carries the full
mechanics — when to reclassify to `web-auth-session`, `web-open-redirect`,
`web-csrf`, `web-race-condition`, or `web-logic-flaw`.

## The boundary map

| Sibling class | The overlap | The discriminator |
|---|---|---|
| `web-auth-session` | session issuance, token handling | the session is issued by the app; the OAuth flow is the delegation mechanism |
| `web-open-redirect` | `redirect_uri` validation, `Location` header | the redirect is the sink; the OAuth flow is the mechanism |
| `web-csrf` | `state` not bound, cross-site write | the CSRF is the delivery; the OAuth flow is the mechanism |
| `web-race-condition` | registration race, TOCTOU | the race is the mechanism; the OAuth flow is the target |
| `web-logic-flaw` | business logic, account linking | the logic is the mechanism; the OAuth flow is the target |
| `web-ssrf` | `request_uri`/`request` SSRF | the SSRF is the mechanism; the OAuth flow is the target |
| `web-xss` | `login_hint` reflected, DOM sink | the XSS is the sink; the OAuth flow is the mechanism |

## Boundary 1 — `web-auth-session`

`web-auth-session` is the session mechanism — the cookie, the token, the
session issuance. `web-oauth-sso` is the delegation mechanism — the IdP
that issues the token, the app that trusts it.

The discriminator: does the challenge name an IdP, an `authorize` endpoint,
a `callback` endpoint, or an `id_token`? If yes, it is `web-oauth-sso`. If
the session is issued locally — a `session` cookie, a `token` cookie, a
`JWT` signed by the app — it is `web-auth-session`.

## Boundary 2 — `web-open-redirect`

`web-open-redirect` is the redirect sink — the `Location` header that
delivers the user to an attacker URI. `web-oauth-sso` is the flow — the
`authorize` → `callback` → `token` sequence.

The discriminator: does the challenge name an `authorize` endpoint, a
`callback` endpoint, or an `id_token`? If yes, it is `web-oauth-sso`. If the
redirect is the sink — a `?next=`, a `?return=`, a `?redirect=` — it is
`web-open-redirect`.

## Boundary 3 — `web-csrf`

`web-csrf` is the cross-site delivery — the form that POSTs to the app's
endpoint. `web-oauth-sso` is the flow — the `state` that binds the authorize
to the callback.

The discriminator: does the challenge name an `authorize` endpoint, a
`callback` endpoint, or an `id_token`? If yes, it is `web-oauth-sso`. If the
CSRF is the delivery — a `POST` to a state-changing endpoint without a
`state` binding — it is `web-csrf`.

## Boundary 4 — `web-race-condition`

`web-race-condition` is the TOCTOU — the check-then-act window between the
registration check and the registration write. `web-oauth-sso` is the flow —
the account linking that lands on the pre-registered account.

The discriminator: does the challenge name an `authorize` endpoint, a
`callback` endpoint, or an `id_token`? If yes, it is `web-oauth-sso`. If the
race is the mechanism — a `check` then a `write` on the same object — it is
`web-race-condition`.

## Boundary 5 — `web-logic-flaw`

`web-logic-flaw` is the business logic — the rule that is violated by a
valid-looking request. `web-oauth-sso` is the flow — the delegation that
trusts the IdP's identity.

The discriminator: does the challenge name an `authorize` endpoint, a
`callback` endpoint, or an `id_token`? If yes, it is `web-oauth-sso`. If the
logic is the mechanism — a `price` that is negative, a `quantity` that is
zero, a `role` that is `admin` — it is `web-logic-flaw`.

## Boundary 6 — `web-ssrf`

`web-ssrf` is the server-side fetch — the `request_uri` that is fetched by
the IdP. `web-oauth-sso` is the flow — the `request`/`request_uri` that is
fetched by the IdP's `authorize` endpoint.

The discriminator: does the challenge name an `authorize` endpoint, a
`callback` endpoint, or an `id_token`? If yes, it is `web-oauth-sso`. If the
SSRF is the mechanism — a `?url=`, a `?callback=`, a `?fetch=` — it is
`web-ssrf`.

## Boundary 7 — `web-xss`

`web-xss` is the DOM sink — the `login_hint` that is reflected in the
authorize page. `web-oauth-sso` is the flow — the `login_hint` that is
reflected in the authorize page.

The discriminator: does the challenge name an `authorize` endpoint, a
`callback` endpoint, or an `id_token`? If yes, it is `web-oauth-sso`. If the
XSS is the sink — a `?q=`, a `?search=`, a `?name=` — it is `web-xss`.

## The reclassification table

| The observation | The reclassification |
|---|---|
| The session is issued locally — a `session` cookie, a `token` cookie, a `JWT` signed by the app | `web-auth-session` |
| The redirect is the sink — a `?next=`, a `?return=`, a `?redirect=` | `web-open-redirect` |
| The CSRF is the delivery — a `POST` to a state-changing endpoint without a `state` binding | `web-csrf` |
| The race is the mechanism — a `check` then a `write` on the same object | `web-race-condition` |
| The logic is the mechanism — a `price` that is negative, a `quantity` that is zero, a `role` that is `admin` | `web-logic-flaw` |
| The SSRF is the mechanism — a `?url=`, a `?callback=`, a `?fetch=` | `web-ssrf` |
| The XSS is the sink — a `?q=`, a `?search=`, a `?name=` | `web-xss` |
