# Host artifact: Transfer queue qmgr.db

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`C:\ProgramData\Microsoft\Network\Downloader\qmgr.db` (`qmgr0.dat`/`qmgr1.dat` pre-Windows 10) — a SQLite/EDS store of transfer jobs. `RemoteName` is the URL fetched or pushed, `LocalName` where it landed. A job to an odd `RemoteName` is the 'who asked for that URL' answer on the host side.

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
