# Trap: S3 lines do not split on spaces

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Time is [bracketed], Request-URI/Referer/User-Agent quoted - measured 30 naive tokens vs 27 fields. Regex: `\[[^\]]*\]|"[^"]*"|\S+`.

## Guard

Check before the claim it protects - each trap is a way to produce a
plausible-looking wrong answer.

## Pivot

Traps clear -> `meth-*` for the next step.
