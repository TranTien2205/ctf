# Trap: Parser opens r+b

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

impacket winregistry.py:209 `open(hive,'r+b')`  -  a read-only evidence copy raises PermissionError errno 13. cp + chmod u+w first; measured here.

## Guard

Check this trap BEFORE the claim it protects  -  the failure is silent:
the wrong answer reads as plausible as the right one.

## Pivot

Traps clear -> continue the mechanism sweep (`meth-order`).
