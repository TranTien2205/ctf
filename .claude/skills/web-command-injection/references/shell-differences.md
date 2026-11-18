# Shell Differences — sh vs bash vs dash vs zsh vs fish vs busybox

## Identify the shell first — the syntax rules change

```
echo $0                    — argv0 (often 'sh' or '-sh')
readlink /proc/$$/exe      — actual binary (bash/dash/busybox)
$BASH_VERSION/$ZSH_VERSION — env vars
help /sh --version         — builtin presence check
```

`sh` on Debian/Ubuntu = `dash`; on Alpine/containers = `busybox ash`;
on RHEL = `bash` in posix mode; BSD = `pdksh`/`ash`.

## Feature matrix — what each supports

| Feature | dash/sh | bash | zsh | fish | busybox ash |
|---|---|---|---|---|---|
| `$( )` | ✓ | ✓ | ✓ | `( )` fish | ✓ |
| backticks | ✓ | ✓ | ✓ | ✗ | ✓ |
| `{a,b}` brace | ✗ | ✓ | ✓ | ✗(lists) | ✗ |
| `<(cmd)` proc subst | ✗ | ✓ | ✓ | `(psub)` | ✗ |
| `$'...'` ANSI-C | ✗ | ✓ | ✓ | ✗ | ✗ |
| `[[ ]]` | ✗ | ✓ | ✓ | ✗ | partial |
| `${var,,}`/`^^` | ✗ | bash≥4 | ✓ | ✗ | ✗ |
| arrays `a[i]` | ✗ | ✓ | ✓ | lists | ✗ |
| `$RANDOM` | ✗ | ✓ | ✓ | ✗ | ✓ |
| `shopt`/`setopt` | ✗ | shopt | setopt | ✗ | ✗ |
| `<<<` herestring | ✗ | ✓ | ✓ | ✗ | ✗ |
| `echo -e` escapes | varies | builtin ok | ✓ | differs | varies |
| `<<<`, `${!x}` | ✗ | ✓ | ✓ | ✗ | ✗ |
| `printf %b` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `$$`/`$!`/`$?` | ✓ | ✓ | ✓ | different vars | ✓ |
| `;`/`&`/`\|`/`&&`/`\|\|` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `#` comment | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/dev/tcp` | ✗ | ✓ | ✓ | ✗ | sometimes |

## dash specifics — Debian/Ubuntu `/bin/sh`

- no `<<<`, no `$'...'`, no `{}`, no `[[`, no `${var,,}`
- `echo -e` DOES handle escapes (dash echo honors `-e`? actually dash's
  echo interprets escapes by default — `echo '\x61'` → 'a' — yes!)
- `read` without `-r` mangles backslashes
- `function` keyword NOT supported — `f(){}` only

## busybox ash — Alpine/containers

- minimal — most bash-isms absent
- applets under `/bin`/`/sbin`/`/usr/bin` all busybox links — `nc`/`wget`
  variants may exist as busybox applets — `busybox nc` supports `-e`!
- `awk`/`sed`/`grep`/`find`/`xargs` as applets — feature-limited but real
- `sh` IS busybox ash

## bash — feature-complete

All forms work. `$'...'`, `<<<`, `{a,b}`, `<( )`, `${var,,}`, arrays,
`[[ ]]`, `printf %b`, `declare`, `typeset`, `shopt`, `$BASH_*` vars,
`/dev/tcp/HOST/PORT` — the bash network primitive.

## zsh — mostly superset, some syntax differences

`{a,b}` ok, `<( )` ok, `$'...'` ok. Word splitting differs — unquoted
vars DON'T split by default (`SH_WORD_SPLIT` off) — `$x` with spaces is
one word in zsh! The `IFS`-split tricks fail on zsh.

## fish — a different language entirely

- no `$( )` — use `(cmd)`
- no backticks
- vars are lists — `$x` expands differently
- `&&`/`||` are `and`/`or` in older fish (7+ supports `&&`)
- `string`/`math` builtins replace `$(( ))` (use `math 7*7`)
- `set x y` not `x=y`
- `;`/`|`/`>`/`>>`/`<` work
- `$IFS` absent — `string split` instead

## `sh -c` vs `bash -c` vs `sh` invoked as `bash`

`sh` invoked AS `sh` enters posix mode on bash — `posix` mode limits
some features. `bash -c` full features.

## `cmd.exe` — `windows-cmdi.md`

Separators `&`/`&&`/`||`/`|` — no `;`. Quote = `"` only (no single-quote
grouping). `^` escape. `&&`/`||` semantics same.

## PowerShell — `powershell-injection.md`

`;`/`&`/`|`/`&&`(pwsh7+) — `$( )` is subexpression — `` ` `` is escape.
`-and`/`-or`/`-eq` operators. `|`=pipeline (objects, not text).

## The fallback strategy — write payloads in POSIX common subset

`dash`-safe = works on every POSIX shell:

- `$( )` not `` ` `` (both work; `$( )` nests)
- `;`/`|`/`&`/`&&`/`||` — all work everywhere POSIX
- `>`/`>>`/`<` work
- `$IFS`, `${var}`, `$(())` arithmetic work
- `${var:off:len}` — dash DOES support `${x:o:l}` (POSIX)
- avoid `{}`, `<<<`, `$'...'`, `[[ ]]`, `${var,,}`, `<( )` — bash-isms

## The `$0`/`$SHELL` detection command

```sh
echo "SH=$0 BASH=$BASH_VERSION ZSH=$ZSH_VERSION"
readlink /proc/$$/exe 2>/dev/null
ls -l /bin/sh
```

## Falsifiers

- the shell identified doesn't support the needed construct AND a
  simpler one can't substitute → try another shell's syntax only after
  fingerprinting which

## Output to record

- the resolved shell binary + which syntax tier works
