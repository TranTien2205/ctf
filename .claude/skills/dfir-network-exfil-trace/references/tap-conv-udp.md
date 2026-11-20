# Tap: -z conv,udp

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

Per-peer UDP conversations — the same shape as `conv,tcp`, and the same
direction trap: the first pair is B-to-A, the second A-to-B.

## Command

```bash
tshark -r capture.pcapng -q -z conv,udp
```

## Reading the output

UDP carries no stream state, so a long-running channel (DNS tunnelling, QUIC,
a custom UDP protocol) appears as one or a few huge conversations. For DNS
exfil, the classic row is a stub resolver to ONE server with thousands of
queries — pair with `dns,tree` Query Stats.

## Evidence rule

Same quoting rule as TCP. When the question is "one server taking
everything", the `conv,udp` row plus a `dns.qry.name` parent-domain histogram
(`awk -F. '{print $(NF-1)"."$NF}' | sort | uniq -c`) is the paired evidence.

## Trap

UDP conversations keyed by ephemeral ports split a single logical channel
into many rows. Sum by `ip.dst` before concluding "no dominant peer".

## Pivot

High query counts to one resolver -> `dns-tree`, `chan-dns-*` modules.
