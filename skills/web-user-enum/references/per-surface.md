# Per-surface — the technology surface and its oracle shape

| Surface | The oracle shape | The note |
|---|---|---|
| server-rendered form | `POST` form body → re-rendered HTML error | diff raw body; the error block differs |
| SPA + JSON API | `POST /api/login` JSON | error-code/boolean field |
| GraphQL | `POST /graphql` | `checkUser`/`userByEmail`/`login` typed errors |
| REST users | `GET /api/users/{id}` | `200`/`404` — enum + `web-idor` |
| OAuth/token | `POST /oauth/token` | `invalid_grant` vs `invalid_client` |
| SSO-backed | a provider redirect | a `redirect_uri`/account-exists leak — `web-oauth-sso` |
| basic-auth | `Authorization: Basic` | `401` vs a `WWW-Authenticate` realm difference |
| LDAP-backed | a bind attempt | `invalid credentials` vs a typed bind error — `htb-phonebook` card |
| websocket | `ws://` auth message | a typed `auth_error` frame — `web-websocket` |

## The surface → the probe

- HTML form → `curl -d 'user={U}&pass=x'`
- JSON → `curl -H 'Content-Type: application/json' -d '{"username":"{U}"...}'`
- GraphQL → `curl -d '{"query":"mutation{login(username:\"{U}\",...)}..."}'`
- REST → `curl /api/users/{U}`
- basic-auth → `curl -u {U}:x`
- ws → a `websocat`/scripted auth-message

## The surface-note: timing is surface-agnostic

The hash-asymmetry timing oracle exists on EVERY surface — the
`verify()` runs wherever a real user authenticates. When content is
uniform, the timing channel is the surface-independent fallback.
