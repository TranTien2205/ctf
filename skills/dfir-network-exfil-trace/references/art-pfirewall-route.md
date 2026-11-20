# Route: art-pfirewall

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Base module: `art-pfirewall.md`. This card answers where its output feeds.

## Primary consumer

`q-bytes-left-host.md` — the question this artifact most often answers.

## Constraint

`trap-rotation.md` — the method or trap that bounds how the artifact's records may be quoted.

## Check before reporting

Which question, which field, which record — and is the value an index needing resolution through its map table (`trap-index-values`)?

## Pivot

Artifact produced no new record after three measured shapes -> next family per `../SKILL.md` Discipline.
