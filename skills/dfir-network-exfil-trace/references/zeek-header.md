# Zeek: conn.log header discipline

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Zeek TSV carries its own header: `head -8 conn.log` prints `#separator`, `#fields`, `#types`. NEVER assume column order — `zeek-cut` reads the header for you: `zeek-cut id.orig_h id.resp_h orig_bytes < conn.log`. A hand-coded `cut -fN` lands on the wrong column when the build's field list differs.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
