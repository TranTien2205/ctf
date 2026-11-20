# Trap: sitting on one challenge

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Past the stuck threshold, parking and returning beats sitting
- a challenge consumes clock whether or not it is being
worked, and other solves are perishable.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
