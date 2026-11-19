# Falsifier map — the kill-map format for the whole class

## The live/dead cell matrix

```
endpoint         carrier     flat    nested   array    typed    verdict
─────────        ───────     ────    ──────   ─────    ─────    ───────
PATCH /users/me  json        P       P        P        P        → widest binder
PATCH /users/me  form        P       P        P        P        → 2nd parser
PUT  /users/:id  json        P       P        P        P        → replace
POST /register   json        P       P        P        P        → create
POST /register   form        P       —        P        —        → form create
POST /orders     json        P       P        P        P        → economic
POST /import     json        P       P        P        P        → bulk
GraphQL          args        P       input    —        —        → schema
POST /admin/*    json        P       P        P        P        → needs edge
```

`P` = probe-worthy; the falsifier at each cell prunes the rest.

## The falsifier-to-live-cells decision table

| Dead cell | The kill | Live cells |
|---|---|---|
| `PATCH /me` json/flat `400` | json row for PATCH | form, nested, PUT, POST |
| `PATCH /me` json/flat drop | flat for PATCH | nested, array, typed, PUT, POST |
| `PATCH /me` all carriers | all binders for PATCH | PUT, POST/register, orders, import |
| `POST /register` drop | flat for register | PATCH (wider), PUT, nested |
| `orders` `400` | json for orders | form, /import |
| `import` drop | bulk binder | GraphQL, /admin |
| `role` inert | `role` semantic | `is_staff`, `permissions`, JWT |
| all user fields | user model | `orders`/`wallets`/`memberships` models |
| all binders | class | decide.py → next class |

## The falsifier-depth reading

```
400 on json/flat           → depth 1: content-type — form path open
200+drop on json/flat      → depth 2: endpoint — nested/other endpoint
drop on all carriers       → depth 3: binder-family — /import/GraphQL
no priv fields anywhere    → depth 4: model — class dead
stored, gate unchanged     → depth 5: semantic — next field/gate
```

## The honest-map record

```
## falsifier map — <challenge>

### PATCH /users/me
- json/flat `role`        → 400 unknown property  [content-type dead]
- json/flat `is_admin`    → 400                   [content-type dead]
- json/nested `profile.*` → UNTESTED  ← next
- form `role`             → UNTESTED  ← next

### POST /register
- json/flat `role`        → drop ("role":"user")  [endpoint dead]
- form `role`             → UNTESTED  ← next

### live cells
- PATCH /me json/nested, form
- POST /register form
- PUT /users/:id all carriers
- /import, GraphQL, /admin
```

## The budget discipline

5 probes per mechanism cell; a falsifier closes the cell. The map
shows which cells are spent (`dead`), which are live (`UNTESTED`),
and which are ruled out (`—`). The next session resumes at a live
cell, not a dead one.
