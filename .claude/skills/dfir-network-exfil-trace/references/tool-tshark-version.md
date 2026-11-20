# Tool: tshark on this box

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

tshark 4.0.7 measured. Capinfos companion: `-a` start, `-e` end, `-c` count, `-z` size. `tshark -G currentprefs` greps the real preference names (tls.keylog_file line 5387, ssh.keylog_file 5019, wg.keylog_file 5630). `tshark -G fields` is the field-name oracle.

## Verification

`--help` / `--selftest` / `which` before relying on any flag — the AGENTS.md
rule. Never claim output from a tool that was not run.

## Pivot

Tool absent -> the sibling tool covering the same question; all local tools
absent -> `tshark`/`capinfos` measured-present route.
