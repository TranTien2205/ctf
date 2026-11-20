# tools/decide.py

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

The controller - what the next step is, enforcing budgets
(5 probes / 15 min per class, 25 / 45 overall) and the
escalation order. The agent proposes; decide.py decides.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
