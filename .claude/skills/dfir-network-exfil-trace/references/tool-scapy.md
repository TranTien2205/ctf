# Tool: scapy 2.6.1

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Installed. `PcapReader` streams big captures (`for p in PcapReader('cap'): ...`); `rdpcap` loads everything — dies on multi-GB files. For custom field pulls beyond tshark fields, or packet-crafting verification fixtures.

## Verification

`--help` / `--selftest` / `which` before relying on any flag — the AGENTS.md
rule. Never claim output from a tool that was not run.

## Pivot

Tool absent -> the sibling tool covering the same question; all local tools
absent -> `tshark`/`capinfos` measured-present route.
