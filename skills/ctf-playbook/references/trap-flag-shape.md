# Trap: flag-shaped string

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

A string matching the flag format in source or output is a
candidate, not a flag - the pre-flag gate is the only writer
of solved status.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
