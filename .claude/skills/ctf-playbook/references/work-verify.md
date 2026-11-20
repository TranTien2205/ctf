# Verification through the gate

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

A flag candidate passes hooks.py pre-flag from a live response
or supplied artifact - agent-written flag.txt is a claim until
an independent verifier accepts the exact candidate.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
