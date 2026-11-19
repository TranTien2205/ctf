# Per-vector — each request vector's note

## The field vectors

| Vector field | The shape | Note |
|---|---|---|
| `user`/`username`/`name` | `user={U}` | the common slot |
| `email` | `email={U}` | a registration/reset slot — `{U}` may be `a@b.c` |
| `login`/`account`/`uid`/`handle` | `login={U}`/`uid={U}` | app-specific names |
| `phone`/`mobile` | `phone={U}` | SMS-OTP flows enumerate by number |
| `identifier`/`sub`/`principal` | `identifier={U}` | OIDC/SAML-shaped |
| JSON `username`/`email`/`login` | `{"username":"{U}"}` | the SPA/API slot |
| GraphQL arg | `login(user:"{U}")`/`userByEmail(email:"{U}")` | a typed resolver |

## The format vectors

- bare `admin` vs `admin@corp.com` — the app may expect one format; probe
  both, a `404` on the wrong format is a format, not an oracle
- `admin` vs `ADMIN` vs `Admin` — case normalization; a case-insensitive
  lookup treats them as one
- `corp\admin` vs `admin` — a domain prefix
- `admin` vs ` admin`/`admin ` — whitespace normalization

## The transport vectors

- `POST` form body — the default
- `POST` JSON body — the API slot
- `GET` query `?user=` — a check/REST endpoint
- `Authorization: Basic {U}:x` — a basic-auth oracle
- `ws://` auth frame — `web-websocket`
- GraphQL `{"query":"mutation{login(user:\"{U}\"...)}"}`

## The vector-to-oracle note

The oracle is the *pair*, not the vector — every vector is just how the
`{U}` is delivered. The measurement is identical: known-good vs known-bad
vs repeated-bad on the same channel, whatever the transport.
