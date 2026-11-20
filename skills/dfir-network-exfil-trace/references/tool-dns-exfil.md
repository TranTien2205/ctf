# Tool: tools/forensics/dns_exfil.py

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`--pcap cap` or `--names file` `[--domain suffix]` — reassembles data smuggled in DNS query names: label decode, chunk ordering, retransmission de-dup, controlled-suffix stripping. Auto-detects the domain suffix when `--domain` is omitted. `--selftest` proves it offline.

## Verification

`--help` / `--selftest` / `which` before relying on any flag — the AGENTS.md
rule. Never claim output from a tool that was not run.

## Pivot

Tool absent -> the sibling tool covering the same question; all local tools
absent -> `tshark`/`capinfos` measured-present route.
