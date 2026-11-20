# Deep dive: Deep: SDDL in TaskCache

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`SecurityDescriptor` in `Tasks\{GUID}` is SDDL. `O:<sid>` is the owner; `D:` ACEs grant/deny. The value survives the XML's deletion, so on a 'task deleted, who made it' question this is the artifact. Resolve machine SIDs via SAM `Domains\Account\Users`.

## Use

Depth for when the row-level module is not enough  -  cite this file's
artifact and offset when the claim rests on the decoded detail.

## Pivot

Deep read done -> back to the scenario (`scen-*`) or the matrix.


## Closing note

Record the reading, not the impression: the corpus exists so that a
verbatim record or a recorded negative  -  not a hunch  -  ends each probe.
