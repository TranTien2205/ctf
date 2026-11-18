# Gadget index — polluted property → sink → payoff

A landed write is only the beginning: the polluted property has to be
READ by later code with a fallback. This index maps property names to
the sinks that read them. The right column is what you get; the middle
is the code idiom to find in source or bundle.

---

## 1. Template-engine sinks (server-side)

| Property | Sink idiom | Payoff |
|---|---|---|
| `outputFunctionName` | EJS: `new Function(opts.outputFunctionName)` | RCE — the function name is compiled into generated code |
| `escape`/`escapeFunction` | EJS/Pug escape fn lookup | XSS/RCE — replace the escaper |
| `destructureLocals` | EJS local-var destructuring | RCE — inject a variable name |
| `client`/`compileDebug` | Pug/EJS options branch | code path selection |
| `filters`/`globals` | template engine option objects | add a filter/global that runs |
| `root`/`views`/`filename` | template file resolution | file-read / arbitrary template |
| `basedir` | Pug include resolution | path control |
| `delimiter`/`openDelimiter`/`closeDelimiter` | Mustache/lodash template | syntax confusion → injection |
| `imports`/`imports.require` | lodash `_.template` imports | `require` inside template |
| `variable` | lodash template `options.variable` | rebind the data name |
| `evaluate`/`interpolate`/`escape` delimiters | `_.templateSettings` | inject template syntax |
| `pretty`/`debug` | engine option flips | verbose errors, dev render |

## 2. Process/spawn sinks

| Property | Sink idiom | Payoff |
|---|---|---|
| `shell` | `spawn(cmd, {shell: true})` | command injection through the spawned shell |
| `env`/`env.NODE_OPTIONS` | `spawn(cmd, {env})` | `NODE_OPTIONS=--require /tmp/x` → arbitrary require |
| `execPath`/`execArgv` | `fork(script, {execPath, execArgv})` | run a different node/file |
| `NODE_OPTIONS` | any node child | `--require`, `--inspect`, `--eval` |
| `cwd` | spawn's working dir | relative-path binary pickup |
| `argv0`/`args` | process spawn args | argument injection |
| `windowsHide`/`detached`/`uid`/`gid` | spawn option flips | drop privs / detach a process |
| `stdio`/`input`/`output` | spawn stdio config | redirect/read pipes |

## 3. HTTP/request sinks

| Property | Sink | Payoff |
|---|---|---|
| `url`/`uri`/`hostname`/`host`/`port`/`path` | request construction | SSRF — the fetch goes where you say |
| `headers` | header merge | header injection, auth overwrite |
| `agent`/`proxy` | http agent config | MITM/route through attacker host |
| `rejectUnauthorized` | TLS verify flag | disable cert check |
| `timeout` | request timeout | DoS/never-return |
| `maxRedirects`/`followRedirect` | redirect policy | open-redirect following |
| `qs`/`query`/`search` | querystring append | parameter smuggling |
| `baseURL`/`baseUrl` | axios/fetch prefix | re-root every API call |

## 4. Authz/identity sinks

| Property | Sink | Payoff |
|---|---|---|
| `isAdmin`/`is_admin`/`admin` | `user.isAdmin || false` | admin gate |
| `role`/`roles` | `user.role === 'admin'` | role check |
| `verified`/`active`/`banned` | account-state check | bypass pending/ban |
| `tenant`/`tenant_id`/`org` | tenant scoping | tenant pivot |
| `owner`/`owner_id`/`user_id` | ownership check `obj.owner === user.id` | fake ownership |
| `permissions`/`scopes` | `perms.includes('x')` | scope grant |
| `sub`/`aud`/`iss` | JWT claim verification | claim forge-adjacent |
| `password`/`hash` | a compare that reads a default | auth bypass by polluted compare |

## 5. Config/settings sinks

| Property | Sink | Payoff |
|---|---|---|
| `debug`/`dev`/`verbose` | feature flag | error/leak surfaces on |
| `main`/`entry`/`module` | `require(config.main)` | load your file |
| `paths`/`require.paths` | module resolution order | shadow a real module |
| `extensions` | `require.extensions` handler | handler hijack |
| `plugins`/`middleware` | app.use/plugin load list | run a supplied function/file |
| `key`/`secret`/`signingKey` | crypto config | re-sign tokens |
| `cookie`/`session` opts | session middleware | unsigned/weak session opts |
| `allowedHosts`/`whitelist`/`allowlist` | host allowlist | SSRF/open-redirect allowed |
| `uploadDir`/`dest`/`filename` | multer/upload config | write-where on upload |
| `view engine`/`views` | express app settings | template directory swap |

## 6. Cache/store sinks

| Property | Sink | Payoff |
|---|---|---|
| `cache`/`store`/`ttl` | cache config | cache-poison duration/location |
| `keyPrefix`/`prefix` | redis key namespace | collide another user's key |
| `driver`/`client` | cache backend pick | swap to attacker-controlled |
| `serialize`/`deserialize` | cache codec | code path in deserialization |

## 7. Logging/output sinks

| Property | Sink | Payoff |
|---|---|---|
| `log`/`logger`/`transport` | log transport config | write where, leak to |
| `format`/`formatter` | log/template format string | format-string injection |
| `silent`/`level` | logging disable | hide tracks |
| `output`/`outFile`/`file` | report/write targets | write-where |
| `layout`/`header`/`footer` | report template | HTML/PDF injection |

## 8. The fallback grammar — what "read with a fallback" looks like

```js
opts.x || defaults.x        — the classic
opts.x ?? defaults.x        — nullish version
'x' in opts ? opts.x : def  — explicit check
opts.hasOwnProperty('x') ? opts.x : def
opts.x !== undefined ? opts.x : def
Object.assign({}, defaults, opts)  — merge where opts wins
_.defaultsDeep(opts, defaults)     — opts wins over defaults
config.x                       — direct read, default is in config
```

The sink idiom that matters: the property is OPTIONAL in the app's own
objects, so its absence is "trusted" — your pollution supplies it and
the fallback never fires.

## 9. Reading the right column off the source

In white-box: `grep -nE '\|\||\?\?|hasOwnProperty|in opts|defaults'`
around every merge site and every option object — each is a candidate
fallback. The property NAME the fallback reads is the pollution key.

In black-box: `bundle_miner.py` the JS — `process.env`, `config.`,
`opts.`, `defaults`, `??`, `||` — the same grep on bundle text names
the readable properties.

## 10. The two-tier strategy

- **Tier 1 — prove the class**: pollute `ppmarker`, read it back on a
  fresh object. No sink needed yet.
- **Tier 2 — prove impact**: pollute the property a real sink reads —
  `outputFunctionName`, `shell`, `env.NODE_OPTIONS`, `isAdmin`,
  `role`. The sink's changed behaviour is the evidence.

Never skip tier 1: jumping straight at `isAdmin` without proving the
write reaches `Object.prototype` produces nothing when the merge is
local, and you cannot tell the failure apart from a missing sink.
