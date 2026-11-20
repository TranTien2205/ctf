# Tool: tools/forensics/timeline_merge.py

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`--source PATH:TIMECOL:LABEL` (repeatable; TIMECOL = name, 0-based index, or dotted path for JSONL), `--filetime` per source, `--gap N`, `--challenge <n>` — merges net.csv with sysmon.jsonl on one UTC axis. Counts unparsed rows instead of dropping them; reports largest gaps. 18/18 offline cases in `tools/forensics/selftest.py`.

## Verification

`--help` / `--selftest` / `which` before relying on any flag — the AGENTS.md
rule. Never claim output from a tool that was not run.

## Pivot

Tool absent -> the sibling tool covering the same question; all local tools
absent -> `tshark`/`capinfos` measured-present route.
