# A rejected candidate

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

A verifier's rejection preserves the candidate as rejected -
record it, do not call the flag hook, and retry only through
a bounded feedback loop.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
