# tools/state.py

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

The ledger: category, target, challenge-name, event at step
0; --show to resume; --strategy-used to spend an escalation
rung. The controller reads it for every decision.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
