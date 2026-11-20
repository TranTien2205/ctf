# Ledger before probing

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

tools/state.py records category, target, challenge-name, event at
step 0 - the controller's writeup-search rule and the budget both
read from it. A challenge with no ledger entry has no controller.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
