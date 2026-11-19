# Per-form — each account-touching form's oracle profile

| Form | Endpoint shape | Most-common leak | File |
|---|---|---|---|
| login | `POST /login` | timing (hash short-circuit) > body > redirect | `login-enum.md` |
| register | `POST /register` | "username/email taken" — often direct text | `register-reset-enum.md` |
| reset/forgot | `POST /forgot-password` | "sent" only for real accounts, or timing | `register-reset-enum.md` |
| check-username | `/check-username`,`/available` | a direct boolean — the strongest oracle | `form-surface.md` |
| forgot-username | `POST /forgot-username` | "emailed" only for real | `register-reset-enum.md` |
| unlock/reactivate | `POST /unlock` | "unlocked" vs "no locked account" | `register-reset-enum.md` |
| invite/contact | `POST /invite` | "already a member" | `form-surface.md` |
| mfa/otp | `POST /mfa`,`/send-otp` | "code sent" only for real | `form-surface.md` |
| api login | `POST /api/login` | JSON error-code/boolean | `api-enum.md` |
| token/oauth | `POST /api/token` | `invalid_grant` vs a different error | `api-enum.md` |
| graphql | `POST /graphql` | `userByEmail`/`checkUser`/`login` typed errors | `api-enum.md` |
| user-resource | `GET /api/users/{id}` | `200` vs `404` — enum + `web-idor` | `api-enum.md` |

## The probe-order rule

The cheapest-leak order across forms: check-username > register > reset >
login > mfa. Probe the direct oracle (check-username) first — if it
exists, the whole class is confirmed in one request.

## The per-form record

Each form gets its own record — `register: text: "taken"` is a separate
finding from `login: timing: +180ms`. A uniform login does NOT close a
leaky register; coverage is per-form.
