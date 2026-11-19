# Obfuscation formats — the resistance shapes and their counters

## The obfuscation ladder

```
minified          -> beautify -> read
identifier-mangled-> strings still literal -> grep
string-array      -> packed literals -> extract array / grep shape
encoded strings   -> atob/\x/\u -> decode escapes
control-flow      -> flattening -> skip the flow, grep literals
packed/wrapped    -> a packer -> unpack or grep shape
```

## The string-array obfuscator

`var _0x1a2b=['str1','str2',...]; function _0x3c4d(i){return
_0x1a2b[i]}` — javascript-obfuscator style. The literals are in the
array; the code references them by index.

```bash
# the packed array at the head
grep -oE 'var\s+_0x[0-9a-f]+\s*=\s*\[[^]]+\]' bundle.js | head
# grep the array for shapes
grep -oE '"[^"]*(api|http|token|flag|admin|secret|key)[^"]*"' bundle.js | sort -u
```

A deobfuscator (`webcrack`, `unminify`, `deobfuscator`) resolves the
lookups; often unnecessary — grep the array for the shape.

## The encoded-string shapes

| Encoding | Shape | Decode |
|---|---|---|
| `atob`/`base64` | `atob("aGVsbG8=")` | base64-decode |
| `\x` hex | `"\x68\x65\x6c\x6c\x6f"` | hex-decode |
| `\u` unicode | `"\u0068\u0065\u006c\u006c\u006f"` | unescape |
| `fromCharCode` | `String.fromCharCode(104,...)` | the char codes |
| `decodeURIComponent` | `%68%65%6c%6c%6f` | URL-decode |
| rot/caesar | a rotated literal | a rotation decode |
| a packed eval | `eval(function(p,a,c,k...)` | a packer unpacker |

```bash
grep -oE 'atob\(["'"'"'][A-Za-z0-9+/=]+' bundle.js
grep -oE "(\\\\x[0-9a-fA-F]{2}){4,}" bundle.js
grep -oE "(\\\\u[0-9a-fA-F]{4}){2,}" bundle.js
grep -oE 'String\.fromCharCode\([^)]*\)' bundle.js
grep -oE 'eval\(function\(p,a,c,k' bundle.js
```

## The control-flow flatten

A `switch(state)`/`for(;;)` state machine — the real logic is a jump
table. Skip it; grep the literals. A control-flow deflatter exists but
is rarely needed for endpoint mining.

## The packer shape

`eval(function(p,a,c,k,e,d){...}('packed',62,N,'lookup'.split('|')))` —
the Dean Edwards packer. A `p,a,c,k,e,d` signature. Unpack it (a
`packer` unpacker) or grep the packed string for the shape.

## The domain-lock / anti-tamper

The bundle checks `document.domain`, `window.location`, a hash of itself
— an anti-tamper that aborts off-domain. For mining (not executing),
irrelevant — grep the strings anyway.

## The shape-grep rule

Whatever the obfuscator does to the *code*, the *strings the runtime
needs* survive as data. Grep for the shape — `/api/`, `http`, `token`,
`flag{`, `secret`, `admin` — and the literals surface.
