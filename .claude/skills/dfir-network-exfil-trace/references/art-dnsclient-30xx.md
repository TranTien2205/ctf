# Host artifact: DNS Client 3006/3008

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`Microsoft-Windows-DNS-Client/Operational`. 3006 = query issued (`QueryName, QueryType, QueryOptions, ServerList, IsNetworkQuery, NetworkQueryIndex, InterfaceIndex, IsAsyncQuery`); 3008 = query completed (`QueryName, QueryType, QueryOptions, QueryStatus, QueryResults`) — 3008 is the one carrying the resolved address. Join 3006->3008 on `NetworkQueryIndex`.

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
