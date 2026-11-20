# Closing checklist

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Before reporting any answer

- The number/name is quoted verbatim from a tool row, headers visible.
- Direction is named (Tx / `->` / orig / toserver / Initiated).
- Unit is named (wire bytes vs payload; packets vs bytes).
- Window is named (capture epoch bounds or artifact coverage).
- Claims (SNI, Host, filename) are labelled claims; observations ground
  the sentence.
- Index values are resolved through their map tables.
- Every negative is recorded with the filter/tap that produced it.

## Before closing the class

- Each question mapped to its artifact and either answered or falsified.
- The falsifier block in `../SKILL.md` is itself quoted when the verdict
  is 'nothing left this host'.
- Cross-class handoffs are named: process -> dfir-execution-trace, cloud
  API -> dfir-cloud-audit-trace, carved content -> forensics-pcap-carve.
