# Per-framework — how the common IdPs and clients break

Different frameworks implement OAuth differently — the same bug class has a
different shape on each.

## Keycloak

The most common open-source IdP. The surface:

- `redirect_uri` validated against a stored list per client — exact match by
  default, but a `Valid Redirect URIs` field accepts `*` (allow all) or a
  prefix pattern (`https://app/*`).
- `state` is echoed back but not bound to the session by Keycloak itself —
  the client's own binding is the check.
- `scope` is per-client; a `Client Scope` can add claims the app did not
  request.
- `admin` endpoints are on a different realm path — a token for `realm/master`
  should not work on `realm/app`.
- Account linking is on `sub` by default; `email` is available via a
  `User Attribute` mapper but is not the default linking field.

## Auth0

The hosted IdP. The surface:

- `redirect_uri` validated against `Allowed Callback URLs` — exact match,
  but wildcards are allowed in the path (`https://app/callback*`).
- `state` is the client's responsibility — Auth0 does not bind it.
- `scope` is per-API; a token for one API should not work on another.
- `aud` is the API identifier — the app must verify it.
- Account linking is on `sub` (the `user_id` claim); `email` is available
  but `email_verified` is a separate claim the app must check.
- The `password` grant is disabled by default on new tenants — but enabled
  on older ones.

## Okta

The enterprise IdP. The surface:

- `redirect_uri` validated against `Sign-in redirect URIs` — exact match,
  but trailing-slash and path variations are common misconfigurations.
- `state` is the client's responsibility.
- `scope` is per-Authorization Server; a custom AS can add custom scopes.
- `aud` is the Authorization Server's issuer URI — the app must verify it.
- Account linking is on `sub`; `email` is available but `email_verified` is
  not always populated.

## Passport.js (Node.js)

The most common client library. The surface:

- `passport.authenticate('oauth2')` — the strategy's `state` handling is
  the app's responsibility; `passport-oauth2` does not bind `state` to the
  session by default.
- `req.user` is the OAuth profile — the app maps it to a local account;
  the mapping field is the linking surface.
- `req.logIn()` establishes the session — the session cookie is the app's,
  the token cookie is the IdP's.

## Gin + `ShouldBindJSON` (Go)

The SSOS card's stack. The surface:

- `ShouldBindJSON` reads the raw request body as JSON regardless of
  `Content-Type` — the text/plain JSON trick works.
- `gin-contrib/sessions` cookie store — the session cookie is the app's,
  the SSO token cookie is the IdP's.
- The `loginSSO` step may ignore credentials and use the jar's token — the
  parameter-confusion bug.

## Spring Security (Java)

The enterprise client. The surface:

- `oauth2Login()` — the `state` is bound to the session by default
  (`DefaultOAuth2AuthorizationRequestResolver`), but a custom resolver can
  break it.
- `oauth2Client()` — the client-credentials flow; the `client_secret` is in
  the config — a source-disclosure surface.
- `JdbcOAuth2AuthorizedClientService` — the token is stored server-side;
  the binding is on the `principal_name` column.

## Falsifier ordering by framework

| Framework | Cheapest falsifier | The shape it closes |
|---|---|---|
| Keycloak | `redirect_uri` exact match | code interception |
| Auth0 | `state` bound to session | CSRF |
| Okta | `aud` verified | cross-client |
| Passport.js | `state` bound to session | CSRF |
| Gin | `Content-Type: application/json` enforced | cookie swap |
| Spring | `state` bound to session | CSRF |
