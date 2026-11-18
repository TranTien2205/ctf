# Mongoose internals — the schema/cast layer's quirks

## The `cast` — type-coercion per path

```javascript
const User = mongoose.model('User', {user: String, pass: String, age: Number})
User.findOne({user: {$ne: null}, pass: {$ne: null}})
```

Mongoose casts the filter per the schema — a `String`-typed field with an
object value → `CastError` (mongoose ≥6). The cast happens BEFORE the
query reaches mongo — `mongo-specific.md`.

## The `strictQuery` — the unknown-key strip

```javascript
mongoose.set('strictQuery', true)     — strip keys not in the schema
mongoose.set('strictQuery', false)    — pass everything
mongoose.set('strictQuery', 'throw')  — throw on unknown
```

`strictQuery: true` (the ≥6 default) strips non-schema keys — a
`{$where: ...}` or `{"$or": [...]}` at the ROOT gets stripped —
`filter-bypass.md` — but `$`-keys INSIDE a schema-typed field still
reach the query.

## The `sanitizeFilter` — the `$`-key strip

```javascript
const filter = mongoose.sanitizeFilter(req.body)
Model.findOne(filter)
```

`sanitizeFilter` strips top-level `$`-keys and keys containing `.` —
`filter-bypass.md` — the bypass is a non-`$`/`non-`.`-key carrier or a
nested depth.

## The `CastError` — the type-mismatch

```javascript
User.findOne({user: {$ne: null}})  — user: String → CastError
User.findOne({user: "admin"})      — ok
User.findOne({age: {$ne: null}})   — age: Number → CastError
User.findOne({age: "5"})           — "5" → 5 — cast-coerces
```

`CastError` — the string-coercion is loose for scalars, strict for
objects — `denied-conditions.md`.

## The `Mixed`/`Object`/`Schema.Types.Mixed` — the free-pass

```javascript
{f: mongoose.Schema.Types.Mixed}
{f: Object}
{f: {}}
{f: mongoose.Schema.Types.Map}
{f: mongoose.Schema.Types.Buffer}
{f: mongoose.Schema.Types.Decimal128}
{f: mongoose.Schema.Types.ObjectId}
```

A `Mixed`/`Object`/`Map`-typed field — no cast — the object passes
through — `mongo-specific.md`.

## The `ObjectId` cast — the 24-hex check

```javascript
{_id: mongoose.Schema.Types.ObjectId}
User.findOne({_id: {$ne: null}})    — CastError — object to ObjectId
User.findOne({_id: "507f..."})      — coerced
User.findOne({_id: "507f1f77bcf86cd799439011"})  — 24-hex — ok
User.findOne({_id: "not-an-id"})    — CastError — invalid
```

`ObjectId` — `mongo-specific.md`.

## The `Map` — the `{$}`-key carrier

```javascript
{f: mongoose.Schema.Types.Map, of: String}
User.findOne({f: {$ne: null}})
```

`Map` — a `{$}`-key inside a Map — `filter-bypass.md`.

## The `findOne` vs `find` — the cardinality

```javascript
User.findOne({$ne: null})  — returns the FIRST doc — object
User.find({$ne: null})     — returns ALL — array
```

`findOne` — the first-doc — `mongo-specific.md`.

## The `lean`/`populate` — the doc-shape

```javascript
User.findOne({...}).lean()                  — plain object
User.findOne({...}).populate('ref')          — join
User.findOne({...}).populate({path: 'ref'})  — nested-populate
```

`lean` returns a plain object; `populate` joins the ref — the
`populate`-leak — `mongo-specific.md`.

## The `select` — the projection

```javascript
User.findOne({...}).select('user pass')
User.findOne({...}).select('-pass')
User.findOne({...}).select('+secret')
```

`select` — the projection — a `+secret` pulls a hidden field — the
injection's read-back — `mongo-specific.md`.

## The `skip`/`limit`/`sort` — the pagination

```javascript
User.find({...}).skip(0).limit(1).sort({created: -1})
User.find({...}).sort({user: 1})
User.find({...}).sort({$natural: -1})
User.find({...}).sort({$meta: "textScore"})
```

`sort`/`skip`/`limit` — the pagination — `mongo-specific.md`.

## The `countDocuments`/`estimatedDocumentCount` — the count

```javascript
User.countDocuments({user: {$ne: null}})
User.estimatedDocumentCount()
User.find({...}).count()
User.find({...}).countDocuments()
```

The count-oracle — `mongo-specific.md`.

## The `distinct` — the unique-values

```javascript
User.distinct("role", {user: {$ne: null}})
User.distinct("pass", {user: "admin"})
User.distinct("flag", {})
```

`distinct` — the unique-value extraction — `mongo-specific.md`.

## The `aggregate` — the pipeline

```javascript
User.aggregate([{"$unionWith": "flag"}])
User.aggregate(req.body.pipeline)
User.aggregate(JSON.parse(req.body.q))
```

`aggregate` — `aggregation.md`.

## The `updateOne`/`updateMany`/`findOneAndUpdate` — the write

```javascript
User.updateOne({user: req.body.user}, req.body.update)
User.updateMany({user: req.body.user}, req.body.update)
User.findOneAndUpdate({user: req.body.user}, req.body.update)
User.findOneAndReplace({user: req.body.user}, req.body.update)
User.findOneAndDelete({user: req.body.user})
User.replaceOne({user: req.body.user}, req.body.update)
User.deleteOne({user: req.body.user})
User.deleteMany({user: req.body.user})
```

The update/write-filter — `update-injection.md`.

## The `bulkWrite` — the batch

```javascript
User.bulkWrite([
  {updateOne: {filter: {user: "x"}, update: {$set: {role: "admin"}}}},
  {updateMany: {filter: {user: {$ne: null}}, update: {$set: {role: "admin"}}}},
  {deleteMany: {filter: {user: {$ne: null}}}},
])
```

`bulkWrite` — `update-injection.md`.

## The `insertMany`/`create` — the write-shape

```javascript
User.insertMany(req.body)
User.create(req.body)
```

`create`/`insertMany` — `update-injection.md`.

## The `toJSON`/`toObject` — the doc-shaping

```javascript
doc.toJSON()
doc.toObject()
doc.toJSON({getters: true})
```

`toJSON` — the doc's shape — `mongo-specific.md`.

## The `pre`/`post` — the middleware

```javascript
schema.pre('findOne', function() { this.setQuery(sanitize(this.getQuery())) })
schema.post('save', function() { ... })
```

`pre`/`post` middleware — the app-level sanitize — `whitebox-hunt.md`.

## The `virtual` — the computed-field

```javascript
schema.virtual('fullName').get(function() { return this.user + ' ' + this.pass })
```

`virtual` — a computed field — `mongo-specific.md`.

## The `discriminator` — the sub-type

```javascript
const Admin = User.discriminator('Admin', {role: String})
```

`discriminator` — `mongo-specific.md`.
