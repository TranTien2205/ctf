# Payload dictionary II — the less-common operators

## The `$mod` — the modulo

```json
{"id": {"$mod": [4, 0]}}          — id % 4 == 0
{"id": {"$mod": [2, 0]}}          — even ids
{"id": {"$mod": [2, 1]}}          — odd ids
{"id": {"$mod": [10, 0]}}         — id % 10 == 0
{"id": {"$mod": [100, 0]}}
{"id": {"$mod": [0, 0]}}          — INVALID — div by 0
{"score": {"$mod": [5, 0]}}
{"ts": {"$mod": [60, 0]}}
{"ts": {"$mod": [3600, 0]}}
{"ts": {"$mod": [86400, 0]}}
```

`operators.md` — `$mod` on a non-numeric field errors.

## The `$size` — the array-length

```json
{"tags": {"$size": 0}}            — empty array
{"tags": {"$size": 1}}            — 1-element
{"tags": {"$size": 2}}            — 2-element
{"tags": {"$size": 3}}
{"tags": {"$size": 10}}
{"roles": {"$size": 0}}           — no roles — guest
{"roles": {"$size": 1}}
{"tokens": {"$size": 0}}
{"items": {"$size": 0}}
{"flags": {"$size": 0}}
{"perms": {"$size": 0}}
{"roles": {"$size": {"$gt": 0}}}  — INVALID — $size takes int only
{"tags": {"$size": "2"}}          — string-2 — type-mismatch in qs
{"tags": {"$size": -1}}           — INVALID
{"tags": {"$size": 1.5}}          — INVALID — not int
```

`$size` only takes an int — `{"$size": {"$gt": 0}}` is a syntax error —
the error-oracle itself is the probe — `error-analysis.md`.

## The `$all` — the all-in

```json
{"tags": {"$all": ["a"]}}           — contains "a"
{"tags": {"$all": ["a", "b"]}}      — contains both
{"tags": {"$all": ["flag", "x"]}}
{"tags": {"$all": []}}              — matches nothing? no — only [] docs
{"tags": {"$all": [[]]}}
{"tags": {"$all": [["a"]]}}
{"roles": {"$all": ["admin"]}}
{"roles": {"$all": ["admin", "root"]}}
{"perms": {"$all": ["read", "write"]}}
{"tokens": {"$all": [{"$elemMatch": {"v": "x"}}]}}
{"tags": {"$all": [{"$regex": "^a"}]}}    — INVALID — no regex in $all
```

`$all` — `operators.md` — regex inside `$all` is invalid (unlike `$in`).

## The `$bits` family — the bitwise

```json
{"flags": {"$bitsAllSet": [1, 4]}}
{"flags": {"$bitsAllSet": 5}}
{"flags": {"$bitsAllSet": {"$binary": "..."}}}
{"flags": {"$bitsAnySet": [1, 4]}}
{"flags": {"$bitsAnyClear": [1, 4]}}
{"flags": {"$bitsAllClear": [1, 4]}}
{"flags": {"$bitsAllSet": 0}}
{"flags": {"$bitsAnySet": 0}}
{"flags": {"$bitsAnyClear": 0}}
{"flags": {"$bitsAllClear": 0}}
{"perms": {"$bitsAllSet": [0, 1, 2]}}
{"perms": {"$bitsAnySet": [0, 1, 2]}}
{"perms": {"$bitsAllSet": 7}}       — bits 0,1,2 set
{"perms": {"$bitsAllSet": 3}}       — bits 0,1 set
{"perms": {"$bitsAllSet": 1}}       — bit 0 set
{"perms": {"$bitsAllSet": 255}}
{"perms": {"$bitsAllSet": 256}}
{"perms": {"$bitsAllSet": -1}}
{"perms": {"$bitsAllSet": 0.5}}     — non-int — error
```

`$bits*` — `operators.md` — the bit-oracle — `flags`/`perms`/`mask`.

## The `$geo*` — the geospatial family

