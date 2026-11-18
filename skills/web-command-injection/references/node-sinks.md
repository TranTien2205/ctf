# Node.js Sinks — child_process and the eval family

## The sink table

| Call | Shell? | Notes |
|---|---|---|
| `exec(cmd)` | `/bin/sh -c` | THE common sink |
| `execSync(cmd)` | `/bin/sh -c` | sync version |
| `execFile(file, args, opts)` | NO shell by default | argv — falsifier at this sink |
| `execFile(file, args, {shell:true})` | sh -c | shell:true flips it |
| `spawn(cmd, args)` | NO shell | argv |
| `spawn(cmd, args, {shell:true})` | sh -c | |
| `spawnSync` | same spawn rules | |
| `fork(module, args)` | node argv | module execution |
| `execFileSync`/`spawnSync` | same rules | |
| `eval(code)` | JS evaluator | `eval-injection.md` |
| `new Function('x', code)` | JS evaluator | implicit eval |
| `vm.runIn*Context(code)` | vm module | sandbox-bypassable historically |
| `require` of uploaded .js | module exec | `skills/web-file-upload/references/node-specific.md`-style |
| `setTimeout(str)`/`setInterval(str)` | string-eval | implicit eval |
| `import('data:...')`/dynamic import | module eval | data-URI trick |

## `exec`/`execSync` — always sh -c

```js
exec('ping -c1 ' + host)
execSync(`convert ${file} out.png`)
```

`;`,`|`,`&&`,`||`,`$()`,backticks,`\n` all work — standard POSIX sh
semantics (dash on Debian/Ubuntu).

## `execFile`/`spawn` — the argv boundary, and its `shell:true` flip

```js
execFile('ping', [host])              // argv — safe-ish
execFile('ping', [host], {shell:true}) // shell:true → host inside sh -c!
spawn('ping', [host], {shell:true})
```

`shell:true` re-opens injection. Check source for `shell` option.

`execFile` with an args ARRAY + shell:true joins args with spaces into
the shell string — `host='127.0.0.1;id'` inside still injects.

## `spawn` argv elements — flag injection territory

`spawn('ping', [host])` — `host` is argv[1] — `-v`/`-c`/`--` flags work
— `argument-injection.md`. No shell, no metachars, flags are free.

## `fork(module)` — run a node file

`fork(file)` runs a .js module as a child — if `file` is upload/user-
controlled → js exec — `skills/web-file-upload/references/node-specific.md`.

## `eval`/`new Function`/`vm` — the JS evaluator family

```js
eval(userCode)                       → js exec
new Function('return ' + expr)()     → implicit eval
vm.runInNewContext(code, sandbox)    → sandbox (bypassable: this.constructor.constructor)
vm.runInThisContext / runInContext
setTimeout('code', 0)                → string eval
setInterval('code', ms)
require('vm').runInThisContext
```

The `vm` sandbox escape classic:

```js
this.constructor.constructor('return process')().mainModule.require('child_process').execSync('id')
```

`eval-injection.md` has the full gadget.

## `require` — module-load exec

`require(x)` runs the file — if `x` is a path you control (uploaded
`.js`, or `require(req.query.m)`) → exec. Also `require('data:...')`?

No — `import('data:text/javascript,...')` works in newer node for
data-URI eval.

## `child_process` output channels

- `exec` callback gets `(err, stdout, stderr)` — output flows to app
- `execSync` returns Buffer
- `spawn` events stream
- errors surface `Error: Command failed: ...` + the command line echoed!
  — the error message reveals the exact template

## `exec` error-message fingerprint

`Error: Command failed: ping -c4 x;id` — the command template leaked
verbatim — free white-box.

## Express/other handler contexts — where injection hides

- `req.query`/`req.body`/`req.params` → `exec()`
- JSON field into `exec`
- uploaded filename into `exec('mv ...')`
- file path into `exec('convert ' + f)`
- `req.headers['x']` into a command

## The `process.binding`/`process.mainModule` escape — post-eval

Inside `eval`:

```js
process.mainModule.require('child_process').execSync('id')
process.binding('spawn_sync')
require('child_process').execSync('id')
```

## Falsifiers

- `execFile`/`spawn` argv-array without `shell:true` AND no fork/require
  path AND no eval/vm sink
- `shell-escape`/`shell-quote` libs applied correctly

## Output to record

- the sink call + whether `shell:` option is present + the argv shape
