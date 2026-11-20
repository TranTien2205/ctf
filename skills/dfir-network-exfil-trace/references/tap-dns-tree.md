# Tap: -z dns,tree

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

One tree with everything a DNS question needs: `rcode`, `opcodes`,
`Query/Response` split, `Query Type` (leaf `TXT (Text strings)`), `Class`,
`Payload size`, `Query Stats -> Qname Len` Count/Average/Min/Max,
`Label Stats -> 1st/2nd/3rd/4th Level or more`, `Response Stats -> no. of
answers`, `Service Stats -> request-response time (msec)` and `no. of
retransmissions`. Leaf names measured on this box (tshark 4.0.7).

## Command

```bash
tshark -r capture.pcapng -q -z dns,tree
```

## Reading for tunnelling

- `Qname Len` Max far above Average -> over-long names carrying payload.
- `4th Level or more` label count high -> stacked labels under one parent.
- `TXT` share unusual for the capture size -> record-type mixing.
- `no. of retransmissions` high -> retransmitted chunks; de-duplicate before
  reassembly (the working code is `skills/ctf-forensics/network-advanced.md`).

## Evidence rule

Quote the specific leaf lines (e.g. `Qname Len ... Average 38`) — the tree is
wide, and a vague "dns,tree showed anomalies" is not quotable.

## Trap

`dns,tree` counts every DNS packet including refused/failed responses. A
failure storm and a tunnel share the high-count shape; check `rcode` first.

## Pivot

Over-long names -> `fld-dns-qry-name-len`, `tool-dns-exfil`.
