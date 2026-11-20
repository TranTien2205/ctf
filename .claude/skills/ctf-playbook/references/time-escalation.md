# Escalation spending

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

The escalation rungs (chain_match, reclassify,
writeup_search, novel_plan, fanout_sweep, solver_handoff)
each cost one --strategy-used; spending them early is the
point of having them.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
