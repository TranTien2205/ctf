# Recovery cell: File wiped (EFSTMPWP/sdelete) -> quar

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Destroyed: File wiped (EFSTMPWP/sdelete).

## The survivor

quarantine ResourceData — Defender's copy.

## How to read it

This cell is one column of the recovery table — the FIRST place to look after the destroyed artifact is confirmed destroyed. Work the cell's family once; a negative here moves you to the next column, not to a variant of the same query.

## Evidence rule

The survivor must itself be quoted — a column that exists but holds nothing relevant is a recorded negative, closing this cell.

## Pivot

Next column in `rec-wiped-file.md`; all columns dry -> `meth-falsifier`.
