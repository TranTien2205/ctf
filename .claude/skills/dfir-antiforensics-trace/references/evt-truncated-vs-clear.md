# Event: Truncated file vs cleared file

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A header-only `.evtx` (valid `ElfFile\x00`, no `ElfChnk` at 0x1000) is TRUNCATED/carved/stub — NOT a clear. A clear still contains one chunk and record id 1. The `if not ids` guard exists because the unguarded loop dies with IndexError on the first stub and hides every other channel — measured on the 44-byte fixtures here.

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
