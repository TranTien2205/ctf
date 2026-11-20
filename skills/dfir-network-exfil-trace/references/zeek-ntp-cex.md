# Zeek: non-conn logs for exfil

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`ntp.log`, `dhcp.log`, `kerberos.log`, `smtp.log` exist in the same bundle and carry their own volumes. An exfil channel over an unusual protocol shows in `conn.log` `service` column first, then in the protocol log for the what.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
