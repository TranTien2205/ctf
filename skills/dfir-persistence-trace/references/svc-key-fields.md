# Service: Service key fields in SYSTEM hive

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`<set>\Services\<name>`: `ImagePath`, `Type` (bitmask  -  0x10 own / 0x20 share / 0x1 kernel / 0x2 fs driver / 0x4 adapter / 0x8 recogniser / 0x100 interactive), `Start` (0 boot / 1 system / 2 auto / 3 manual / 4 disabled  -  only 0-2 survive reboot), `ObjectName` (account), `FailureCommand`, and `Parameters\ServiceDll` when the host is svchost.

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
