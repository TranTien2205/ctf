# Field: icmp fields

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Where it lives

ICMP has no ports — `icmp.type` (8 echo request, 0 reply), `data.len` for payload size. ICMP tunnelling = many echo requests with fat `data_len` to one peer. Filter `icmp` and check `data.len` distribution; normal pings are 32-64 bytes, tunnels run hundreds.

## Extraction

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y -e icmp fields ...
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
