# Trap: zcat ** glob needs globstar

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`zcat CloudTrail/**/*.json.gz` without `shopt -s globstar` silently matches ONE level - measured guidance: `find -exec gzip -dc {} +`.

## Guard

Check before the claim it protects - each trap is a way to produce a
plausible-looking wrong answer.

## Pivot

Traps clear -> `meth-*` for the next step.
