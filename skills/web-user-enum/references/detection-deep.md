# Detection (deep) — finding the oracle where it hides

## The full endpoint inventory

Every account-touching endpoint is a candidate oracle:

| Endpoint | What it may leak |
|---|---|
| `POST /login` `/signin` `/auth` | text/status/timing on user+pass |
| `POST /register` `/signup` | "username/email taken" on register |
| `POST /reset` `/forgot` `/forgot-password` | "sent" only for real accounts |
| `POST /forgot-username` | account exists by username |
| `GET/POST /check-username` `/username-available` | direct exists-oracle |
| `POST /api/login` `/api/auth` `/api/token` | JSON boolean/error-code differential |
| `POST /graphql` | a `user(email:)` / `login` resolver leak |
| `POST /contact` `/invite` | "already a member" on invite |
| `POST /mfa` `/2fa` `/otp` | "code sent" only for real accounts |
| `POST /unlock` `/reactivate` | "no locked account" vs a real unlock |

Probe ALL of them — the login is often hardened while the register or
reset leaks. The cheapest-leak ordering: check-username > register >
reset > login > mfa.

## The form-field shape

- `user=`, `username=`, `email=`, `login=`, `account=`, `name=` — the
  username slot; `enum_probe --body '...{U}...'` marks it `{U}`
- the password field is held constant across both arms
- hidden fields (`csrf`, `next`, `redirect`, a honeypot) must be replayed
  identically — a CSRF token that changes per-request can fake a
  differential (grab a fresh one per request, or the pair is unpaired)

## The AJAX/JSON surface

A SPA login posts JSON — `{"username":"x","password":"y"}` to
`/api/login`. The differential is the JSON error body: `{"error":
"user_not_found"}` vs `{"error":"bad_password"}` or a status 404 vs 401.
The body field names ARE the oracle; `enum_probe --body '{"username":
"{U}","password":"x"}'` with `--headers 'Content-Type: application/json'`.

## The GraphQL surface

```graphql
mutation { login(user:"x", pass:"y") { token } }
query { userByEmail(email:"x") { id } }
query { checkUser(username:"x") { exists } }
```

A `userByEmail`/`checkUser` query is a direct oracle — no credential
needed. A `login` mutation returns distinct errors (`USER_NOT_FOUND` vs
`INVALID_PASSWORD`) or a `null` token with a typed error.

## The timing-only detection

When every content channel is uniform, measure elapsed:

```bash
for i in 1 2 3 4 5 6 7 8; do
  for u in KNOWN zzz-NOSUCH; do
    curl -s -o /dev/null -w "$u %{time_total}\n" \
      -X POST -d "user=$u&pass=x" "$BASE/login"
  done
done | sort -k2
```

Alternate good/bad to cancel network drift; compare medians. A bcrypt
gap is 50-300ms — a fast-hash gap is sub-10ms and needs a local-loop
baseline.

## The recognize-matrix

| Signal in the response | First hypothesis |
|---|---|
| text names the account | direct text oracle |
| same text, timing gap | hash short-circuit |
| 302 `/login?e=1` vs `?e=2` | redirect-param oracle |
| `Set-Cookie` on one arm | session-artifact oracle |
| `"error":"user_not_found"` | JSON error-code oracle |
| `{"exists":true}` | direct boolean oracle |
| `429` after N | throttle present — the other half |
