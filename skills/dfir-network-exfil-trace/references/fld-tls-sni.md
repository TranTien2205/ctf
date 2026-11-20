# Field: tls.handshake.extensions_server_name

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Where it lives

The SNI — the only destination name available for encrypted sessions without a keylog. It is a CLIENT CLAIM: the process asked for this name, but `ip.dst` is where bytes went. When the two disagree (domain fronting, ESNI/ECH), ground the answer on `ip.dst` and quote SNI only as intent.

## Extraction

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y -e tls.handshake.extensions_server_name ...
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
