# Per-user artifact scoping

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Recycle.Bin is per-SID; PSReadLine history is per-user; SDelete EulaAccepted is per-SID. An artifact absent for the wrong user's SID is not absence — check the SID the question is about.

## Pivot

`corpus-index.md`.
