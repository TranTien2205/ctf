# Recovery cell: Security log cleared (1102/gap) -> usn

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Destroyed: Security log cleared (1102/gap).

## The survivor

$J 0x100/0x200 records — file operations survived.

## How to read it

This cell is one column of the recovery table — the FIRST place to look after the destroyed artifact is confirmed destroyed. Work the cell's family once; a negative here moves you to the next column, not to a variant of the same query.

## Evidence rule

The survivor must itself be quoted — a column that exists but holds nothing relevant is a recorded negative, closing this cell.

## Pivot

Next column in `rec-security-cleared.md`; all columns dry -> `meth-falsifier`.
