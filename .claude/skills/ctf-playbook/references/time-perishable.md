# Perishable solves

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

An unbanked solve ages - flag rotation, challenge fixes, and
the end of the clock all eat pending work. Submit as soon as
the flag verifies.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
