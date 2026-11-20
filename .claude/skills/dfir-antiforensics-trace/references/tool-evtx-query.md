# Tool: tools/forensics/evtx_query.py

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`--input <jsonl> --event-id <id>` (repeatable for the clear sweep) `--field-contains F=v --challenge <n> --class dfir-antiforensics-trace --hypothesis-id h1 --evidence-kind class [--answer F]` — measured: one 1102 record reported read:2 matched:1, resolved SubjectUserName from inside UserData/LogFileCleared with no path given, and emitted the pre-flag argv.

## Verification

`--help`/`--selftest` before relying on flags. No tool in this list was
assumed; absent tools are routed to `skills/dfir-sherlock-triage/toolchain.md`.
