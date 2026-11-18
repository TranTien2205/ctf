# White-box hunt — finding the NoSQLi in source

## The `find`/`findOne` sinks — the driver-call

```javascript
User.findOne({username: req.body.user, password: req.body.pass})
User.find({user: req.query.user})
db.collection('u').findOne({user: req.body.user})
db.users.find({user: req.body.user})
Model.findOne(req.body)
Model.find(req.query)
```

`find`/`findOne` with `req.body`/`req.query` — the filter-sink —
`detection.md`.

## The `aggregate` sink — the array-body

```javascript
Model.aggregate(req.body.pipeline)
Model.aggregate(req.body)
Model.aggregate(JSON.parse(req.body.q))
db.collection('u').aggregate(req.body)
```

`aggregate` — the array-body → pipeline — `aggregation.md`.

## The `update` sinks — the write-side

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

The update/delete-filter — `update-injection.md`.

## The `countDocuments`/`distinct` — the oracle

```javascript
User.countDocuments({user: req.body.user})
User.distinct("role", {user: req.body.user})
User.find({user: req.body.user}).count()
```

`countDocuments`/`distinct`/`count` — the count-oracle — `mongo-specific.md`.

## The `express.urlencoded` — the `qs` carrier

```javascript
app.use(express.urlencoded({extended: true}))
app.use(bodyParser.urlencoded({extended: true}))
```

`extended: true` → `qs` parses `user[$ne]=x` into `{user: {$ne: "x"}}` —
`injection-points.md`.

## The `express.json` — the JSON carrier

```javascript
app.use(express.json())
app.use(bodyParser.json())
```

`express.json` — the JSON-body — `{"user": {"$ne": null}}` —
`injection-points.md`.

## The `sanitizeFilter` — the sanitize

```javascript
app.use(mongoSanitize())
const filter = sanitizeFilter(req.body)
const q = sanitize(req.query)
```

`express-mongo-sanitize`/`mongoose.sanitizeFilter` — the `$`-strip —
`filter-bypass.md`.

## The `enableJs` — the `$where` capability

```javascript
// mongod.conf
security:
  javascriptEnabled: true
```

`enableJs`/`javascriptEnabled` — the `$where`/`$function` capability —
`operators-js.md`.

## The mongoose-schema — the type-coercion

```javascript
const User = mongoose.model('User', {user: String, pass: String})
```

A `String`-type schema — mongoose's `cast` — the object-into-filter is
cast or passes — `mongo-specific.md`.

## The `toJSON`/`JSON.parse` — the carrier

```javascript
const filter = JSON.parse(req.body.q)
const q = JSON.parse(req.query.filter)
const body = JSON.parse(req.headers['x-filter'])
```

`JSON.parse` on a param/header — the object-carrier — `injection-points.md`.

## The `eval`/`Function` — the JS-eval

```javascript
eval(req.body.q)
new Function(req.body.q)()
```

A JS-eval — the JS-injection — `operators-js.md`.

## The greps — the source-patterns

```bash
grep -rn "findOne\|\.find(\|\.aggregate(\|\.update\|\.distinct(" src/
grep -rn "req\.body\|req\.query\|req\.params" src/
grep -rn "express\.json\|urlencoded" src/
grep -rn "sanitizeFilter\|mongoSanitize" src/
grep -rn "javascriptEnabled\|enableJs" src/
grep -rn "JSON\.parse" src/
grep -rn "\$where\|\$expr\|\$regex\|\$ne\|\$gt" src/
```
