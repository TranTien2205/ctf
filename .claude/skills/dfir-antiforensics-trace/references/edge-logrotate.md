# Edge: logrotate vs deletion

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Rotated-but-shipped logs are complete coverage; rotated-and-not-shipped is collection scope; a gap INSIDE one file is neither — the distinction is the rotation config + which files the bundle contains.

## Pivot

`corpus-index.md`; `meth-falsifier` when every shape is benign.
