# Deobfuscation — reading a bundle that resists

## The escalation ladder

```
minified        -> beautify -> read           (trivial)
obfuscated-lite -> grep the strings           (endpoints survive)
obfuscated      -> unpack the string array    (literals recoverable)
obfuscated-hard -> a deobfuscator             (last resort)
```

Start with the cheapest read; escalate only when grep fails.

## Beautify — the first move

`js-beautify` / `prettier` reformats minified code into readable
structure — near-source for non-obfuscated bundles:

```bash
npx js-beautify bundle.js -o bundle.pretty.js 2>/dev/null
npx prettier --write bundle.js 2>/dev/null
# a python fallback
python3 -c "import jsbeautifier,sys;print(jsbeautifier.beautify(open('b.js').read()))" > pretty.js
```

## The string-array obfuscator

`var _0x1a2b = ['str1','str2',...]` at the head + `_0x1a2b[0]` lookups
throughout — javascript-obfuscator style. The literals are in the
array; the lookups index it.

```bash
# the packed string array at the head
grep -oE 'var\s+_0x[0-9a-f]+\s*=\s*\[[^]]+\]' bundle.js | head
# extract the array, decode the lookups — or grep the array for shapes
grep -oE '"[^"]*(api|http|token|flag|admin|secret)[^"]*"' bundle.js | sort -u
```

A deobfuscator (`deobfuscator`, `webcrack`, `unminify`) resolves the
lookups to literals — recoverable but usually unnecessary for endpoint
mining.

## Control-flow flattening

The logic is a `switch`/state machine — hard to read but the strings
endure. Skip the control flow; grep the literals.

## Encoded strings

`atob`, `decodeURIComponent`, a `String.fromCharCode` array, hex `\x`,
unicode `\u` — the strings are encoded but decoded at runtime.

```bash
# atob / base64 literals
grep -oE 'atob\s*\(\s*["'"'"'][A-Za-z0-9+/=]+' bundle.js
# \x and \u escapes
grep -oE "(\\\\x[0-9a-fA-F]{2}|\\\\u[0-9a-fA-F]{4}){4,}" bundle.js
# fromCharCode runs
grep -oE 'String\.fromCharCode\([^)]*\)' bundle.js
```

## The shape-grep fallback

When deobfuscation is too costly, grep for the *shape* — the string the
obfuscator could not remove:

```bash
strings bundle.js | grep -oE '/[a-z0-9_./-]+|https?://\S+|flag\{[^}]*\}|[A-Za-z0-9+/=]{20,}' | sort -u
```

## The rule

Deobfuscation is a means, not the goal — the goal is the endpoint, the
secret, the flag. If grep surfaces them, stop; do not spend the budget
prettying the whole bundle.
