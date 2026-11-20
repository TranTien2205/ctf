# Event: Absence is collection scope until proven

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A channel absent from the bundle is a collection fact first. The falsifier shape requires the clear-and-disable sweep to return matched:0 AND artifact_inventory to name no erased-family artifacts. `dfir-filesystem-timeline` measured a fresh NTFS listing no $J at all — the journal is created on first use, so 'no journal' is creation scope, not deletion.

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
