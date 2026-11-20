# Field: dns.qry.name

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Where it lives

The queried name — the carrier string for DNS exfiltration. Harvest outbound-only with `-Y 'dns.flags.response==0'` so answers (which echo the name) do not double-count. Parent-domain histogram: `awk -F. '{print $(NF-1)"."$NF}' | sort | uniq -c`.

## Extraction

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y -e dns.qry.name ...
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
