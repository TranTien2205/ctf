# Tool: tools/forensics/recycle_i.py + info2.py

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

$I record parsing: original path + deletion FILETIME; info2.py covers the pre-Vista INFO2 format. The $I row is the two-answer record for deletions.

## Verification

`--help`/`--selftest` before relying on flags. No tool in this list was
assumed; absent tools are routed to `skills/dfir-sherlock-triage/toolchain.md`.
