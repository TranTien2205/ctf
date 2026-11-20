# Zeek: uid pivot

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Every protocol log (`dns.log`, `http.log`, `ssl.log`, `files.log`, `notice.log`) carries `uid` joining back to `conn.log`. The pattern: find the row in `conn.log` (volume), take its `uid`, grep it in `http.log`/`ssl.log`/`files.log` for the what.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
