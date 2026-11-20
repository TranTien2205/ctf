# Field: tcp.payload / tcp.len

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Where it lives

`tcp.len` is payload bytes per segment — the honest 'how much data' counter when the question means data, not wire. `SUM(tcp.len)` per direction per stream is the defensible figure; `frame.len` over-counts by headers.

## Extraction

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y -e tcp.payload ...
```

All field names were checked against `tshark -G fields` on this box; verify a
new name with `tshark -G fields | awk -F'\t' '$1=="F"{print $3}' | grep <name>`
before relying on it.

## Evidence rule

A field value quoted without its row context (time, peers, stream) is a
fragment, not an answer. Quote the whole `-T fields` line.

## Pivot

Field answers the question -> stop; field shows nothing after three shapes ->
change artifact family (`../SKILL.md`, Discipline).
