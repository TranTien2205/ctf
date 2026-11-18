# Error analysis — what each failure response is telling you

Pollution probes fail in informative ways. The error's status, body,
and wording locate which layer rejected the write.

---

## 1. Status-code map

| Status | The layer that fired | The next probe |
|---|---|---|
| 400 "Invalid JSON" | body parser | fix the syntax; the carrier reaches the merge |
| 400/422 "unexpected key __proto__" | schema validator | `constructor.prototype`, nested wrapper, a schema-permitted field |
| 401/403 | authn/authz, not the merge | the route is gated — the write never ran |
| 404 | no such route | endpoint mismatch — not a falsifier |
| 405 | method not allowed | try GET/PUT/PATCH |
| 413 | body too large | shrink the wrapper depth |
| 415 | content-type rejected | try `application/json` → `application/x-www-form-urlencoded` |
| 500 TypeError | the setter ran and threw | a lead — the proto path was attempted |
| 500 RangeError (call stack) | recursive merge on deep input | the merge IS recursive — depth works, try shallower |
| 502/503 | upstream/app crash | the write may have landed AND broken the app — check if the marker persists after recovery |

## 2. The error-body fingerprints

| Error text | What it means |
|---|---|
| `Cannot set property __proto__` | the setter threw — proto path attempted on a frozen/immutable target |
| `Converting circular structure to JSON` | your object created a cycle (the merge followed `__proto__` into itself) — the merge IS deep |
| `__proto__ is not allowed` | an explicit blacklist — constructor path next |
| `Invalid property name` | a schema layer rejects the key |
| `Maximum call stack size exceeded` | recursion through your nested object — deep merge confirmed |
| `Cannot create property on ...` | the target is non-extensible |
| `Cannot assign to read only property` | a getter-only or frozen target |
| `Object prototype may only be an Object` | you sent `__proto__` a primitive — needs an object value |
| `assignment to undeclared variable` | strict-mode — the merge writes globals |
| `is not a function` | a sink read your polluted property as a callable — the READ confirmed |
| `must be a string`/`must be an object` | typed sink rejected the VALUE type — the property was read, fix the type |

## 3. The `500` split — the most informative error

A `500` on `__proto__` input where a `200` on normal input exists
means the request REACHED the merge and the merge tried something
special for the proto key. Two sub-cases:

- **"Cannot set property"** — the proto-write was attempted and
  rejected by the engine (frozen proto, immutable root) — the sink
  exists but is hard.
- **Generic `500`** — the merge ran and the app crashed later on the
  polluted state — the write may STILL have landed. Fetch a fresh
  object: a marker there means the 500 was post-write damage, and the
  pollution is real.

## 4. The error-echo surfaces

```json
{"error": "Cannot merge key \"__proto__\""}
{"errors": [{"field": "__proto__", "message": "forbidden"}]}
{"message": "Bad Request", "detail": "path __proto__.m rejected"}
{"stack": "TypeError: ...\n    at merge (/app/lib/merge.js:42)"}
{"detail": {"type": "invalid_key", "key": "__proto__"}}
```

The `stack` echo names the merge's file:line — the white-box target.
The `detail.field`/`detail.key` echoes which segment the filter
caught — a path-aware filter (`__proto__.m` rejected) vs a key-only
filter (`__proto__` rejected).

## 5. The "500 with no body" case

A bare `500`/`502`/`503` after the write — the app may have crashed on
the polluted state. If it recovers, the pollution may persist in
memory:

```bash
# after the crash, the app restarted
GET /api/me → does the object carry the marker?
```

A persistent marker after a crash means the write was durable (to a
store) not just in-memory — stronger evidence AND a worse blast
radius.

## 6. The `200` that isn't a `200`

`200 {"success":true}` on the write but the readback is clean —
silently-dropped `__proto__`. The success response lies about the
proto write; the merge's own filter ate the key. The signal is the
ABSENCE on readback — the write's 200 was about the OTHER fields.

## 7. The per-layer error vocabulary

| Layer | Its characteristic error |
|---|---|
| qs parser | `Parameter limit exceeded`, `array limit` |
| body-parser | `Unexpected token`, `invalid json` |
| schema (joi/zod/ajv) | `"__proto__" is not allowed`, `additional property` |
| merge lib | `TypeError`, the lib's file in stack |
| ORM | `strict mode`, `unknown path`, `CastError` |
| template compile | `SyntaxError` in generated code — the sink got your bad payload |
| spawn | `ENOENT`/`EACCES` on your path |
| the gate | `403` on the foreign read |

Each layer's error names itself — the wording is the fingerprint.

## 8. What "no error" means

`200` + silent drop is the commonest denial — no exception, no marker,
just absent. The merge's key-filter ate the `__proto__` segment before
assigning. It is NOT "the sink is safe" — it is "the key never became
a write". Try the `constructor.prototype` alias, a deeper nest, or a
different content-type before recording `refutes`.
