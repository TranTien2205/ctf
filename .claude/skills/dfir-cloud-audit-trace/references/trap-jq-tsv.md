# Trap: @tsv on an object exits 5

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

jq 'cannot be tsv-formatted, only array' - group_by maps must emit arrays before @tsv; the error is a pipeline-shape bug, not a data gap.

## Guard

Check before the claim it protects - each trap is a way to produce a
plausible-looking wrong answer.

## Pivot

Traps clear -> `meth-*` for the next step.
