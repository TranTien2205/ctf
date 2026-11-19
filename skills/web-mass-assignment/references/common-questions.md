# Common questions — the mass-assignment FAQ

## "I sent `role:admin` — where did it go?"

Read-back through a DIFFERENT endpoint (`GET /api/me` or the object
detail). The write's own echo shows the parser's view, not the store's.
If the read-back shows `role:"user"` — the binder dropped it (allowlist
falsifier). If `role` is absent entirely — serializer-hidden; exercise
the decision directly.

## "The field stored but `/admin` still `403`s — is it real?"

No — the class bar says a stored-but-inert field is a NULL result. The
gate reads a different field (`is_staff`, `permissions`, a JWT claim).
Find the field the gate ACTUALLY reads: diff a real admin's record,
read the gate's source, or re-login (the bound `role` may land in the
re-issued token).

## "JSON rejects it — is the class dead?"

No — the schema falsifier kills ONE content-type. Try `role=admin`
form-encoded, multipart, `{"profile":{"role":..}}` nested, `PATCH`
instead of `POST`. The form path uses a different parser and possibly
a different allowlist.

## "Which field names should I try?"

The model's REAL fields — from `GET` read-backs, the JS bundle, error
messages, docs. `binding_probe.py`'s default set (`role`, `admin`,
`is_admin`, `isAdmin`, `debug`, `permissions`, `group`, `verified`,
`is_staff`) is the high-frequency shortlist. Probe SEMANTICS
(privilege, verification, economics, plan, ownership, workflow) not
spellings.

## "`role` stores — why doesn't the flag appear?"

The bound field is the EDGE, not the flag. `role:admin` opens `/admin`;
the flag sits behind the admin route, or behind a second action the
role unlocks (`POST /admin/users` — the admin binder's own mass-
assignment writing the flag field). Follow the chain.

## "Is this IDOR?"

Only if the bug is object ACCESS. `PATCH /users/9` reaching another
user's record → IDOR; `{"author_id":9}` forging authorship → mass
assignment; `{"role":"admin"}` on your own record → mass assignment.
The line: ACCESS vs FIELD.

## "Is this prototype pollution?"

No — `__proto__`/`constructor` keys pollute the shared prototype (every
object gains the property); `role` binds on YOUR object. `{}.role`
resolving globally = pollution; `user.role` set on your record = mass
assignment. Different class, different evidence.

## "Do I need 100 field names?"

No — the dictionary covers SEMANTIC space; the high-frequency set
(`role`, `is_admin`, `verified`, `balance`, `permissions`, `groups`,
`plan`, `price`, `discount`) reaches most models. The field inventory
(from `GET`s and the bundle) is the real source.
