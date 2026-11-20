# Field: frame.time_delta

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Where it lives

Seconds since the previous DISPLAYED packet — depends on the active filter, so recompute per-flow: `-Y 'tcp.stream==N' -e frame.time_delta`. Beacon cadence arithmetic in `beacon-io-stat` uses this correctly; a delta over a mixed filter is meaningless.

## Extraction

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y -e frame.time_delta ...
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
