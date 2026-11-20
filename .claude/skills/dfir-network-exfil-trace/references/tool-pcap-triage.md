# Tool: tools/forensics/pcap_triage.py

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`--input cap --challenge <n> [--top N] [--names] [--beacon-peer ADDR] [--display-filter EXPR] [--class dfir-network-exfil-trace --hypothesis-id h1 --evidence-kind class]` — the offline triage: who talked to whom, how much left, is it periodic. Emits the hooks-shaped record when the gate flags are supplied. Stdlib-only — the fallback when tshark is absent.

## Verification

`--help` / `--selftest` / `which` before relying on any flag — the AGENTS.md
rule. Never claim output from a tool that was not run.

## Pivot

Tool absent -> the sibling tool covering the same question; all local tools
absent -> `tshark`/`capinfos` measured-present route.
