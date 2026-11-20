# Event: Sysmon 16 — configuration changed

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`ServiceConfigurationChange` — 'logs changes in the Sysmon configuration - for example when the filtering rules are updated', also unfilterable. A config-only Sysmon kill writes 16 and NO 4 — the distinction that names which tamper happened.

## Query shape

```bash
python3 tools/forensics/evtx_query.py --input <channel>.jsonl \
  --event-id <id> --challenge <name> --class dfir-antiforensics-trace \
  --hypothesis-id h1 --evidence-kind class [--answer FIELD]
```

## Evidence rule

Quote the event id, channel, timestamp, and the answering field verbatim.
A clear-time timestamp answers 'when was it cleared' — never 'when did the
intrusion start'.

## Pivot

Clear/disable events clean -> the deletion/timestomp families; all clean ->
the falsifier block in `../SKILL.md`.
