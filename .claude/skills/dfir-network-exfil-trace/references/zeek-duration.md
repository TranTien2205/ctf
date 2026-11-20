# Zeek: duration

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Seconds the connection lived (`-` when not measured). Long duration + small steady writes = shell/C2 shape; long duration + one big write = transfer. Sort numeric: `sort -t'\t' -k<durcol> -rn`.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
