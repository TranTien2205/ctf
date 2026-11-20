# Tool: tools/forensics/pcap_parse.py

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Subcommands `convs|dns|ascii|follow|http|fields` — a stdlib pcap reader for the carve workflow: conversations, DNS query list, ascii streams, single-stream follow, HTTP object carve to `--out`, per-packet field carve. Use when tshark is missing or the bundle's pcap subset suffices.

## Verification

`--help` / `--selftest` / `which` before relying on any flag — the AGENTS.md
rule. Never claim output from a tool that was not run.

## Pivot

Tool absent -> the sibling tool covering the same question; all local tools
absent -> `tshark`/`capinfos` measured-present route.
