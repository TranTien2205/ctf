# Per-vector — every vector the extra field can ride

## Vector: flat JSON key

`{"username":"x","role":"admin"}` — the canonical shape. Reaches merge-
all and allowlist binders equally; the allowlist decides. Probe order:
`role` → `is_admin` → `verified` → `balance` → `permissions` →
`groups` → the dictionary's remaining semantics.

## Vector: nested JSON object

`{"user":{"role":..}}`, `{"profile":{"role":..}}`,
`{"settings":{"admin":..}}` — reaches deep-merge binders and prefix-
required models. The allowlist covers `profile`/`settings` as a unit;
the merge reaches the nested field. Depth-1 and depth-2.

## Vector: array

`{"roles":["admin"]}`, `{"groups":[{"id":1}]}`,
`{"permissions":["*"]}` — reaches array-typed fields and binders that
coerce scalar→array. The scalar-vs-array pair is one semantic, two
probes — `role` filtered but `roles` bound.

## Vector: duplicate key

`{"role":"user","role":"admin"}` — JSON parsers take LAST; a validator
reading the first and binder taking the last is the parse-layer two-
validator gap. Form `role=user&role=admin` — first-vs-last parser
semantics.

## Vector: form-encoded flat

`username=x&password=p&role=admin` — the form path's parser is
different from JSON's; the allowlist may differ. `role` dropped on
JSON may bind on form.

## Vector: form-encoded prefixed

`user[role]=admin`, `user[role][]=admin` — Rails/PHP/Laravel nesting
convention reaching nested model fields flat keys can't. `user[profile]
[role]=admin` for depth-2.

## Vector: dotted

`user.role=admin`, `profile.role=admin` — qs-style dotted convention;
.NET `User.Role` convention. Reaches binders accepting dotted paths.

## Vector: query string

`POST /users?role=admin` or `GET /users?role=admin` — params union
reaches the binder; a body-rejected field may bind through the query.
`binding_probe.py --method GET` tests it.

## Vector: multipart

`role=admin` inside `multipart/form-data` — a third parser, least
tested. The field the JSON and form paths reject may bind through the
multipart binder.

## Vector: GraphQL args

```graphql
mutation{ updateUser(id:9, input:{role:ADMIN}) }
```

The args schema IS the binder; extra input-object fields are mass
assignment in the schema. Introspection dumps every bindable arg.

## Vector: headers

`X-Role: admin` — header-reading binders (API gateways forwarding
headers into context objects). Rare; a last-resort vector.

## Vector: method-override

`POST` + `X-HTTP-Method-Override:PUT` or `?_method=PATCH` — POST's
validation routing through PUT's binder. The override is a vector,
not a method.
