# Scenario: Worked DNS-tunnel case sketch

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

io,phs shows outsized DNS share -> dns,tree Qname Len Max >> Average + `4th Level or more` labels -> `dns.qry.name.len > 50` filter hit + parent-domain concentration -> alphabet/entropy check (hex: alphabet regex, base32/64: entropy) -> `dns_exfil.py --pcap` reassembles -> carved bytes get carved per `forensics-pcap-carve`. Each stage quotes its row.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
