# Tool: tools/forensics/hive_parse.py

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Hive cell reading — key LastWriteTime (the untamperable registry clock), values as they exist in the primary hive. For tampered hives pair with the .LOG replay reasoning in `reg-*`.

## Verification

`--help`/`--selftest` before relying on flags. No tool in this list was
assumed; absent tools are routed to `skills/dfir-sherlock-triage/toolchain.md`.
