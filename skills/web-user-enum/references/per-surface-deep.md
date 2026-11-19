# Per-surface (deep) — each technology surface's full protocol

## HTML-form surface — the full protocol

```bash
# 1. fetch the form — read the fields + CSRF
curl -s "$BASE/login" | grep -oE '<input[^>]*(name|type)[^>]*>'
# 2. fetch a fresh token per request if CSRF-protected
tok=$(curl -sc cj "$BASE/login" | grep -oE 'name="csrf[^"]*" value="[^"]*"' | cut -d'"' -f4)
curl -sb cj -i -X POST -d "user=$KNOWN&pass=x&csrf=$tok" "$BASE/login" > g
tok=$(curl -sc cj "$BASE/login" | grep -oE 'name="csrf[^"]*" value="[^"]*"' | cut -d'"' -f4)
curl -sb cj -i -X POST -d "user=$FAKE&pass=x&csrf=$tok"  "$BASE/login" > b
# 3. the masked diff + the status/redirect + the envelope
```

## JSON-API surface — the full protocol

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"username\":\"$KNOWN\",\"password\":\"x\"}" "$BASE/api/login" > ag
curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"username\":\"$FAKE\",\"password\":\"x\"}"  "$BASE/api/login" > ab
diff ag ab; grep -oE '"(error|code|reason|detail|exists|available|taken|success)":[^,}]*' ag ab
```

The field names ARE the oracle — `error`/`code`/`reason`/`exists`/
`available`/`taken`/`detail`/`attempts_remaining`.

## GraphQL surface — the full protocol

```bash
# the exists-resolver
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"query":"query{userByEmail(email:\"'$KNOWN'\"){id}}"}' "$BASE/graphql"
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"query":"query{userByEmail(email:\"'$FAKE'\"){id}}"}'  "$BASE/graphql"
# the login-mutation typed error
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"query":"mutation{login(username:\"'$U'\",password:\"x\"){token}}"}' "$BASE/graphql"
```

`{"data":{"userByEmail":null}}` vs a real object; a
`errors[].extensions.code` of `USER_NOT_FOUND` vs `INVALID_CREDENTIALS`.

## REST user-resource — the protocol

```bash
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/users/$KNOWN"
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/users/$FAKE"
# 200 vs 404 — enum + web-idor; a 200's body feeds the read
```

## Basic-auth surface

```bash
curl -s -u "$KNOWN:x" "$BASE/protected" -D - | grep -iE 'http|www-authenticate'
curl -s -u "$FAKE:x"  "$BASE/protected" -D - | grep -iE 'http|www-authenticate'
```

A `401` with a differing `WWW-Authenticate` realm/message, or a `403`
vs `401`, or a body difference.

## The surface-to-channel note

Every surface carries every channel — the surface is the *transport*;
the channel is the *measurement*. A SPA can leak on timing just as a
form can; the four-channel measurement is transport-agnostic.
