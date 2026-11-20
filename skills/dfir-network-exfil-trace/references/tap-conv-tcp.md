# Tap: -z conv,tcp (conversations)

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

Per-peer TCP conversations with frames and bytes in BOTH directions, relative
start, and duration. This is the ranking step for "which external address
carried the bulk".

## Command

```bash
tshark -r capture.pcapng -q -z conv,tcp
```

## Reading the output — direction trap

Each row prints `addrA:portA <-> addrB:portB` then TWO byte/frame pairs. The
first pair is B-to-A (`<-`), the second is A-to-B (`->`). Measured fixture row:
`10.10.10.5:50000 <-> 185.199.0.7:443   20 1,880 bytes   20 9,080 bytes`.
"Bytes sent by A" is the SECOND pair — reading the first column as "sent"
inverts every exfiltration answer in the report.

## Evidence rule

Quote the full row verbatim, including both direction pairs. A retyped byte
count is not evidence; `post-probe` requires the quoted line to be a substring
of the real output.

## Trap

`conv,tcp` counts wire bytes including headers, so a "how much data" question
needs payload-level fields (`-e tcp.payload` length) when the question means
data, not wire.

## Pivot

Rank by the `->` column away from the internal host. The top external peer is
the follow target: `-z follow,tcp,ascii,<stream>` or the field extraction in
`fld-tcp-stream.md`.
