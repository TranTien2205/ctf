# Closing checklist

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

Before the claim leaves this class:

- the state-changing request named (method, path, params)
- the missing/weak defence named (token absent, unbound,
  referrer-only, SameSite gap) with the response that shows it
- the forged request outcome: accepted vs refused, verbatim
- the content-type boundary tested (simple vs preflighted)
- the falsifier status explicit

## Pivot

Checklist complete -> record via hooks; incomplete -> the named gap.
