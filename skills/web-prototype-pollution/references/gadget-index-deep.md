# Gadget index deep — the extended sink→property lookup

The full property-name → sink mapping, with the trigger condition
and the payoff for each. Ordered by how often each name is the
intended write in a real challenge.

---

## 1. Template-engine options (the RCE tier)

| Property | Engine | What it does | Payoff |
|---|---|---|---|
| `outputFunctionName` | ejs | the generated function's name — embedded raw into the compiled source | code-exec on render — `x;CODE;var y` |
| `localsName` | ejs | the locals object's name in generated code | identifier-grammar escape |
| `destructureLocals` | ejs | array of identifiers destructured in generated code | same — `["x;CODE;y"]` |
| `escape` | ejs | the escape function's generated name | code-embed |
| `escapeFunction` | ejs | the escape fn — `opts.escapeFunction` used as-is | supply a call-target |
| `client` | ejs | returns the compiled function vs running it | behavior switch |
| `compileDebug` | ejs | embeds line numbers / debug — verbosity oracle | marker |
| `filename` | ejs/pug | the template path used in errors and `include`/`extends` resolution | path-redirect of includes |
| `root` | ejs | include-resolution base dir | file-read redirect |
| `views` | express | view lookup dirs | path-redirect |
| `delimiter`/`openDelimiter`/`closeDelimiter` | ejs | tag delimiters | grammar break |
| `_with`/`strict` | ejs | whether `with(locals)` is generated | scope-shape |
| `name` | pug | the compiled function's name | code-embed like outputFunctionName |
| `basedir` | pug | include/extends resolution base | path-redirect |
| `self` | pug | use `self` namespace for locals | scope-shape |
| `globals` | pug | whitelist of globals available in template | inject names |
| `filters` | pug | named filter functions map | `filters.x = code-path` |
| `compileDebug`/`pretty`/`debug` | pug | verbosity | marker |
| `cache` | pug/ejs | template caching | second-order persistence |
| `allowProtoPropertiesByDefault` | handlebars 4.6+ | read proto properties in templates | unlocks proto reads |
| `allowProtoMethodsByDefault` | handlebars 4.6+ | call proto methods in templates | unlocks proto calls |
| `compat` | handlebars | compat mode | grammar switch |
| `helpers` | handlebars | helper-function map | `helpers.x` a call-target |
| `partials` | handlebars | partial map | inject markup |
| `decorators` | handlebars | decorator map | code-embed |
| `data`/`blockParams`/`knownHelpers` | handlebars | compile opts | data-path writes |
| `autoescape`/`autoEscape` | nunjucks | escape control | XSS unlock |
| `filters` | nunjucks | filter-function map | call-target |
| `globals` | nunjucks | global objects in template | data-inject |
| `extensions` | nunjucks | extension classes | code-path |
| `loader`/`searchPaths`/`path` | nunjucks | template search dirs | path-redirect |
| `tags`/`blockStart`/`blockEnd`/`variableStart`/`variableEnd`/`commentStart`/`commentEnd` | nunjucks/mustache | tag grammar | syntax-grammar write |
| `partials` | mustache | partial map | markup inject |
| `delimiters`/`tags` | mustache | tag grammar | syntax-grammar |
| `variable` | underscore `_.template` | the data-object's name in generated code | `x;CODE;var y` — code-embed |
| `imports` | underscore | imported names in template | `imports.require = "require"` — module inject |
| `evaluate`/`interpolate`/`escape` | underscore | the regexes for `<% %>`/`<%= %>`/`<%- %>` | grammar write |
| `sourceURL`/`sourceMap` | underscore | source-map URL | info/path |
| `helpers`/`blocks`/`layouts` | handlebars-layouts | layout helper opts | code-path |
| `pre`/`post`/`wrapper`/`format` | various | generated-code wrappers | code-embed |
| `locals`/`context`/`data` | various | the render-context object | data-write |
| `transform`/`map`/`each`/`filter` | various | callback opts | call-target |

## 2. `child_process` options (the exec tier)

