# Tap: -z expert and expert items

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

The dissector's own complaints: malformed packets, checksums, reassembly
gaps, deprecated fields, sequence problems — grouped by severity.

## Command

```bash
tshark -r capture.pcapng -q -z expert
```

## Reading for exfiltration

Deliberately malformed or fragmented exfil often leaves expert chatter
(reassembly failed, bad checksums a craft tool wrote). It is a supporting
signal, not a finding — the volume and direction still come from the flow
taps.

## Evidence rule

Expert items are annotator output; quote them as "tshark flagged X in frame
N", and corroborate with the actual field or payload before treating them as
a finding.

## Trap

A capture written by a lossy sensor shows reassembly gaps that mean sensor
drops, not attacker fragmentation. Pair with Zeek `missed_bytes` reasoning in
`zeek-missed-bytes` when a Zeek bundle accompanies the capture.

## Pivot

Heavy `Reassembled`/`Malformed` on one peer -> `chan-icmp-*` or
`chan-custom-*` inspection of that peer's packets.
