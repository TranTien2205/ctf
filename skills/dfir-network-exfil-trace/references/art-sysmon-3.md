# Host artifact: Sysmon event 3 (network connect)

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Fields in order: `RuleName, UtcTime, ProcessGuid, ProcessId, Image, User, Protocol, Initiated, SourceIsIpv6, SourceIp, SourceHostname, SourcePort, SourcePortName, DestinationIsIpv6, DestinationIp, DestinationHostname, DestinationPort, DestinationPortName` (OSSEM EventId-3). `Initiated=true` means the local process opened the connection — the exfil direction. Join to process context by `ProcessGuid`, NEVER by PID (PIDs recycle). The event is DISABLED by default in Sysmon — absence is a configuration fact, not innocence. Query: `evtx_query.py --input sysmon.jsonl --event-id 3 --field-contains DestinationIp=. --challenge <n> --class dfir-network-exfil-trace --hypothesis-id h1 --evidence-kind class --answer DestinationIp`.

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