| Property | What spawn reads | Payoff |
|---|---|---|
| `env` | child environment | NODE_OPTIONS/LD_PRELOAD/BASH_ENV/PATH/PYTHONPATH/PERL5OPT/RUBYOPT/GIT_SSH_COMMAND/EDITOR/http_proxy — env-load RCE |
| `shell` | `/bin/sh -c` wrap | `;`/`&&`/`\|` injection into the spawned command string |
| `execPath` | the binary to exec | run `/tmp/x` as the "node" |
| `execArgv` | args to execPath | `--eval 'CODE'` |
| `execFile` | the file to run | path-redirect |
| `argv0` | the argv[0] | name spoof (cosmetic mostly) |
| `cwd` | child working dir | path context |
| `uid`/`gid` | child uid/gid | priv shape (needs root parent) |
| `stdio` | stdio config | output redirect |
| `detached` | process-group detach | persistence shape |
| `timeout`/`killSignal` | kill control | liveness |
| `serialization` | IPC codec | `advanced` vs `json` — a deserialization surface |
| `silent`/`windowsHide`/`windowsVerbatimArguments`/`input`/`maxBuffer`/`encoding` | misc | behavior writes |
| `workerData`/`eval`/`execArgv`/`argv`/`stdin`/`stdout`/`stderr`/`trackUnmanagedFds`/`transferList`/`resourceLimits`/`name`/`type`/`credentials` | `new Worker` opts | eval:true+filename=CODE is the clean one |

## 3. `require`/`import` resolution (the load tier)

| Property | The read | Payoff |
|---|---|---|
| `main` | package `main` field | `{"main":"/tmp/x.js"}` |
| `paths` | resolution search dirs | prepend /tmp/node_modules |
| `extensions` | ext→loader map | redirect `.js` |
| `exports`/`imports` | package export/import maps | map-redirect |
| `specifier`/`dir`/`modulePath`/`parent`/`filename`/`id`/`loaded`/`children`/`paths` | module-system reads | path-redirect |
| `type` | `"module"`/`"commonjs"` | ESM-vs-CJS confusion |
| `dlopen`/`filename` | `process.dlopen` | native-module load |

## 4. HTTP/TLS/client options (the SSRF tier)

| Property | The read | Payoff |
|---|---|---|
| `url`/`uri`/`host`/`hostname`/`port`/`path`/`href`/`base`/`baseURL`/`baseUrl`/`endpoint`/`api`/`server`/`origin` | request target | SSRF |
| `proxy`/`agent`/`httpAgent`/`httpsAgent`/`dispatcher` | proxy/tunnel | traffic-redirect |
| `headers` | request headers | header-inject (auth/cookie) |
| `auth`/`bearer`/`token`/`apiKey`/`key`/`secret`/`password`/`username` | auth fields | cred-inject |
| `rejectUnauthorized`/`checkServerIdentity`/`ca`/`cert`/`key`/`pfx`/`passphrase`/`ciphers`/`secureProtocol`/`servername`/`ALPNProtocols`/`minVersion`/`maxVersion`/`session`/`ticketKeys`/`honorCipherOrder`/`ecdhCurve`/`dhparam`/`crl`/`sigalgs`/`clientCertEngine`/`privateKeyEngine`/`pskCallback`/`SNICallback`/`createConnection`/`getSocket`/`freeSocketTimeout`/`socketPath`/`localAddress`/`localPort`/`family`/`hints`/`lookup`/`all`/`verbatim` | TLS/net opts | verification-off, path-redirect |
| `timeout`/`maxRedirects`/`followRedirect`/`followAllRedirects`/`maxRedirects`/`removeRefererHeader`/`redirect`/`redirects`/`method`/`qs`/`query`/`search`/`searchParams`/`body`/`form`/`formData`/`json`/`multipart`/`encoding`/`gzip`/`deflate`/`brotli`/`decompress`/`compress`/`insecure`/`strictSSL`/`jar`/`cookie`/`withCredentials`/`credentials`/`mode`/`cache`/`referer`/`referrer`/`referrerPolicy`/`integrity`/`keepalive`/`signal`/`priority`/`duplex`/`window`/`serviceWorker` | request opts | behavior writes |
| `callbackUrl`/`callback`/`webhook`/`notifyUrl`/`notify`/`returnUrl`/`redirectUri`/`redirect_uri`/`successUrl`/`failureUrl`/`cancelUrl`/`postback`/`pingback`/`hook`/`endpoint` | callback fields | outbound-SSRF |

## 5. Authz/role/ownership names (the gate tier)

