# API and GraphQL enumeration — the JSON/typed-error oracles

## The JSON login

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"username":"KNOWN","password":"x"}' "$BASE/api/login" > ag.json
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"username":"zzz-NOSUCH","password":"x"}' "$BASE/api/login" > ab.json
diff ag.json ab.json
```

The JSON differentials:
- `{"error":"user_not_found"}` vs `{"error":"bad_password"}` — direct
- `{"code":1001}` vs `{"code":1002}` — a numeric error code
- `{"message":"..."}` — a message field difference
- `{"success":false,"reason":"no_user"}` — a reason field
- `{"user_exists":false}` — a direct boolean
- `404 {"detail":"not found"}` vs `401 {"detail":"unauthorized"}` —
  a status+body pair

## The token/auth endpoints

`POST /api/token`, `/api/auth`, `/oauth/token`, `/jwt` — a
`grant_type=password` flow; the RFC-6749 error is `invalid_grant` for a
bad password but a `invalid_client`/different error for a bad user — or
a typed sub-error. Check the `error` + `error_description` fields.

## The check endpoints — direct oracles

```bash
curl -s "$BASE/api/user-exists?u=KNOWN"
curl -s "$BASE/api/username-available?u=zzz-NOSUCH"
curl -s "$BASE/api/v1/users/KNOWN"          # a user-resource 404/200
curl -s "$BASE/api/v1/users/zzz-NOSUCH"
```

- `{"exists":true}` / `{"available":false}` — direct
- `200 {user}` vs `404` — a user-resource oracle
- `{"taken":true}` — a taken flag

## GraphQL

```graphql
query { userByEmail(email:"x@x.c") { id } }
query { checkUser(username:"x") { exists } }
mutation { login(username:"x",password:"y") { token } }
```

- `{"data":{"userByEmail":null}}` vs a real object — a direct oracle
- a login mutation error: `"USER_NOT_FOUND"` vs `"INVALID_CREDENTIALS"`
  in `errors[].extensions.code`
- a typed `User`/`AuthError` union exposing the distinction

## The REST user-resource

`GET /api/users/{id|name|email}` — `200 {user}` vs `404` is a direct
exists-oracle and is also `web-idor` territory (the object is owned).
Route the read-through to `web-idor`; record the enum oracle here.

## The timing channel on APIs

The same hash asymmetry applies — measure `time_total` across a JSON
good/bad pair when the body is uniform.
