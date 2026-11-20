# Host artifact: pfirewall.log

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`%systemroot%\system32\LogFiles\Firewall\pfirewall.log`, W3C text. Index columns off the file's own `#Fields:` line: `date time action protocol src-ip dst-ip src-port dst-port size tcpflags tcpsyn tcpack tcpwin icmptype icmpcode info path`, `-` empty, `size` in bytes — sum `size` per `dst-ip` for volume. Logs NOTHING until 'Log dropped packets' or 'Log successful connections' is enabled; the documented split is per-profile `pfirewall_Domain/Private/Public.log` — check all four names. Default max 4,096 KB, old entries deleted at the cap: a missing early record may be ROTATION, not absence — check whether the file starts with the `#Version`/`#Fields` header block or mid-line.

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
