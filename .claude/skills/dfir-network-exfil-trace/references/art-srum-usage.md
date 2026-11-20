# Host artifact: SRUM network usage table

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`C:\Windows\System32\sru\SRUDB.dat`, table `{973F5D5C-1D90-4944-BE8E-24B94231A174}` 'Network Data Usage Monitor'. Nine columns in order: `AutoIncId, TimeStamp` (OLE Automation date — NOT FILETIME), `AppId, UserId, InterfaceLuid, L2ProfileId, L2ProfileFlags, BytesSent, BytesRecvd`. `AppId`/`UserId` index into `SruDbIdMapTable` — a raw number is never the answer; resolve it. `BytesSent` per app per hour is the host-side volume oracle when no capture exists.

## Query shape

```bash
python3 tools/forensics/evtx_query.py --input <channel>.jsonl --event-id <id> \
  --field-contains <Field>=<needle> --challenge <name> \
  --class dfir-network-exfil-trace --hypothesis-id h1 \
  --evidence-kind class --answer <Field>
```

`--answer` prints the value AND the `hooks.py pre-flag` argv — the value is
never retyped.

## Evidence rule

Quote the event record verbatim: event id, timestamp, and the answering
field. `AppId`-style index values must be resolved through their map table
before being reported.

## Pivot

Artifact family dry after three measured shapes -> next family per
`../SKILL.md` Discipline. Process-side questions -> `dfir-execution-trace`.
