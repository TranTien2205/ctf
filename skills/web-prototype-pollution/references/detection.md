# Detection — finding the merge before you have the payload

Pollution needs three things on the wire: a merge site, a carrier that
reaches it, and a sink that reads the polluted property. Detection is
naming all three before spending a payload.

---

## 1. The merge-site signals

In a request you can send, look for:

- an endpoint that takes an OBJECT and stores it — `POST /settings`,
  `PUT /profile`, `PATCH /prefs`, `POST /theme`, `POST /config`,
  `PUT /document`, `POST /update`, `POST /import`
- a response that reflects the sent object back — the merge echo
- a body shape with nested objects (`{"theme":{"colors":{...}}}`) —
  deep merges only exist for nested data
- an update API with `$`-shaped or path-shaped fields (`$set`,
  `fields`, `ops`, `update`, `doc`, `patch`)
- a bulk endpoint (`[{"id":..,"fields":{..}}]`) — bulk walks merge
  per row

In source/bundle:

```bash
grep -rnE 'merge|extend|defaults|assign|set\(|deepSet|for \(.*in ' \
  --include='*.js' . | grep -vE 'node_modules|test' | head -40
grep -rnE 'Object\.assign|_\.merge|_\.defaultsDeep|deepmerge|\$\.extend' .
```

Every hit is a merge call — the option objects it touches are the
pollution targets.

## 2. The carrier question

Once a merge exists, does request data reach it?

```bash
grep -rnE 'merge\(.*req\.|extend\(.*req\.|merge\(.*body|merge\(.*query' .
```

`merge(opts, req.body)` / `merge(config, req.query)` / the JSON body
passed through a schema then merged — each is a carrier. The merge
that takes only `req.body` (no `res.body` field list) is the one.

## 3. The sink question

```bash
grep -rnE 'new Function|eval\(|\.compile\(|\.render\(|spawn\(|exec|require\(|\|\||\?\?|hasOwnProperty' .
```

Each `new Function`/`compile`/`spawn`/`eval` call site's OPTION object
is a sink. Each `opts.x || def` / `opts.x ?? def` fallback names a
readable property.

## 4. The cheap black-box tell

Send the marker and look for it reflected:

```bash
python3 tools/web/pp_probe.py --url "$BASE/api/profile" \
  --body '{"__proto__":{"ppmarker":"x"}}' --readback "$BASE/api/profile"
```

`pp_probe` runs the matrix — `__proto__` through JSON/form/query
carriers, then the readback. Output `marker-on-readback` = the write
reached the prototype; `readback-changed` = a fallback changed
without echoing (the subtler signal); neither = the merge rejected
the key or the carrier never reached it.

## 5. The reflected-vs-inherited discriminator

A `200 {"ppmarker":"x"}` in the response is NOT proof — it may be
the write echoed on the same object. The discriminator:

```
GET a DIFFERENT object (fresh, or another user's)
→ does IT carry ppmarker?
```

yes → prototype write (global). no → own-property write (local) —
NOT the class. `pp_probe --readback <other-url>` runs exactly this
control.

## 6. The qs/parser fingerprint

```bash
curl "$BASE/api/x?a[b]=1"
# → 400/500? a nested parser exists → __proto__[x]=1 shape works
# → {"a[b]":"1"} literal? flat parser → dotted-path payloads instead
```

`qs` (extended parser) builds nested objects from brackets — the
`__proto__[marker]` shape only exists where qs runs. Express's
`?query parser=extended` enables it; `simple` keeps it flat.

## 7. The "settings-shaped" endpoints to check first

The endpoint naming corpus — where merges live in the wild:

```
/api/settings /api/prefs /api/preferences /api/config /api/options
/api/theme /api/layout /api/style /api/customize /api/personalize
/api/profile /api/me /api/account /api/user
/api/update /api/patch /api/merge /api/sync /api/import /api/load
/api/document /api/doc /api/note /api/item /api/object /api/record
/api/filter /api/query /api/search /api/report /api/export
/api/admin/settings /api/admin/config /api/system/config
/api/widget /api/dashboard /api/panel /api/component
/api/i18n /api/locale /api/lang /api/translation
/api/notify /api/alert /api/template /api/email
```

Any one taking a nested object is a candidate merge site.

## 8. The response-time fingerprint

A deep merge is measurably slower on a nested body than a shallow
assign — `{"a":{"b":{"c":{"d":{"e":{"__proto__":{"m":1}}}}}}}` sent
twice, timed. A depth-proportional time delta hints a recursive walk
ran; a flat response time hints `Object.assign` (no sink).

## 9. The denial signature

| Observation | Meaning |
|---|---|
| `400/422` on `__proto__` key | explicit filter — try `constructor.prototype` |
| `200`, key echoed literally (`"__proto__"`) | parser kept it as data — merge not reached or key-safe |
| `200`, key absent from response | dropped by schema — try the nested path |
| `200`, key on written obj only | local write — the merge is shallow or frozen |
| `500` on `__proto__` value | the setter THREW — writable target exists (a lead) |

## 10. Where to look in the bundle

`tools/web/bundle_miner.py` output: `sources` with `merge(`,
`extend(`, `defaults`, `__proto__` (the library's own guard strings),
`hasOwnProperty`, `Object.assign`. The minified merge function is
identifiable by its shape even without symbols — it iterates keys
and recurses on objects.
