# Route: q-records-deleted

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Base module: `q-records-deleted.md`. This card answers where its record feeds next.

## Primary question

`evt-record-id-gaps.md`.

## Constraint / partner

`meth-gap-vs-event.md`.

## Check before reporting

Artifact + field named? Timestamp interpreted (clear-time vs intrusion-time)? Benign twin excluded?

## Pivot

No new record after three shapes -> next family per `../SKILL.md` Discipline.
