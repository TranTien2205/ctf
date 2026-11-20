# Service: ImagePath shape reading

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Outside %windir%/Program Files = suspicious per Microsoft; also suspicious shapes: quoted paths with spaces exploited by unquoted-path hijack (see `mech-unquoted`), `cmd /c`/`powershell -enc` in the path (a command service, not a binary), UNC paths, paths in temp/Public/writable dirs.

## Query

```bash
python3 tools/forensics/evtx_query.py --input system.jsonl --event-id 7045 \
  --order asc --challenge <n> --class dfir-persistence-trace \
  --evidence-kind class --answer ImagePath
```

## Evidence rule

A service claim needs the record AND the fields: 'a new service exists' is
surface; `ImagePath=C:\Users\Public\svc.exe` quoted from the 7045 row is
class evidence.

## Pivot

Service records clean -> scheduled tasks (`task-*`), then registry autostart
(`run-*`).
