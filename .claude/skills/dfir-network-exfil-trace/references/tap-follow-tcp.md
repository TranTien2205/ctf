# Tap: -z follow,tcp,<mode>,<stream>

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

One reassembled TCP stream — the bytes as the application saw them. Syntax is
`prot,mode,filter[,range]` where the filter is a stream index or
`ip0:port0,ip1:port1` (tshark(1) on this box).

## Commands

```bash
tshark -r capture.pcapng -q -z follow,tcp,ascii,0
tshark -r capture.pcapng -q -z follow,tcp,hex,0
tshark -r capture.pcapng -q -z follow,tcp,raw,0 > stream0.bin
```

## Modes

`ascii` for printable content, `hex` for a side-by-side dump, `raw` to write
the payload bytes to a file for carving (credentials, uploaded archives).
The output separates directions with a header line per direction change —
read which side sent before quoting.

## Evidence rule

A `follow` chunk is exactly the verbatim excerpt `post-probe` wants. Include
the direction header line so the excerpt proves who sent it.

## Trap

Reassembly hides packet boundaries — a "one request = one chunk" assumption
fails when the sender fragmented deliberately. Timing of chunks needs
`-e tcp.stream -e frame.time_epoch` per packet, not the follow view.

## Pivot

Stream carrying readable commands -> `tools/net_dialog.py` parsing; binary
blob -> `forensics-pcap-carve` territory.