```json
{"loc": {"$near": [0, 0]}}
{"loc": {"$near": {"type": "Point", "coordinates": [0, 0]}}}
{"loc": {"$near": {"$geometry": {"type": "Point", "coordinates": [0, 0]}}}}
{"loc": {"$nearSphere": [0, 0]}}
{"loc": {"$geoWithin": {"$box": [[0,0], [1,1]]}}}
{"loc": {"$geoWithin": {"$center": [[0,0], 1]}}}
{"loc": {"$geoWithin": {"$centerSphere": [[0,0], 1]}}}
{"loc": {"$geoWithin": {"$polygon": [[0,0],[1,0],[1,1],[0,1]]}}}
{"loc": {"$geoWithin": {"$geometry": {"type": "Polygon", "coordinates": [[[0,0],[1,0],[1,1],[0,1],[0,0]]]}}}}
{"loc": {"$geoIntersects": {"type": "Point", "coordinates": [0, 0]}}}
{"loc": {"$geoIntersects": {"type": "LineString", "coordinates": [[0,0],[1,1]]}}}
{"loc": {"$geoIntersects": {"type": "Polygon", "coordinates": [[[0,0],[1,0],[1,1],[0,1],[0,0]]]}}}
{"loc": {"$geoIntersects": {"type": "MultiPoint", "coordinates": [[0,0],[1,1]]}}}
{"loc": {"$geoIntersects": {"type": "MultiLineString", "coordinates": [[[0,0],[1,1]]]}}}
{"loc": {"$geoIntersects": {"type": "MultiPolygon", "coordinates": [[[[0,0],[1,0],[1,1],[0,1],[0,0]]]]}}}
{"loc": {"$geoIntersects": {"type": "GeometryCollection", "geometries": []}}}
{"loc": {"$near": {"$geometry": {"type": "Point", "coordinates": [0, 0]}, "$maxDistance": 100}}}
{"loc": {"$near": {"$geometry": {"type": "Point", "coordinates": [0, 0]}, "$minDistance": 10}}}
{"loc": {"$near": {"$geometry": {"type": "Point", "coordinates": [0, 0]}, "$maxDistance": 100, "$minDistance": 10}}}
{"loc": {"$geoWithin": {"$box": [[0,0], [1,1]], "$maxDistance": 100}}}
{"loc": {"$geoWithin": {"$box": [[0,0], [1,1]], "$minDistance": 10}}}
{"loc": {"$geoWithin": {"$center": [[0,0], 1], "$maxDistance": 100}}}
{"loc": {"$geoWithin": {"$center": [[0,0], 1], "$minDistance": 10}}}
```

`$geo*` — `extended-corpus.md` — the geospatial-oracle — the
`"coordinates": [lng, lat]` order.

## The `$text`/`$search` — the text-search

```json
{"$text": {"$search": "admin"}}
{"$text": {"$search": "\"flag\""}}
{"$text": {"$search": "flag secret"}}
{"$text": {"$search": "flag -secret"}}
{"$text": {"$search": "\"flag{abc}\""}}
{"$text": {"$search": "flag", "$caseSensitive": true}}
{"$text": {"$search": "flag", "$caseSensitive": false}}
{"$text": {"$search": "flag", "$diacriticSensitive": true}}
{"$text": {"$search": "flag", "$diacriticSensitive": false}}
{"$text": {"$search": "flag", "$language": "en"}}
{"$text": {"$search": "flag", "$language": "none"}}
{"$text": {"$search": "flag", "$language": "es"}}
{"$text": {"$search": "flag", "$language": "fr"}}
{"$text": {"$search": "flag", "$language": "de"}}
{"$text": {"$search": "flag", "$language": "ru"}}
{"$text": {"$search": "flag", "$language": "zh"}}
{"$text": {"$search": "flag", "$language": "ar"}}
{"$text": {"$search": "flag", "$language": "hi"}}
{"$text": {"$search": "flag", "$language": "pt"}}
{"$text": {"$search": "flag", "$language": "ja"}}
{"$text": {"$search": "flag", "$language": "ko"}}
{"$text": {"$search": "flag", "$language": "it"}}
{"$text": {"$search": "flag", "$language": "nl"}}
{"$text": {"$search": "flag", "$language": "pl"}}
{"$text": {"$search": "flag", "$language": "sv"}}
{"$text": {"$search": "flag", "$language": "tr"}}
{"$text": {"$search": "flag", "$language": "uk"}}
{"$text": {"$search": "flag", "$language": "cs"}}
{"$text": {"$search": "flag", "$language": "da"}}
{"$text": {"$search": "flag", "$language": "fi"}}
{"$text": {"$search": "flag", "$language": "el"}}
{"$text": {"$search": "flag", "$language": "he"}}
{"$text": {"$search": "flag", "$language": "hu"}}
{"$text": {"$search": "flag", "$language": "id"}}
{"$text": {"$search": "flag", "$language": "nb"}}
{"$text": {"$search": "flag", "$language": "ro"}}
{"$text": {"$search": "flag", "$language": "th"}}
{"$text": {"$search": "flag", "$language": "vi"}}
{"$text": {"$search": "flag", "$language": "invalid-lang"}}
```

