# Splitting by strength

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Categories split across the team by strength - two people on
one challenge only when both are otherwise blocked.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
