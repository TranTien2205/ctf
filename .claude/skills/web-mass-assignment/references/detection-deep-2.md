# Detection deep 2 — the advanced detection layer

## The field-inventory completion check

The field inventory is complete when five sources agree:

1. `GET /api/me` keys — the returned set;
2. the bundle's constructed objects — the JS's field names;
3. the error's schema leak — `"unknown property: x, expected: a,b,c"`;
4. the docs/introspection — the official model;
5. the admin/sibling view — the full record.

A field in ANY is a candidate; the union is the probe set.

## The binder-fingerprint confidence

| Confidence | Evidence |
|---|---|
| high | `TypeError`/`unknown property`/`X-Runtime` — the stack+family known |
| medium | `X-Powered-By`/cookies — the stack known, the binder inferred |
| low | silent `200` — infer merge-all, verify with a probe |

## The endpoint-width ordering

```
PATCH /users/me    ── widest (editable profile)
PATCH /settings    ── wide (nested settings)
PUT  /users/:id    ── wide (replace binds or wipes)
POST /import       ── wide (bulk, unguarded)
POST /orders       ── medium (domain fields)
PATCH /profile     ── medium (nested merge)
POST /register     ── narrow (declared fields)
GraphQL mutation   ── schema-bounded
POST /admin/*      ── widest (needs edge)
```

The widest binder first — `PATCH /me` before `POST /register`.

## The carrier-likelihood ordering

```
flat JSON      — 90% of binders
nested JSON    — 60% (deep-merge sites)
form flat      — 80% (form parser)
form prefixed  — 40% (Rails/PHP)
array          — 30% (typed fields)
typed          — 50% (enum/FK/bool)
multipart      — 20% (least tested)
query          — 15% (params union)
GraphQL        — 10% (args schema)
override       — 5%  (`?_method=`)
```

Probe the likely carriers first; the falsifier drives the rest.

## The detection-confidence score

```
score = (fields found / semantics covered)
      × (endpoints found / expected binders)
      × (binder fingerprint confidence)
```

A high score means the surface is mapped; a low score means the
inventory is incomplete — keep reading before probing.

## The detection artifacts

| Artifact | File | Content |
|---|---|---|
| field list | `../field-notes.md` | the probe set |
| endpoint list | `../field-notes.md` | the binder surface |
| binder fingerprint | `../field-notes.md` | the grammar |
| falsifier map | `../field-notes.md` | the dead cells |
| live-cell matrix | `../field-notes.md` | the remaining probes |
| decision map | `../field-notes.md` | field → gate |

## The detection traps

- **narrow serializer**: `GET` shows `{"username","id"}` — the model
  may carry `role` hidden by the serializer. Check admin/sibling views.
- **cached read-back**: a stale `GET` — re-GET fresh before falsifying.
- **the `400` baseline**: the control itself `400`s — the documented
  body is wrong before the probe can run.
- **the `403` ownership**: `PATCH /users/9` on another's record — the
  ownership check `403`s before the binder — probe `me` instead.
