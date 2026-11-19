# Per-vector deep — each carrier's mechanics and when to use it

## Flat JSON key — the baseline vector

`{"username":"x","role":"admin"}` — the canonical shape. The binder's
allowlist decides. When to use: FIRST probe on every endpoint — the
lowest-cost falsifier. A `200`+drop here is the endpoint falsifier; a
`400` is the schema falsifier.

## Nested JSON object — the tunnel vector

`{"profile":{"role":"admin"}}`, `{"user":{"role":..}}`, `{"settings":
{"admin":..}}`, `{"preferences":{"role":..}}`, `{"billing":{"price":0}}`.

The deep-merge reach — the allowlist covers the PARENT (`profile`,
`settings`, `user`) as a unit; the merge reaches the nested field the
flat allowlist would drop. When to use: SECOND probe after a flat
drop — the allowlist covers flat keys but maybe not the parent's
contents.

**Depth-2**: `{"a":{"b":{"role":..}}}` — recursive merge sites reach
two levels.

## JSON array — the typed vector

`{"roles":["admin"]}`, `{"groups":[{"id":1}]}`, `{"permissions":["*"]}`,
`{"scopes":["admin"]}`.

Scalar-vs-array: `role` filtered by type/schema but `roles` array binds.
FK arrays take `[{"id":1}]` objects where the scalar takes a string.
When to use: after a scalar `role`/`group` falsifier — the model's
TYPE selects the shape.

## Duplicate key — the parser-gap vector

`{"role":"user","role":"admin"}` — JSON parsers take LAST. A validator
reading the first and binder taking the last = the parse-layer two-
validator gap.

Form: `role=user&role=admin` — first-vs-last parser semantics decide
which the binder sees.

## Form-encoded — the second-parser vector

`username=x&password=p&role=admin` — the form path uses a DIFFERENT
parser (and often a different allowlist) than JSON. `role` rejected on
JSON may bind on form.

Prefixed: `user[role]=admin`, `user[role][]=admin`, `user[profile]
[role]=admin` — Rails/PHP/Laravel nesting reaching fields flat keys
can't.

Dotted: `user.role=admin`, `User.Role=admin` — qs-style or .NET
convention.

## Query string — the params-union vector

`POST /users?role=admin` or `GET /users?role=admin` — `params`/
`request.values`/`request.query` merge into the same binder. A body-
schema-rejected field may bind through the query — the union the
allowlist forgot. `binding_probe.py --method GET` tests it.

## Multipart — the third-parser vector

`role=admin` inside `multipart/form-data` — a third parser, least
tested. The field JSON and form reject may bind through multipart's
own code path.

## GraphQL args — the schema-explicit vector

```graphql
mutation{ updateUser(id:9, input:{role:ADMIN, isAdmin:true}) }
```

The args schema IS the binder — `UserInput` types spell every bindable
field. Extra input-object fields are mass assignment in the schema.
Introspection dumps the whole set.

## Method-override — the routing vector

`POST` + `X-HTTP-Method-Override:PUT` or `?_method=PATCH` — POST's
validation routes through PUT's binder. Different allowlists on the
two methods make the override a carrier.

## The carrier-fallback order

```
flat json → nested json → form flat → form prefixed → query →
multipart → array → typed → PUT → override → GraphQL
```

Each falsifier closes a cell; the next carrier is the next cell.
