# Service: Driver-type services

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

ServiceType hex on 7045, Type bitmask on the key: 0x1/0x2/0x8 driver values loading into the kernel are the higher-signal rows in the 4697 triage rules  -  a user-mode service is quieter but a driver service at boot is the louder tamper.

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
