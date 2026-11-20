# Method: Error-code grouping

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`group_by(.userIdentity.accessKeyId) | map([key, errorCode, count])` - the denied-burst signature. Build an ARRAY before `@tsv`: object input exits 5 'cannot be tsv-formatted'.

## Discipline

Each method keeps the evidence rule: the answer is a quoted record;
the method only gets you to it.

## Pivot

Method spent -> `scen-*` for the bundle shape.
