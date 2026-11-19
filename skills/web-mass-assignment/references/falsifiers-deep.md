# Falsifiers deep — the depth-annotated kill map

## The five depths

```
depth 1 — content-type:    schema rejection kills one parser
depth 2 — endpoint:        allowlist drop kills one binder
depth 3 — binder-family:   drop on all carriers kills all binders
depth 4 — model:           no privileged fields kills the class
depth 5 — semantic:        stored-but-inert kills the field, not the class
```

Each depth closes different cells and leaves different ones open.

## Depth 1 — the schema falsifier

`400 "unknown property: role"`, `422 "additional properties not
allowed"`, `TypeError: unexpected keyword 'role'`.

- **Kills**: extra fields via that content-type on that endpoint.
- **Open**: form/multipart carrier (different parser); `PATCH`/`PUT`
  (different binder); nested under allowed parents; GraphQL (different
  schema layer).
- **The leak**: a rejection that NAMES the field is schema disclosure —
  `"role must be one of: user, admin"` confirms `role` exists and is
  an enum. The falsifier leaks the model.

## Depth 2 — the endpoint falsifier

`200`, write completes, read-back shows control state — the binder
silently dropped the extra key. `permit`, `$fillable`, `[Bind]`,
`pick`, `fields=` all produce this.

- **Kills**: flat extra fields on THIS endpoint.
- **Open**: nested under allowed parent (`{"profile":{"role":..}}`
  where `profile` is legit); the update binder (`PATCH`/`PUT` — wider);
  other methods (`POST` → `PATCH`); other endpoints (`/import`).

## Depth 3 — the binder-family falsifier

Drop on JSON, form, multipart, `PATCH`, `PUT`, query — every binder
the model touches is allowlisted.

- **Kills**: the conventional binders.
- **Open**: `/import`/bulk (different code path); `/admin/*` (needs a
  privilege edge); GraphQL mutations (args schema is a separate binder);
  method-override (`?_method=` reaching a different handler).

## Depth 4 — the model falsifier

`GET` responses show no privileged fields on ANY object — the model is
genuinely narrow. `role` lives in a separate `admins` table,
permissions in a join, `balance` in a `wallets` table the user-model
never exposes.

- **Kills**: the class on this app — nothing privileged to bind.
- **Open**: the OTHER models' binders — `POST /wallets` with a bound
  `balance`; `POST /memberships` with a bound `role`.

## Depth 5 — the semantic falsifier (inert field)

`role:"admin"` stores, `/admin` `403`s — the field bound but the gate
reads `is_staff`, `permissions`, a join table, or a JWT claim.

- **Kills**: `role` as a decision-changer.
- **Open**: the field the gate ACTUALLY reads — diff a real admin's
  record, read the gate's source, try the sibling semantic (`is_staff`,
  `permissions`, `groups`).
- **The re-issue edge**: the bound `role` lands in the RE-ISSUED JWT —
  log out and in, re-hit the gate.

## The pair-discipline

Every falsifier needs a CONTROL pair — `role:"user"` on the read-back
is the falsifier only because the control also showed `role:"user"`.
A canary-only `role:"user"` is ambiguous (maybe `user` IS the default).
Control + canary byte-identical = falsifier; canary > control = bound.

## The near-miss readings

- **echo-only**: write echoes `admin`, read-back `user` — echo
  artifact, the field dropped. Endpoint falsifier.
- **type-error**: `role:true` dropped, `role:"admin"` binds — type
  falsifier isn't the field's; one right-type retry.
- **cache**: `role:"user"` from a stale view — re-GET fresh.

## The depth-annotated record

```
POST /register  json/flat     → endpoint falsifier (allowlist drop)
POST /register  form/flat     → endpoint falsifier (same)
PATCH /me       json/flat     → UNTESTED  ← next cell
PATCH /me       json/nested   → UNTESTED
```

The map says which cells are dead and which are live — the next session
resumes at a live cell, not a dead one.
