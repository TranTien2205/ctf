# Route: art-sysmon-22

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Base module: `art-sysmon-22.md`. This card answers where its output feeds.

## Primary consumer

`q-what-inside-dns.md` — the question this artifact most often answers.

## Constraint

`chan-dns-labels.md` — the method or trap that bounds how the artifact's records may be quoted.

## Check before reporting

Which question, which field, which record — and is the value an index needing resolution through its map table (`trap-index-values`)?

## Pivot

Artifact produced no new record after three measured shapes -> next family per `../SKILL.md` Discipline.
