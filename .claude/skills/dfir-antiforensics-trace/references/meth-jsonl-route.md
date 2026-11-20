# Method: The JSONL route day zero

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

With no EVTX parser: already-converted `.jsonl` bundles go through `evtx_query.py` — `--input`, `--event-id` (repeatable), `--field-contains`, `--answer`. The record-id gap probe needs raw .evtx bytes; on a JSONL-only bundle the identifier check is per-record EventRecordID sorting instead.

## Why

Anti-forensics answers are unusually easy to overclaim — every technique
here also has a benign producer (rotation, truncation, collection scope).
The two-answer rule and the falsifier block are what keep the class honest.

## Pivot

Method exhausted -> `rec-*` recovery columns; all columns dry -> the
falsifier block.
