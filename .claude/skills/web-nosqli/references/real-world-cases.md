# Real-world cases — the NoSQLi's field history

## The `mongo-express` — the database-admin

`mongo-express` — a web admin for MongoDB — the CVE-2019-10758 RCE —
`eval` in the `toBSON` — the `{$where: "..."}`-style eval.

## The `Rocket.Chat` — the `$where` RCE

`Rocket.Chat` — CVE-2019-???? — the `$where` in a `find()` — the
JS-predicate's RCE — `enableJs` required.

## The `Parse Server` — the dashboard-injection

`Parse Server` — a BaaS — the dashboard's `where`/`filter` — the
`{"$regex":"^flag"}` on a hidden field — the `masterKey`-required
falsifier.

## The `Sails`/`waterline` — the `where` filter

`sails`'s `waterline` — `?where={"name":{"$ne":null}}` — the
`waterline-sql-builder` — the query-language's `$`-operators —
CVE-2018-16487-ish.

## The `Strapi` — the `_where`/`_contains`

`strapi`'s `_where`/`_contains`/`_sort` — the admin-API's filters —
CVE-2019-18818/2019-19609 — the `_where` array-of-objects.

## The `KeystoneJS` — the `_where` GraphQL

`keystone`'s GraphQL `_where` — `{allUsers(where: {pass_starts_with: "f"})}`
— the GraphQL's filter — `skills/web-graphql/`.

## The `LoopBack` — the `where`/`filter`

`loopback`'s `?filter[where][name][$ne]=null` — the REST-API's filter —
CVE-2019-???? — the `filter`/`where`/`include`/`fields`/`sort`/`limit`.

## The `Feathers` — the `$` operators

`feathers`'s query-syntax — `?name[$ne]=x` — the `$`-operators in the
query-string — `injection-points.md`.

## The `Mongoose` `populate` — the join-leak

`mongoose`'s `populate` — `{populate: "secret"}` — the join-leak —
CVE-2019-???? — the `$ref`/`$id` DBRef.

## The `NodeBB` — the `regExp` operator

`NodeBB` — the `regExp` operator — `{"name": {"$regex": "^admin"}}` —
the search's regex.

## The `Meteor` — the pub/sub query

`meteor`'s pub/sub — `Meteor.subscribe('users', {name: {$ne: null}})` —
the `EJSON`/`Mongo.Collection` — the pub-sub's query.

## The `MongoDB` `$where` — the historical

MongoDB pre-4.4 — `$where` used `eval` — the JS-engine's full surface —
`sleep()`/`load()`/`print()` — `operators-js.md`.

## The `aggregate` — the `saveToDB` leak

MongoDB's `aggregate` + `$out`/`$merge` — the write-pipeline — the
`$unionWith` — `aggregation.md`.

## The `gridfs` — the file-attach

`gridfs` — MongoDB's file-store — the `filename`/`metadata` injection —
`{"metadata.flag": {"$exists": true}}` — the dot-path.

## The `JStoJSON` — the eval-injection

`eval()`/`Function()`/`vm.runInNewContext()` — the JS-eval — `{"user":
{"$where": "this.pass == 'x'"}}` — `operators-js.md`.
