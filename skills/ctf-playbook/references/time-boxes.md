# The time-boxes

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Easy 15-30, medium 30-60, hard 60-120 minutes - the box is
set before the first probe and is a tripwire for escalation,
not a deadline for the flag.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
