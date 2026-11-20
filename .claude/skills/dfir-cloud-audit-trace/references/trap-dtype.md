# Trap: dtype=object is not optional

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Measured pandas 2.3.3: a TSV account-id column with one empty cell becomes float64 and `123456789012` prints `123456789012.0` - a silently wrong answer. dtype=object on every read.

## Guard

Check before the claim it protects - each trap is a way to produce a
plausible-looking wrong answer.

## Pivot

Traps clear -> `meth-*` for the next step.
