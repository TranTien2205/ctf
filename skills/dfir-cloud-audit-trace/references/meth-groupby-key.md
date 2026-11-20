# Method: Group by accessKeyId

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Every identity question pivots on `.userIdentity.accessKeyId` first (one key = one row-set), then splits by eventName - the recon-then-act boundary emerges per key.

## Discipline

Each method keeps the evidence rule: the answer is a quoted record;
the method only gets you to it.

## Pivot

Method spent -> `scen-*` for the bundle shape.
