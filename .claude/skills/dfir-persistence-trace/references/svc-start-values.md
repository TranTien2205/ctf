# Service: Start value arithmetic

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

0=boot (driver, smss loads), 1=system (kernel init), 2=auto (SCM at startup), 3=manual (not persistence  -  something ELSE starts it, and that something is the answer), 4=disabled. A 'persistent service' claim with Start=3/4 is wrong  -  find the starter instead.

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
