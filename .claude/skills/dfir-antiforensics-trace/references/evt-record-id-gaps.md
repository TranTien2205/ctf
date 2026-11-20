# Event: Record-identifier gaps — the signature that survives

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A clear writes 1102; surgical deletion writes NOTHING. The only trace is the identifier sequence itself: `ElfChnk` headers carry first/last record identifiers at +0x18/+0x20, and a gap between chunk N's last id and chunk N+1's first id counts the deleted records and dates the hole against neighbours. `gaps=[(4200, 4310)]` = 109 records gone. The first-probe one-liner in `../SKILL.md` reads these without any EVTX parser.

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
