# Workflow: Negatives are recorded

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Each family read ends with either a verbatim record or a negative line: 'Run HKLM clean  -  checked keys X,Y on hive SOFTWARE.rw'. The falsifier is an AND of negatives, so unrecorded negatives block closure.

## Pivot

Workflow covered -> the scenario (`scen-*`) for the bundle shape.
