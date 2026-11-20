# Deep: Wire vs payload for 'bytes left'

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`endpoints,ip` Tx Bytes counts wire bytes. For payload, `SUM(tcp.len)`+`SUM(udp.length-8)` per direction, or Zeek `orig_bytes`. Report the figure with its unit named — '9,896 wire bytes (Tx Bytes) / ~8,800 payload bytes' is a complete answer.

## Evidence rule

The deep card refines interpretation; the quotable row still comes from the base question's own probe.

## Pivot

`q-bytes-left-host.md` for the procedure; `meth-answer-shape` for the reporting checklist.
