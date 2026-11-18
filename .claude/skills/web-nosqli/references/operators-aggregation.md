# Aggregation operators — the `$expr`/`$accumulator`/`$function` JS-side

## `$expr` — the query-side agg operators

```json
{"$expr": {"$eq": [{"$substrCP": ["$p", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$strLenCP": "$p"}, 32]}}
{"$expr": {"$eq": [{"$indexOfCP": ["$p", "{"]}, 4]}}
{"$expr": {"$regexMatch": {"input": "$p", "regex": "^a"}}}
{"$expr": {"$eq": [{"$toUpper": "$p"}, "FLAG{X}"]}}
{"$expr": {"$eq": [{"$toLower": "$p"}, "flag{x}"]}}
{"$expr": {"$eq": [{"$strcasecmp": ["$p", "flag{x}"]}, 0]}}
{"$expr": {"$eq": [{"$concat": ["$p", "x"]}, "flag{x}"]}}
{"$expr": {"$eq": [{"$split": ["$p", "{"]}, ["flag", "x}"]]}}
{"$expr": {"$eq": [{"$arrayElemAt": [{"$split": ["$p", "{"]}, 0]}, "flag"]}}
{"$expr": {"$eq": [{"$ltrim": {"input": "$p", "chars": " "}}, "flag{x}"]}}
{"$expr": {"$eq": [{"$rtrim": {"input": "$p", "chars": " "}}, "flag{x}"]}}
{"$expr": {"$eq": [{"$trim": {"input": "$p", "chars": " "}}, "flag{x}"]}}
{"$expr": {"$eq": [{"$substrBytes": ["$p", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$p", 0, {"$size": "$p"}]}, "flag{x}"]}}
{"$expr": {"$eq": [{"$convert": {"input": "$p", "to": "string"}}, "flag{x}"]}}
{"$expr": {"$eq": [{"$toString": "$p"}, "flag{x}"]}}
{"$expr": {"$eq": [{"$toObjectId": "$p"}, {"$oid": "..."}]}}
{"$expr": {"$eq": [{"$type": "$p"}, "string"]}}
{"$expr": {"$eq": [{"$isArray": "$p"}, true]}}
{"$expr": {"$eq": [{"$dateFromString": {"dateString": "$p"}}, {"$date": "..."}]}}
{"$expr": {"$eq": [{"$dateToString": {"date": "$p", "format": "%Y-%m-%d"}}, "2024-01-01"]}}
```

`$expr` — the aggregation-operators inside a query — `operators.md`.

## `$function` — the JS-in-expression

```json
{"$expr": {"$function": {"body": "function(p) { return p[0]=='f'; }", "args": ["$p"], "lang": "js"}}}
```

`$function` — `enableJs` required — `operators-js.md`.

## `$accumulator` — the JS-accumulator

```json
[{"$group": {"_id": null, "x": {"$accumulator": {"init": "function() { return 0; }", "accumulate": "function(s, p) { return s + p; }", "accumulateArgs": ["$p"], "merge": "function(a, b) { return a + b; }", "lang": "js"}}}}]
```

`$accumulator` — `enableJs` required — `operators-js.md`.

## `$let` — the variable-binding

```json
[{"$project": {"x": {"$let": {"vars": {"p": "$pass"}, "in": {"$eq": ["$$p", "x"]}}}}}]
[{"$project": {"x": {"$let": {"vars": {"p": "$pass"}, "in": {"$substrCP": ["$$p", 0, 4]}}}}}}]
```

`$let` — `extended-corpus.md`.

## `$cond`/`$ifNull`/`$switch` — the conditionals

```json
[{"$project": {"x": {"$cond": [{"$eq": ["$u", "admin"]}, "yes", "no"]}}}]
[{"$project": {"x": {"$ifNull": ["$flag", "none"]}}}]
[{"$project": {"x": {"$switch": {"branches": [{"case": {"$eq": ["$u", "admin"]}, "then": "a"}], "default": "z"}}}}]
```

`extended-corpus.md`.

## `$map`/`$filter`/`$reduce` — the array-expressions

```json
[{"$project": {"x": {"$map": {"input": "$items", "as": "i", "in": "$$i.price"}}}}]
[{"$project": {"x": {"$filter": {"input": "$items", "as": "i", "cond": {"$gt": ["$$i.price", 0]}}}}}]
[{"$project": {"x": {"$reduce": {"input": "$items", "initialValue": 0, "in": {"$add": ["$$value", "$$this"]}}}}}]
```

`extended-corpus.md`.
