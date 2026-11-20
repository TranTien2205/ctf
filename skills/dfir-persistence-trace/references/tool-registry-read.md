# Tool route: impacket registry-read.py

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

The only hive reader on this box (banner Impacket v0.14.0.dev0): `enum_key`/`enum_values`/`get_value`/`get_class`/`walk`, each with `-name`. Needs r+b and a `regf` magic check. Path: `/usr/share/doc/python3-impacket/examples/registry-read.py`.

## Evidence rule

Tool output is the excerpt to quote; the record field inside it is the
evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.


## Closing note

Record the reading, not the impression: the corpus exists so that a
verbatim record or a recorded negative  -  not a hunch  -  ends each probe.
