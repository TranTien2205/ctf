# Common mistakes deep — the subtle ways a mass-assignment run fails

## 1. The echo-as-storage confusion

`POST` echoes `{"role":"admin"}` — recorded as stored. The echo is the
parser/binder's view; the store may drop it (Mongoose `strict`, a
serializer allowlist on the RESPONSE side). The only storage evidence
is a `GET` through a different endpoint — the write's own response is
never the store's truth.

## 2. The semantic-vs-spelling mistake

`role`, `isAdmin`, `admin_flag`, `ROLE`, `access_level` — five probes,
one semantic. A model answering `role` answers the privilege semantic;
the falsifier on `role` likely covers `isAdmin` too. The dictionary
covers SEMANTIC space (privilege, verification, economics, plan,
ownership, workflow, internals) — the spellings are coverage within a
semantic, not new hypotheses.

## 3. The single-content-type falsifier

`role` dropped on JSON → "class dead." The form path uses a DIFFERENT
parser and possibly a different binder — `role=admin` form-encoded may
bind cleanly. A `400` on JSON kills the JSON cell; the matrix has five
more carriers.

## 4. The inert-field-as-finding mistake

`role:"admin"` stores, `/admin` still `403` — the gate reads `is_staff`
or a JWT claim minted at login. A stored-but-inert field is a NULL
result (the class bar verbatim). Record it, then find the field the
gate ACTUALLY reads — `is_staff`, `permissions`, a join table, a re-
issued token.

## 5. The PATCH-blind spot

Probing only `POST /register` — the tightest binder. `PATCH /users/me`
is usually the WIDE one (the profile is meant to be editable) — the
register allowlist says nothing about the update allowlist.

## 6. The two-fields-per-request contamination

`{"role":"admin","verified":true}` — which caused the diff? The
attribution rule is ONE extra field per canary. Two fields means the
read-back diff can't be attributed; split into two canaries.

## 7. The cached-read-back falsifier

`GET` returns `role:"user"` — from a cached representation, not the
store. Re-GET with `?cb=<rand>` or read `/api/me` vs `/api/users/:id`
before recording the falsifier.

## 8. The PUT-wipe

`PUT /users/me {"role":"admin"}` — replace semantics zeroed `username`,
the account broke, the probe looks dead. PUT needs the FULL control
body + extras.

## 9. The type-mismatch falsifier

`role:true` `400`s → "role dead." The column is String — `role:"admin"`
may bind where the boolean died. One right-type retry per semantic
before the falsifier.

## 10. The absent-model conclusion

`GET` shows no privileged fields → "model narrow." Check admin/sibling
views, the bundle's JS constructors, the GraphQL schema — the serializer
may hide fields the model carries.

## 11. The wrong-object mistake

`PATCH /users/9` on ANOTHER user's record — the IDOR-adjacent mistake
that's also a rules violation (mutating another's object). Probe your
own `me`/`id` only until the boundary is proven.

## 12. The writeup-payload trap

Copying a writeup's `{"is_admin":true}` onto a challenge whose model
uses `role` — the writeup's field names are ITS schema's, not yours.
The field inventory is per-target; the writeup is a mechanism hint,
not a payload source.
