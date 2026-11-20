# Service: AccountName tells

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Defaults are localSystem/localService/networkService; anything else (a named user, a machine account, blank/custom) is anomalous per the 4697 rules  -  and `ObjectName` on the key is the field the hive carries.

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
