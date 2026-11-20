# Zeek: zeek-cut practicals

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`zeek-cut ts uid id.orig_h id.resp_h id.resp_p orig_bytes < conn.log` then sort/awk. `zeek-cut -d,` for CSV. Never `awk -F'\t'` by position until the `#fields` line has been counted for THIS file.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
