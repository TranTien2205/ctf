# Edge cases (map) — the boundary behaviors, indexed

## The account-state oracles

| State | The leak | The channel |
|---|---|---|
| locked | `"account is locked"` vs `"invalid"` — a real row has a state | body/state |
| pending/unverified | `"please verify your email"` — a real row, not yet active | body/state |
| disabled/banned | `"account disabled"` — a real row, deactivated | body/state |
| expired | `"password expired"` — a real row's state | body/state |
| deleted | `"account deleted"` or a `404`/`410` | status/body |

The state-message oracle is subtle — a `locked`/`pending`/`disabled`
real account returns a DIFFERENT message than a fake, AND a different
message than a real ACTIVE account. Three states, three messages — a
richer oracle than the binary exists/not.

## The normalization boundary

- `admin`/`Admin`/`ADMIN` — case-insensitive? all hit the same oracle
- ` admin`/`admin ` — whitespace-trimmed? same oracle
- `admin@x.c`/`ADMIN@X.C` — email case-folded? same
- `admin`/`admin@corp.com` — which slot is live? probe both

## The format boundary

- `user` vs `email` — which field the app reads; a `404` on the wrong
  format is a FORMAT error, not a fake-user
- `corp\admin`/`admin.corp`/`a.admin` — a domain/suffix the app parses
- `admin`/`admin\x00`/`admin ` — a terminator/suffix the app strips

## The multi-value boundary

- `user=admin&user=zzz` — which does the app read? `web-parser-diff`
- `user[]=admin` — an array in a scalar slot; a `500`/`crash` or a
  different oracle — `web-parser-diff`/`web-nosqli`
- `{"username":["a","b"]}` — a JSON array; which element?

## The crash boundary

- `user.hash`-on-`None` → `500` — a repeatable crash on the fake arm is
  a differential (a noisy oracle)
- `user`/`user[]`/`{"a":1}` — a type the handler does not expect → `400`/
  `422`/`500` — a parser-gap, not an oracle

## The boundary-oracle boundary

- a `200` for both with a hidden `data-reason` — the residual hunt
- a `302` for both to the same path — the `Location` param hunt
- a `bcrypt` app — the timing oracle; a `sha256` app — sub-jitter
- a fixed-dummy equalized app — the variance oracle

## The transport boundary

- `/login` form-encoded vs `/api/login` JSON — different channels
- `POST` vs `GET` vs `PUT` — a method the limiter/oracle does not count
- a GraphQL `query{userByEmail}` — a resolver that bypasses the form

## The boundary rule

Every boundary is a CELL, not a class — a state/format/normalization/
multi-value/crash boundary is one observable, measured on the three
arms, marked `oracle`/`uniform`. A boundary that produces an
injection-shaped differential routes to the neighbor class.
