# Role assignment deep — the privilege-write paths

`role-assignment.md` covers the register-field probe. This module maps
every path by which a privilege field gets written — the register
binder is only one of them.

## The write paths

| Path | The binder | Notes |
|---|---|---|
| `POST /register` | create binder | the canonical probe |
| `PATCH /users/me` | update binder | second allowlist, often wider |
| `PUT /users/:id` | replace binder | full-object replace — `role` binds if not stripped |
| `POST /admin/users` | admin binder | needs an admin edge first — chain order matters |
| `_method=PUT` override | routed binder | POST validation, PUT handler |
| `?role=` on any mutator | query binder | GET-adjacent write paths |
| GraphQL `updateUser` | resolver args | field-level — `role` arg exists? |
| import/seed endpoints | bulk binder | `/import`, `/seed`, `/migrate` |

Each path is a different binder — a falsifier on `POST /register` says
nothing about `PATCH`. The cheap order: register → PATCH → nested →
content-type → method-override.

## The privilege fields — the full dictionary

```
role roles user_role userRole accountType userType
isAdmin is_admin admin isAdminFlag superuser staff
moderator operator internal employee developer debug
permissions permissions[] scopes scope groups groups[]
accessLevel level tier plan subscription entitlement
flags flags[] features featureFlags capabilities
verified isVerified emailVerified confirmed approved
active enabled suspended banned locked
```

## The indirect write paths

Privilege written indirectly — the field the binder accepts isn't
`role`, it's a field `role` derives from:

```js
// isAdmin is computed, not stored — but a stored field feeds it
get isAdmin() { return this.groups.includes('admin'); }
```

`role` rejected but `groups=["admin"]` binds → `isAdmin` derived true.
Probe the derived fields' sources: `groups`, `permissions`, `flags`,
`plan`, `level`, `type`.

## The token-claim paths

Role lives in a JWT claim — different write path entirely:

- registration mints a JWT with `role` from the model → mass-assign
  at register writes the claim's source;
- `POST /token/refresh` re-derives claims — does it re-read the model
  or copy the old claims? copying preserves a stale-privilege claim;
- a `role` claim editable in the token itself → auth-session's
  signature question, not this class's.

## The second-admin / privilege-escalation paths

`role=admin` binds but the app "only has one admin":

- singleton check on `username==admin` — a second object with
  `role:admin` isn't checked;
- the admin check reads `user.role` — your `role` write IS the check's
  input;
- `role` written but a separate `canAdmin()` checks `id==1` — the
  role is cosmetic; the real gate is a different field — probe it.

## The evidence chain

```
1. POST /register {..., "role":"admin"}     → echo (surface)
2. GET /api/user/probe                       → "role":"admin" (class)
3. GET /admin                                → 200 + admin view (impact)
4. GET /admin/flag | /admin/config           → flag field (the sink)
```

Steps 2→4 are the walk — the role is reach, the flag is inside the
role's gated surface.
