# Host artifact: Linux iptables LOG lines

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`/var/log/syslog` or `kern.log`: `IN= OUT= SRC= DST= LEN= PROTO= SPT= DPT=` per packet. Sum `LEN` per `DST` for the volume answer — `grep 'DST=185' | sed 's/.*LEN=\([0-9]*\).*/\1/' | awk '{s+=$1}END{print s}'`. Presence depends on a LOG rule existing; absence says nothing.

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
