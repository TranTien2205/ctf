# Zeek: ssl.log

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`server_name` (the SNI), `validation_status`, `ja3`/`ja3s` fingerprints where the build logs them, `established`, `resumed`. `server_name` is the client claim; pair with `id.resp_h` from `conn.log` for the observation.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
