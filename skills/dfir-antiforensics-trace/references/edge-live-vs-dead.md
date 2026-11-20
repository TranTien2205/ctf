# Live vs dead capture semantics

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A bundle captured live may include in-flight records a dead copy lacks; conversely unflushed writes are absent live and present after shutdown. Which capture mode the bundle used bounds what 'missing' can mean.

## Pivot

`corpus-index.md`.
