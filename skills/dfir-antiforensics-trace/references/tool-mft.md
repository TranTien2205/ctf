# Tool: tools/forensics/mft_parse.py + usn_parse.py

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Deleted/unallocated $MFT records and $J reason filtering — the timestomp divergence, the 0x8000/0x200 reads, and the sdelete rename-burst all come from these.

## Verification

`--help`/`--selftest` before relying on flags. No tool in this list was
assumed; absent tools are routed to `skills/dfir-sherlock-triage/toolchain.md`.