`$text` — `extended-corpus.md` — needs a text-index.

## The `$slice` — the array-slice

```json
{"items": {"$slice": 5}}           — first 5
{"items": {"$slice": -5}}          — last 5
{"items": {"$slice": [0, 5]}}      — skip 0, limit 5
{"items": {"$slice": [5, 5]}}      — skip 5, limit 5
{"items": {"$slice": [10, 5]}}
{"items": {"$slice": [0, 1]}}
{"items": {"$slice": [0, 0]}}
{"items": {"$slice": [0, -1]}}
{"items": {"$slice": [0, 100]}}
{"items": {"$slice": [0, 1000]}}
{"items": {"$slice": 0}}
{"items": {"$slice": -1}}
{"items": {"$slice": 1}}
{"items": {"$slice": [0, "5"]}}    — string-5 — error
{"items": {"$slice": "5"}}         — string — error
{"items": {"$slice": null}}        — error
```

`$slice` — `extended-corpus.md` — a projection-operator, not a filter —
in a `find` it slices the returned array; in a filter it's an error —
the error-oracle.

## The `$comment`/`$hint`/`$maxScan`/`$snapshot`/`$orderby`/`$natural` — the meta

```json
{"user": "admin", "$comment": "x"}
{"user": "admin", "$comment": "probe-id"}
{"user": "admin", "$comment": "request-id: 123"}
{"user": "admin", "$comment": "<script>alert(1)</script>"}
{"user": "admin", "$comment": {"$ne": null}}
{"user": "admin", "$hint": {"user": 1}}
{"user": "admin", "$hint": {"user": -1}}
{"user": "admin", "$hint": {"$natural": 1}}
{"user": "admin", "$hint": {"$natural": -1}}
{"user": "admin", "$hint": "user_1"}
{"user": "admin", "$hint": "user_1_pass_1"}
{"user": "admin", "$maxScan": 100}
{"user": "admin", "$maxScan": 1000}
{"user": "admin", "$maxScan": 0}
{"user": "admin", "$maxScan": -1}
{"user": "admin", "$maxTimeMS": 100}
{"user": "admin", "$maxTimeMS": 1000}
{"user": "admin", "$maxTimeMS": 0}
{"user": "admin", "$snapshot": true}
{"user": "admin", "$snapshot": false}
{"user": "admin", "$orderby": {"user": 1}}
{"user": "admin", "$orderby": {"user": -1}}
{"user": "admin", "$orderby": {"$natural": 1}}
{"user": "admin", "$orderby": {"$natural": -1}}
{"user": "admin", "$natural": 1}
{"user": "admin", "$natural": -1}
{"user": "admin", "$explain": true}
{"user": "admin", "$readPreference": {"mode": "primary"}}
{"user": "admin", "$readPreference": {"mode": "secondary"}}
{"user": "admin", "$readPreference": {"mode": "nearest"}}
{"user": "admin", "$readPreference": {"mode": "primaryPreferred"}}
{"user": "admin", "$readPreference": {"mode": "secondaryPreferred"}}
{"user": "admin", "$query": {"user": "admin"}}
{"user": "admin", "$query": {"user": {"$ne": null}}}
{"$query": {"user": "admin"}, "$orderby": {"user": 1}}
{"$query": {"user": "admin"}, "$hint": {"user": 1}}
{"$query": {"user": "admin"}, "$comment": "x"}
{"$query": {"user": "admin"}, "$maxScan": 100}
{"$query": {"user": "admin"}, "$maxTimeMS": 100}
{"$query": {"user": "admin"}, "$snapshot": true}
{"$query": {"user": "admin"}, "$explain": true}
{"$query": {"user": "admin"}, "$natural": 1}
```

`$comment`/`$hint`/`$maxScan`/`$maxTimeMS`/`$snapshot`/`$orderby`/
`$natural`/`$explain`/`$readPreference`/`$query` — `mongodb-internals.md`.
