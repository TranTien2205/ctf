# Field: frame.time_epoch

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Where it lives

Packet timestamp as epoch seconds. The column every timeline merge keys on — `timeline_merge.py` accepts it directly as `:TIMECOL`. Quote it with the row it belongs to; a bare timestamp proves nothing without the peer fields.

## Extraction

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y -e frame.time_epoch ...
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
