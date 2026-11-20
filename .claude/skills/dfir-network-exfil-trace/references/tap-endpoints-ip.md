# Tap: -z endpoints,ip

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

The direct "how much left this host" answer: `Packets | Bytes | Tx Packets |
Tx Bytes | Rx Packets | Rx Bytes` per host. `Tx Bytes` is the volume outbound
from that host — never sum a conversation table by hand when this row exists.

## Command

```bash
tshark -r capture.pcapng -q -z endpoints,ip
```

## Measured

On a 48-packet scapy fixture (20 TCP frames of 400-byte payload out, 20 ACKs
back, 8 DNS TXT queries): `10.10.10.5  48  11776  28  9896  20  1880`.
`Tx Bytes` 9896 answered "how much left"; `Bytes` 11776 is bidirectional and
is NOT the answer.

## Evidence rule

Quote the row plus the column header line so the `Tx`/`Rx` split is visible in
the excerpt. `Tx` is transmit; `Rx` is receive.

## Trap

Bytes are wire bytes. For a "data exfiltrated" question, say whether the
figure came from `endpoints` (wire) or a payload sum — the number differs by
header overhead and both are defensible, but the report must name which.

## Pivot

Host with the largest `Tx Bytes` -> `conv,tcp`/`conv,udp` for its peers.
