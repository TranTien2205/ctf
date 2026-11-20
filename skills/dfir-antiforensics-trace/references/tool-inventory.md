# Tool: tools/forensics/artifact_inventory.py

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`--path <bundle> --challenge <n>` — names the artifact families present: registry-transaction-log, recycle-bin, Defender tree. The falsifier's third component: if it names none of the erased-family artifacts, 'nothing erased' is supported.

## Verification

`--help`/`--selftest` before relying on flags. No tool in this list was
assumed; absent tools are routed to `skills/dfir-sherlock-triage/toolchain.md`.
