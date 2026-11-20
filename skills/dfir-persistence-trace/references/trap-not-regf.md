# Trap: Non-hive vs truncated hive errors

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

8KB urandom: `ValueError: Could not determine registry hive format`; 4-byte regf stub: `struct.error` at a later offset  -  a stub gets PAST the format sniff. `head -c4` must print `regf` before interpreting a parse failure as 'key absent'.

## Guard

Check this trap BEFORE the claim it protects  -  the failure is silent:
the wrong answer reads as plausible as the right one.

## Pivot

Traps clear -> continue the mechanism sweep (`meth-order`).


## Closing note

Record the reading, not the impression: the corpus exists so that a
verbatim record or a recorded negative  -  not a hunch  -  ends each probe.