| Property | The check | Payoff |
|---|---|---|
| `isAdmin`/`is_admin`/`admin`/`isAdminUser`/`superuser`/`isSuperuser`/`staff`/`isStaff`/`role`/`roles`/`role_id`/`user_type`/`type`/`kind`/`level`/`group` | `if (user.x)`/`user.role === 'admin'` | role bypass |
| `verified`/`active`/`enabled`/`approved`/`confirmed`/`validated`/`authenticated`/`banned`/`suspended`/`locked`/`frozen`/`disabled`/`blocked`/`muted`/`restricted`/`expired`/`valid`/`kyc`/`mfa`/`mfa_enabled`/`two_factor`/`otp_verified`/`trial`/`subscription`/`plan`/`tier`/`license`/`credits`/`quota`/`balance` | `user.verified`/`!user.banned`/`user.plan === 'pro'` | state-flag bypass |
| `owner_id`/`user_id`/`uid`/`sub`/`tenant_id`/`org_id`/`account_id`/`company_id`/`site_id`/`workspace_id`/`project_id`/`created_by`/`assigned_to`/`author_id`/`creator_id`/`parent_id`/`linked_id`/`scope`/`scope_id`/`context_id`/`realm`/`region`/`zone` | `doc.owner_id === req.user.id`/`user.tenant_id` | ownership/tenant bypass |
| `permissions`/`perms`/`scopes`/`capabilities`/`acl`/`grants`/`rights`/`privileges`/`access`/`access_level`/`clearance`/`entitlements`/`authorities`/`claims`/`allowed`/`whitelist`/`allowlist` | `user.permissions.includes('admin')`/membership | perm-list inject |
| the is_*/can_*/has_*/should_*/allow_*/enable_* family | if (user.x) boolean gates | the pattern is "any boolean the app reads as a gate" — the operative list is extracted per-target by the grep in section 7, not memorized |

The `is_*`/`can_*`/`has_*`/`should_*`/`allow_*`/`enable_*` family
follows one grammar: `if (user.<name>)` where `<name>` is any
boolean-shaped property. The operative list is the ~40 names a
`grep` for `\.is[A-Z]`/`\.can[A-Z]`/`\.has[A-Z]` extracts from the
target's source — the generic list above is the starting set.

## 6. Config/debug names (the behavior tier)

| Property | The read | Payoff |
|---|---|---|
| `debug`/`verbose`/`dev`/`development`/`production`/`test`/`staging`/`local`/`ci`/`trace`/`log`/`logLevel`/`level`/`quiet`/`silent` | verbosity/mode gates | info-leak, error-verbosity, debug-endpoint unlock |
| `cache`/`cacheBust`/`memoize`/`ttl`/`lifetime`/`expiry`/`maxAge`/`stale`/`revalidate` | cache opts | cache-control, second-order persistence |
| `secret`/`signingKey`/`secret_key`/`key`/`privateKey`/`jwtSecret`/`sessionSecret`/`cookieSecret`/`apiKey`/`apiSecret`/`clientSecret`/`tokenSecret`/`encryptionKey`/`encryption_key`/`cipher`/`iv`/`salt`/`pepper`/`hmac`/`hmacSecret`/`signatureSecret`/`verifySecret`/`webhookSecret`/`sharedSecret`/`masterKey`/`rootKey`/`adminKey`/`serviceKey`/`bearer`/`credential`/`credentials`/`password`/`passwd`/`pwd`/`pass`/`passphrase`/`pin`/`otp`/`seed`/`nonce`/`token`/`accessToken`/`refreshToken`/`idToken`/`sessionToken`/`authToken`/`bearerToken`/`apiToken`/`jwt`/`jwtSecret`/`jwtKey`/`jwtPrivate`/`jwtPublic` | signing/secret reads | forge/reuse, key-disclosure |
| the config/debug/mode/secret/env/queue/timeout/limit/feature-flag family | config-field writes | behavior/state toggles — the long tail is the app's config vocabulary |

The `is_*` tail is intentionally compressed — the pattern is "any
boolean the app reads as a gate". The operative list is the FIRST
~40 names; the rest are the long tail a `bundle_miner`/grep can
extract per-challenge.

## 7. The "which name does THIS app read" method

```bash
# 1. every fallback-read property in source
grep -rnoE '[a-zA-Z_$.]+\.[a-zA-Z_]+\s*(\|\||\?\?|===?\s*undefined)' \
  <src> --include='*.js' | grep -v node_modules | sort -u \
  | grep -oE '\.[a-zA-Z_]+\s' | sort -u

# 2. every gate-read property
grep -rnoE '(if|while|&&|\|\||\?)\s*\(?[a-zA-Z_$.]+\.[a-zA-Z_]+' \
  <src> --include='*.js' | grep -v node_modules | grep -oE '\.[a-zA-Z_]+' | sort -u

# 3. every options-object read
grep -rnoE '(opts|options|config|cfg|settings|params|args|env|ctx)\.[a-zA-Z_]+' \
  <src> --include='*.js' | grep -v node_modules | sort -u
```

The union of these lists is the per-challenge pollution vocabulary —
write those names, not the generic list.