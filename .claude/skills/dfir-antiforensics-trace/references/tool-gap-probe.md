# Tool: The record-identifier gap probe

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The inline python in `../SKILL.md` — struct-only, no EVTX parser needed. Reads `ElfChnk` first/last identifiers at +0x18/+0x20, prints oldest/newest/gaps per .evtx. The `if not ids` guard is load-bearing against header-only stubs.

## Verification

`--help`/`--selftest` before relying on flags. No tool in this list was
assumed; absent tools are routed to `skills/dfir-sherlock-triage/toolchain.md`.
