# Common questions deep — the mass-assignment FAQ, extended

## "I sent `role:admin` — why is nothing in the response?"

The write's own response (the echo) shows the parser's view — it may
not reflect what STORED. Read back through a DIFFERENT endpoint:

```bash
curl -b "$JAR" "$BASE/api/me"     # the store's truth
```

Three outcomes: `role:"admin"` (stored — exercise the gate), `role:
"user"` (binder dropped it — allowlist falsifier), `role` absent
(serializer-hidden — exercise the decision directly).

## "The field stored — why does `/admin` still `403`?"

The gate reads a DIFFERENT field: `is_staff`, `permissions`, a join
table, a JWT claim minted at login. Find the gate's real field:

- `GET /api/users/<admin_id>` — diff a real admin's record vs yours;
- the gate's source — `check_admin()`, `is_staff`, `permissions.
  includes('admin')`, `admin_users` table;
- re-login — the bound `role` may land in the re-issued JWT.

The stored-but-inert field is a null result, not a finding.

## "JSON `400`s — is the class dead?"

No — the schema falsifier kills ONE content-type. The form path uses
a different parser:

```bash
curl -X PATCH "$BASE/users/me" -d 'role=admin' -b "$JAR"         # form
curl -X PATCH "$BASE/users/me" -F 'role=admin' -b "$JAR"         # multipart
curl -X PATCH "$BASE/users/me" -d '{"profile":{"role":"admin"}}' -b "$JAR"
```

The same model bound through a different carrier may accept the field.

## "Which fields do I try first?"

The model's REAL fields — from `GET` read-backs (`jq 'keys'`), the
JS bundle, error messages, docs. The high-frequency shortlist:
`role`, `is_admin`, `isAdmin`, `is_staff`, `verified`, `is_active`,
`balance`, `credits`, `price`, `discount`, `plan`, `tier`,
`permissions`, `groups`, `roles`. Probe the SEMANTIC (privilege,
verification, economics, plan, ownership, workflow) not spellings.

## "Is this the same as IDOR?"

No — the line is ACCESS vs FIELD:

- `PATCH /users/9` on another's record → IDOR (access violation);
- `{"role":"admin"}` on YOUR record → mass assignment (bound field);
- `{"author_id":9}` forging authorship → mass assignment;
- `?user_id=9` reading another's → IDOR.

## "Is this prototype pollution?"

No — `__proto__`/`constructor` keys write on the SHARED prototype
(every object gains the property); `role` writes on YOUR object.
`{}.role` resolving globally = pollution (`web-prototype-pollution`);
`user.role` set on your record = mass assignment.

## "Why did `groups:"admin"` `500`?"

Type coercion — `groups` is an array field; `"admin"` (scalar) crashes
the binder. The right-typed variant: `groups:["admin"]` or
`groups:[{"id":1}]` (FK array). The `500` says the binder TRIED —
the type was wrong.

## "Do I need the whole dictionary?"

No — the dictionary covers SEMANTIC space. `binding_probe.py`'s
default set is the high-frequency shortlist; the field inventory from
`GET`s and the bundle is the real source. Probe semantics (privilege,
verify, econ, plan, ownership, workflow, internals) — each semantic
needs the right field name, not all spellings.
