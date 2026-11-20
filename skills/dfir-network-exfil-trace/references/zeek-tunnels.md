# Zeek: tunnel_parents

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Last conn.log column: uids of encapsulating flows when this conn was inside a tunnel (TEREDO, AYIYA, GTP, SOCKS). A `tunnel_parents` value means the outer uid's protocol is the carry — check `conn.log` for the parent uid to see the real transport.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
