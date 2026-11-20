# Field: ip.ttl

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Where it lives

Time-to-live per packet. A TTL far from the sender-OS defaults (64 Linux, 128 Windows, 255 network gear) hints at crafted packets or an unexpected hop count. Corroborating tell only — never a volume field.

## Extraction

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y -e ip.ttl ...
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
