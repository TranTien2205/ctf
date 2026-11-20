# Field: dns.qry.type

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Where it lives

Record type. 16 is TXT, 10 is NULL, 15 MX, 5 CNAME, 2 NS, 255 ANY. `-Y 'dns.qry.type in {10,16}'` is the verified tunnel tell — TXT/NULL carry the fattest arbitrary payloads. A tunnel using A-record-sized labels does not match this filter, so a miss here does not close the channel.

## Extraction

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y -e dns.qry.type ...
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
