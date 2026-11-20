# Agent-written artifacts

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

flag.txt, evidence.txt, repro.sh written by an automated
solver are claims - an independent verifier must accept the
exact candidate before the flag gate sees it.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
