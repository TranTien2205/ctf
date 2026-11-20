# Deep: Chunk decoding discipline

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`dns_exfil.py` emits the byte stream; the byte stream is then a carving problem (magic bytes -> file type -> `forensics-pcap-carve`). Quote both the labels AND the decoded head bytes.

## Evidence rule

The deep card refines interpretation; the quotable row still comes from the base question's own probe.

## Pivot

`q-what-inside-dns.md` for the procedure; `meth-answer-shape` for the reporting checklist.
