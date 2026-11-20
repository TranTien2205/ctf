# Route: evt-record-id-gaps

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Base module: `evt-record-id-gaps.md`. This card answers where its record feeds next.

## Primary question

`q-records-deleted.md`.

## Constraint / partner

`meth-record-vs-number.md`.

## Check before reporting

Artifact + field named? Timestamp interpreted (clear-time vs intrusion-time)? Benign twin excluded?

## Pivot

No new record after three shapes -> next family per `../SKILL.md` Discipline.
