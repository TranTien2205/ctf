# Field: tcp.stream

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Where it lives

Stream index joining every packet of one TCP conversation. Feed it to `-z follow,tcp,ascii,<idx>` and to per-stream byte sums. Two flows to the same server get different indices — group by index, not by socket pair, when reconnects happened.

## Extraction

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y -e tcp.stream ...
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
