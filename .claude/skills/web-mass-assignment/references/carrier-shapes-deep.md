# Carrier shapes deep — the transport internals per carrier

## The JSON parser's semantics

```json
{"a":1,"a":2}                → last wins ({"a":2})
{"a":{"b":{"c":1}}}          → nested objects — deep-merge sites
{"a":[1,2]}                  → arrays — typed fields
{"a":null}                   → null — may clear fields
{"a":""}                     → empty string — vs null vs omitted
{"a":true}                   → boolean — vs "true" string
{"a":1e6}                    → number — vs "1e6" string
{"user[role]":"admin"}       → literal key — not nested (JSON)
```

Last-wins is the two-validator gap: a filter reading the first `role`,
the binder taking the last. `null` vs `""` vs omitted — three different
states; a null `role` may clear vs bind.

## The form parser's semantics

```
a=1&a=2                      → first-or-last wins (parser-dependent)
a[]=1&a[]=2                  → array
a[b]=1                       → nested {a:{b:1}}
a.b=1                        → dotted nested (some parsers)
user[role]=admin             → Rails/PHP nested
user[role][]=admin           → nested array
```

First-vs-last on `role=user&role=admin` — the parser decides; the
validator-vs-binder disagreement on WHICH element is the gap.

## The qs-style nested forms

```
user[role]=admin                    → {user:{role:"admin"}}
user[profile][role]=admin           → {user:{profile:{role:"admin"}}}
user[role][]=admin                  → {user:{role:["admin"]}}
profile[settings][admin]=true       → {profile:{settings:{admin:true}}}
```

Rails `params.require(:user)` — the `user[...]` prefix is the access
convention; `user[profile_attributes][role]` for nested-association
accepts.

## The dotted convention

```
user.role=admin                     → {user:{role:"admin"}}
profile.settings.admin=true         → {profile:{settings:{admin:true}}}
User.Role=admin                     → .NET case-insensitive
```

qs-style `a.b=1` or .NET's `User.Role` — reaches binders accepting
dotted paths.

## The array convention

```
role[]=admin                        → {role:["admin"]}
roles[]=admin&roles[]=superuser     → {roles:["admin","superuser"]}
groups[][id]=1&groups[][id]=2       → {groups:[{id:1},{id:2}]}
{"roles":["admin"]}                 → JSON array
{"groups":[{"id":1}]}               → JSON array-of-objects
```

Array fields take `[]` forms; FK arrays take `[{"id":..}]` object forms.

## The query-string union

```
POST /users?role=admin    + body {u,p}
GET  /users?role=admin    + no body
```

`params`/`request.values`/`request.query` merge query into the same
binder — a body-schema-rejected field may bind through the query. The
`params` union is the carrier most allowlists forget.

## The multipart convention

```
------boundary
Content-Disposition: form-data; name="user[role]"
admin
------boundary
```

Multipart's parser delivers form-style params — the third parser, the
least-tested carrier. A `role` rejected on JSON and form may bind
through multipart's own path.

## The content-type decision table

| Sent `Content-Type` | Parser | The carrier |
|---|---|---|
| `application/json` | JSON | flat/nested/array/dup-key |
| `application/x-www-form-urlencoded` | form | flat/prefixed/dotted/array |
| `multipart/form-data` | multipart | form-style params |
| `text/plain` | raw | unparsed — or JSON coerced |
| `application/xml` | XML | element-shaped fields |
| `application/graphql` | GraphQL | args schema |
