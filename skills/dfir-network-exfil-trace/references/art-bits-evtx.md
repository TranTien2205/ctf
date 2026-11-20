# Host artifact: BITS client Operational channel

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`Microsoft-Windows-Bits-Client/Operational`: 3 job created, 59 started transferring a file, 60 stopped transferring (status code = outcome), 4 job completed (user, job name, job id, owner, file count). Upload and download emit the SAME 3-59-60-4 sequence — direction comes from `RemoteName` vs `LocalName`, never from the event ids. Per-event field lists are UNVERIFIED here; read them off the local provider manifest.

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
