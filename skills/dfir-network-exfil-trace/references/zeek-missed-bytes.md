# Zeek: missed_bytes

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`missed_bytes > 0` means the SENSOR dropped payload: `orig_bytes` under-counts and any volume answer from it is a floor, not the truth. Report the under-count explicitly: 'at least N bytes, sensor missed M'.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
