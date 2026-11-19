# Carrier shapes — how the extra field is delivered, per transport

The binder binds what the parser delivers — and each transport's parser
has different key semantics. This module enumerates the carriers and
which one reaches which binder.

## JSON body

```json
{"username":"x","password":"p","role":"admin"}
```

- **flat** — the canonical shape. Reaches merge-all binders and
  allowlist binders equally; the allowlist decides.
- **nested**: `{"user":{"role":"admin"}}`, `{"profile":{"role":..}}`,
  `{"billing":{"price":0}}` — reaches deep-merge binders and
  prefix-required models. A top-level allowlist that includes `user`
  passes the nested `role` to the user-model's own (maybe absent)
  allowlist.
- **array**: `{"role":["admin"]}`, `{"groups":["admin","wheel"]}`,
  `{"permissions":["*"]}` — reaches array-typed fields and binders that
  coerce scalar→array.
- **duplicate keys**: `{"role":"user","role":"admin"}` — parsers take
  LAST; a validator reading the first and a binder taking the last is
  the parse-layer two-validator gap.
- **typed**: `{"role":true}` vs `{"role":"admin"}` vs `{"role":1}` —
  type-coercion paths differ per binder; a `String` column takes
  `"admin"`, a boolean takes `true`, an enum takes the enum value.

## Form-encoded body

```
username=x&password=p&role=admin
```

Scalar-only — but the repeated-key semantics matter:

- `role=user&role=admin` — qs-style parsers deliver arrays; last-wins
  parsers deliver `admin`; first-wins `user`. The validator-vs-binder
  disagreement on WHICH element decides.
- `user[role]=admin` — Rails/Laravel/PHP nesting convention reaching
  nested model fields flat keys can't.
- `user.role=admin` — dotted convention (some qs configs, .NET).
- `role[]=admin` — array-form reaching array fields.

## Query string

```
POST /users?role=admin      or      GET /users?role=admin
```

Same parser semantics as form bodies, plus: query params merge into
`params` on many frameworks — a field the body's schema rejects may
bind through the query. `binding_probe.py --method GET` tests this
carrier directly. A `GET` that mutates is itself a second bug (CSRF/
prefetch on a state transition — see web-logic-flaw).

## Content-Type switching

The SAME endpoint often accepts three body types with THREE different
binders:

| Content-Type | Binder | Note |
|---|---|---|
| `application/json` | JSON deserializer (maybe schema-validated) | strict schema lives here usually |
| `application/x-www-form-urlencoded` | form parser → model binder | different allowlist, often none |
| `multipart/form-data` | multipart parser → binder | third code path, least-tested |

The field the JSON schema rejects (`400 unknown property`) may bind
cleanly through the form path — two parsers, two allowlists, same
model. Probe every content-type the endpoint accepts.

## Method permutations

- `POST` — create binder;
- `PATCH` — merge binder (deep-merge site, extra fields survive into
  nested objects);
- `PUT` — replace binder (extra fields bind OR the replace wipes
  others — check what got zeroed);
- `_method=PUT`, `X-HTTP-Method-Override` — POST's validation routing
  through PUT's handler.

## Path and header carriers

- `/users/:id` — the object ID in the path; `?role=` params on it.
- `X-Role: admin` — header-reading binders (rare but real in API
  gateways forwarding headers into context objects).

## The carrier-selection rule

For every candidate field, the matrix is `field × carrier ×
content-type × method`. The allowlist lives in ONE cell of that matrix
— a falsifier on `POST /register` JSON says nothing about
`PATCH /users/me` multipart. But don't enumerate the matrix blindly:
the falsifier depth tells you what remains open (see `falsifiers.md`).
A schema rejection kills the content-type; a binder drop kills the
endpoint; a model-level absence kills the semantic everywhere.
