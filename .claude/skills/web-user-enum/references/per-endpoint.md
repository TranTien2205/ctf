# Per-endpoint — the account-touching endpoint matrix

| Endpoint | Method | Body | Oracle | Route |
|---|---|---|---|---|
| `/login` `/signin` `/auth` | POST | `user=&pass=` | text/status/timing/side | `login-enum.md` |
| `/api/login` `/api/auth` | POST | `{"username":...}` | JSON error-code/boolean | `api-enum.md` |
| `/api/token` `/oauth/token` | POST | `grant_type=password&...` | `invalid_grant` vs typed | `api-enum.md` |
| `/register` `/signup` | POST | `user=&email=&pass=` | "taken"/`409`/timing | `register-reset-enum.md` |
| `/check-username` `/available` | GET | `?u=`/`?name=` | `{"available":...}` direct | `form-surface.md` |
| `/forgot-password` `/reset` | POST | `email=` | send/timing/field | `register-reset-enum.md` |
| `/forgot-username` | POST | `email=`/`user=` | "emailed"/timing | `register-reset-enum.md` |
| `/unlock` `/reactivate` | POST | `user=`/`email=` | "unlocked"/"no locked" | `register-reset-enum.md` |
| `/invite` `/contact` | POST | `email=` | "already a member" | `form-surface.md` |
| `/mfa` `/2fa` `/send-otp` | POST | `user=`/`email=` | "code sent"/timing | `form-surface.md` |
| `/api/users/{id\|name}` | GET | — | `200`/`404` + `web-idor` | `api-enum.md` |
| `/graphql` | POST | `{"query":...}` | typed `errors[].code` | `api-enum.md` |

## The endpoint coverage rule

Probe EVERY endpoint in the table that exists — the cheapest-leak order
is check-username > register > reset > login > mfa > api. A uniform
`/login` is one row; the rest are unmeasured until probed.

## The endpoint-alias check

`/login`, `/login/`, `/api/login`, `/api/v1/login`, `/auth`,
`/api/auth`, `/signin`, `/session`, `/token`, `/oauth/token` — the same
logic under different routes; probe each alias (a limit/oracle may
exist on one route but not its alias).
