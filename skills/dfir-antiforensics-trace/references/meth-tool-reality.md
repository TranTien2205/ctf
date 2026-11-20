# Method: Tool reality on this box

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Measured 2026-09-28: `command -v` finds NONE of evtx_dump, chainsaw, hayabusa, vshadowinfo, vshadowmount, regripper, reglookup, regipy. Until the rank-1 apt line in `skills/dfir-sherlock-triage/toolchain.md` runs, the whole capability is: the record-gap one-liner + `evtx_query.py` over converted JSONL + the forensics tools in `tools/forensics/`. Never write a command that imports an absent tool.

## Why

Anti-forensics answers are unusually easy to overclaim — every technique
here also has a benign producer (rotation, truncation, collection scope).
The two-answer rule and the falsifier block are what keep the class honest.

## Pivot

Method exhausted -> `rec-*` recovery columns; all columns dry -> the
falsifier block.
