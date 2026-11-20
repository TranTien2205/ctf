# Method: The class falsifier, operational

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Close the class on: every .evtx reports gaps=[] with oldest consistent with retention AND the clear/disable sweep (`--event-id 1102 --event-id 104 --event-id 1100 --event-id 4719 --event-id 1013`) reports matched:0 AND artifact_inventory names no registry-transaction-log / recycle-bin / Defender tree. All three components must be quoted.

## Why

Anti-forensics answers are unusually easy to overclaim — every technique
here also has a benign producer (rotation, truncation, collection scope).
The two-answer rule and the falsifier block are what keep the class honest.

## Pivot

Method exhausted -> `rec-*` recovery columns; all columns dry -> the
falsifier block.
