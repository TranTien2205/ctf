# Field: eth.src / eth.dst

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Where it lives

Layer-2 identity — matters only inside one L2 segment (ARP-poisoned capture, local tap). For an endpoint capture it is constant per host and usually noise; do not report it as an answer.

## Extraction

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y -e eth.src ...
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
