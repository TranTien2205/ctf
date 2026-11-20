# Field table: sourceIPAddress

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Caller's IP as AWS saw it, `AWS Internal/<n>` for service-mediated calls - network evidence, not identity.

## Pivot

Field mapped -> the ev-* module for the call that carries it.
