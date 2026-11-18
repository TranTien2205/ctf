# Attack trees — the decision structure

The tree of where the check can be missing.

---

## The root — the check's position

```
the check is...
├── absent entirely            → every request reaches the object
├── on a different mount       → /api/ vs / (the prefix)
├── on a different method      → GET checked, PUT not
├── on a different format      → .html checked, .json not
├── on a different version     → /api/v1 checked, /api/v2 not
├── on a different carrier     → ?id checked, body not
├── on a different field       → ?user_id checked, ?owner_id not
├── a param/header/cookie      → ?role=admin / X-Role:admin / Cookie:role=admin
├── a JOIN over a forgeable    → session_token, a weak secret
├── on the wrong object        → the parent's check, not the child's
├── on the wrong field         → obj.owner (a string you set)
├── an "any id" fetch          → Model.get(id) with no scope
├── a collection override      → ?user_id=, ?scope=all, ?all=true
├── a field-list               → ?fields=role,secret
├── a mass-assign              → {"role":"admin","user_id":1}
├── a function-level           → /admin/* exists unguarded
├── a normalization            → //admin, /admin/, ;param, %2f
├── a second-order             → export, render, bot, job, webhook
├── a protocol                 → WS/SSE/RPC/multipart
├── a content-type             → JSON checked, XML not
├── a param-pollution          → ?id=1&id=2, ?id[]=1
├── a type-coerce              → [1], {"$ne":0}, {"$gt":0}
├── a predictable id           → uuid v1, ObjectId, hash-of-name
├── a leaked id                → collection dump, referer, GraphQL edges
└── on a different route       → /users/42 checked, /u/42 not
```

## The "the check is a param/header/cookie" tree

```
the check reads the role from...
├── ?role=admin / ?is_admin=1 / ?admin=1 / ?user=admin
├── ?as=admin / ?impersonate=1 / ?sudo=1 / ?su=1
├── ?debug=1 / ?test=1 / ?internal=1 / ?staff=1 / ?preview=1
├── ?token=admin / ?key=admin / ?secret=admin / ?auth=admin
├── X-Role:admin / X-Admin:true / X-Is-Admin:1 / X-Staff:true
├── X-Internal:true / X-Debug:true / X-Superuser:true / X-Root:true
├── X-Su:1 / X-Impersonate:1 / X-As-User:1 / X-On-Behalf-Of:1
├── X-Act-As:1 / X-User:admin / X-User-Id:1
├── X-Forwarded-User:admin / X-Remote-User:admin / X-Auth-User:admin
├── X-Authenticated-User:admin / X-Api-Role:admin
├── Cookie: role=admin / is_admin=1 / admin=1 / user=admin / uid=1
│           / staff=1 / su=1 / debug=1 / internal=1
├── {"role":"admin"} / {"is_admin":true} / {"isAdmin":true}
│           / {"admin":true} / {"staff":true} / {"superuser":true}
│           / {"sudo":true} / {"su":true} / {"root":true}
│           / {"debug":true} / {"internal":true}
├── JWT sub:1 / uid:1 / role:admin / is_admin:true / admin:true
└── Authorization: admin / Bearer admin
```

## The "the mount/route" tree

```
the route is reached via...
├── /users/42           — the canonical
├── /u/42               — the alias
├── /users/42/          — trailing slash
├── /users//42          — double slash
├── /users/./42         — dot-segment
├── /users/42.json      — format
├── /users/42.xml       — format
├── /users/42?format=json — format param
├── /api/users/42       — the /api mount
├── /api/v1/users/42    — versioned
├── /api/v2/users/42    — versioned
├── /v1/users/42        — version mount
├── /v2/users/42        — version mount
├── /api/legacy/users/42 — legacy
├── /api/internal/users/42 — internal
├── /internal/users/42  — internal mount
├── /_/users/42         — _ mount
├── /-/users/42         — - mount
├── /.users/42          — . prefix
├── /~users/42          — ~ prefix
├── /users/42           — HEAD
├── /users/42           — OPTIONS
├── /users/42           — TRACE
├── /users/42           — CONNECT
├── /users/42           — PUT
├── /users/42           — PATCH
├── /users/42           — DELETE
├── /users/42           — POST
└── the proxy-normalized variants
```

## The "the id is the answer" tree

```
the id is...
├── sequential           → id_sweep the range
├── zero-padded          → id_sweep with zfill
├── prefixed             → id_sweep with mutate
├── epoch ts             → predict + sweep
├── uuid v1              → recompute ts+MAC
├── uuid v4              → need the leak
├── uuid v5              → recompute ns+name
├── ObjectId             → ts+rand+counter enumerate
├── Snowflake            → ts+worker+seq enumerate
├── ULID                 → ts+rand enumerate
├── b64 Type:id          → decode → change → encode
├── hash-of-name         → recompute
├── opaque token         → need the leak
├── nanoid               → need the leak
└── the flag itself      → the route that accepts it
```

## The "the boundary object" tree

```
the object is...
├── your own             → not the proof — the session resolved it
├── another's private    → the proof — attributable data
├── another's public     → not the proof — intentionally readable
├── a linked child       → the parent's check is the gap
├── a linked parent      → the child's check is the gap
├── a deleted object     → /trash/, ?deleted=true
├── a shared object      → the shared_with list
├── a public-flagged one → the ?include_private flag
└── the flag's own object → the flag is the field
```

## The "the boundary layer" tree

```
the check sits at...
├── the mount (app.use('/api'))        → / is unguarded
├── the decorator (@requires_login)    → the undecorated
├── the controller (self.require_owner) → one method skips it
├── the service (check_owner)          → a direct repo call
├── the repo (get_for_user vs get)     → the unscoped get
├── the query (AND user_id)            → the missing AND
├── the ORM (current_user.orders)      → the global find
├── the GraphQL (me vs user(id:))      → the node(id:) resolver
├── the WS (upgrade auth)              → the post-upgrade messages
└── the job (the first hop's check)    → the second hop's read
```

## The "the second hop" tree

```
the second hop is...
├── a bot render            → XSS exfiltrates the rendered page
├── an export job           → the job's output file
├── a preview/screenshot    → the rendered bytes
├── a webhook callback      → the webhook body
├── a notification          → the notification's content
├── an import/clone/copy    → the imported copy
├── an aggregation/report   → the aggregated output
├── a search index          → the indexed content
├── a cache warm            → the warmed object
├── a transaction           → the moved balance
├── a relationship write    → the new relation
└── a trigger/run/execute   → the triggered action
```
