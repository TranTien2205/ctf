# Workflow: Scope order: system then user

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

HKLM/SYSTEM scope first (louder, fewer), then every user scope independently (NTUSER per user, Startup per user, HKCU classes). 'no persistence' after only the system scope is a scope error.

## Pivot

Workflow covered -> the scenario (`scen-*`) for the bundle shape.
