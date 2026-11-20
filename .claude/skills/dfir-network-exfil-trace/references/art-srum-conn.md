# Host artifact: SRUM connectivity table

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Companion table `{DD6636C4-8929-4683-974E-22C046A43763}` 'Network Connectivity Usage Monitor' (libyal esedb-kb) — connection events per interface/app. Needs an ESE reader: neither `esedbexport` nor python `libesedb` is installed here today; install route is `skills/dfir-sherlock-triage/toolchain.md`. Usage once installed: `esedbexport [-c codepage] [-l logfile] [-m mode] [-t target] [-T table] source` writes a `<base>.export/` of TSV tables.

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
