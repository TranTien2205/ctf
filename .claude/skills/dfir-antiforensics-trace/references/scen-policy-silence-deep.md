# Deep: scen-policy-silence

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Base scenario: `scen-policy-silence.md`. This card adds the failure modes and the order of checks that keep the scenario honest.

## Failure modes

- The record that answers the question is itself inside the destroyed window -> drop to the `rec-*` column for that artifact.
- The benign twin (rotation, truncation, collection scope) was not excluded -> run the pairing check named in the scenario's own module.
- A timestamp was read as intrusion-time when it is clear-time (`trap-1102-time`).

## Order

Cheapest discriminator first: the gap probe and the clear sweep cost nothing and settle 'was anything erased' before any recovery work.

## Pivot

`question-map.md`.
