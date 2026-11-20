# Zeek: files.log

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

One row per seen file: `fuid tx_hosts rx_hosts conn_uids source analyzers mime_type filename duration md5 sha1 sha256 total_bytes missing_bytes overflow_bytes`. `tx_hosts` vs `rx_hosts` gives direction; `missing_bytes`/`overflow_bytes` mark incomplete reassembly; `filename` is a claim. `source` names the protocol that carried it.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
