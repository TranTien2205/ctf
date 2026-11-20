# Host artifact: Security 5156 (WFP connection allowed)

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Needs the *Audit Filtering Platform Connection* subcategory enabled. Fields: `Application` (device path like `\device\harddiskvolume2\x.exe` — match the basename, not C:\...), `Direction`, `SourceAddress`, `SourcePort`, `DestAddress`, `DestPort`, `Protocol` (numeric: 1 ICMP, 6 TCP, 17 UDP, 47 GRE, 50 ESP, 51 AH), `FilterRTID`, `LayerName`. `Direction` is a message-table token — `%%14592` inbound is documented; `%%14593` outbound is UNVERIFIED here, decode against the local provider before quoting.

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
