# Per-secret-class — each credential type and its verify

## The session-token class

| Type | Shape | Verify |
|---|---|---|
| JWT | `eyJ..\.[payload]\.[sig]` | decode claims; is it a real session? → `web-auth-session` |
| a session cookie | `session=`, `sid=` value | does it authenticate? |
| an API key | `apiKey`, `X-API-Key` | `Authorization`/`X-API-Key` probe |
| a bearer token | `token`, `auth_token` | `Authorization: Bearer` probe |

## The cloud-key class

| Type | Shape | Verify |
|---|---|---|
| AWS key id | `AKIA[0-9A-Z]{16}` | a scope probe — does it name a role? |
| AWS secret | `aws_secret` assign | pairs with the key id |
| GCP | `AIza[0-9A-Za-z_-]{35}` | a Google API scope probe |
| Azure | a `client_id`/`client_secret`/`tenant` | an Azure auth probe |

## The service-key class

| Type | Shape | Verify |
|---|---|---|
| Stripe | `sk_live_`/`pk_live_`/`rk_live_` | `pk_` is publishable; `sk_`/`rk_` verify |
| GitHub | `ghp_`/`gho_`/`github_pat_` | `api.github.com/user` probe |
| GitLab | `glpat-` | `gitlab.com/api/v4/user` probe |
| Slack | `xox[baprs]-` | `slack.com/api/auth.test` |
| Discord | a webhook URL | a webhook reach probe |

## The private-key class

| Type | Shape | Verify |
|---|---|---|
| RSA/EC private key | `-----BEGIN ... PRIVATE KEY-----` | what does it sign/decrypt? → `web-auth-session`/`file-read` |
| a JWT signing secret | `secret:`/`jwt_secret`/`HS256` key | forge a token → `web-auth-session` |

## The connection-string class

| Type | Shape | Verify |
|---|---|---|
| `postgres://`/`mysql://`/`mongodb://`/`redis://` | a db connection string | an internal target → `web-ssrf`/note |
| `amqp://`/`mssql` | a message/db string | an internal target |

## The internal-host class

| Type | Shape | Verify |
|---|---|---|
| `internal.svc`, `api.internal`, `.local`, `.corp` | an internal host | an SSRF reach target |
| `10.`/`172.16-31`/`192.168`/`localhost`/`127.` | a private IP/host | an SSRF reach target |

## The verify rule per class

| Class | The check | Route |
|---|---|---|
| session/token | authenticates | `web-auth-session` |
| cloud key | scopes a real account | note/`web-auth-session` |
| service key | a live API auth | `web-auth-session` |
| private key | signs/decrypts | `web-auth-session`/`file-read` |
| connection string | internal target | `web-ssrf` |
| internal host | SSRF reach | `web-ssrf` |
| publishable (`pk_`/`NEXT_PUBLIC_`) | meant public | record, not a leak |
