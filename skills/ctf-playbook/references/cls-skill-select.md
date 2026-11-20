# tools/skill_select.py

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Which skill to open once the class is named - reads the
registry and the observation (or --source). Its answer is
the router, and it is deterministic.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
