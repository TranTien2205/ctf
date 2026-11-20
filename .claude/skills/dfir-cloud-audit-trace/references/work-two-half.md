# Workflow: The two-record claim

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Attribution needs BOTH the identity record (userIdentity verbatim) and the action record (eventName + target field) - a name without the action is identity-only; an action without the identity is activity-only.

## Pivot

Workflow covered -> `scen-*` for the bundle shape.
