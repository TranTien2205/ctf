# Tool: tools/forensics/evtx_query.py

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`--input <channel>.jsonl --event-id <id> --field-contains <F>=<v> --challenge <n> --class dfir-network-exfil-trace --hypothesis-id h1 --evidence-kind class [--answer FIELD]` — the JSONL EVTX route. `--answer` prints the value plus the `pre-flag` argv so the value is never retyped.

## Verification

`--help` / `--selftest` / `which` before relying on any flag — the AGENTS.md
rule. Never claim output from a tool that was not run.

## Pivot

Tool absent -> the sibling tool covering the same question; all local tools
absent -> `tshark`/`capinfos` measured-present route.
