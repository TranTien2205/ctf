# Zeek: JSON-format zeek logs

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Some bundles ship JSON instead of TSV (`*_json.log` or `zeek -e redef LogAscii::use_json=T`). Same field names, jq over `jq -r '[.ts,.["id.orig_h"],.["id.resp_h"],.orig_bytes]|@tsv'` — the id.* fields are dotted inside the JSON key itself.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
