# Negative: not jeopardy

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Attack-defense, machine boxes, AD, live IR - the entry table
hands these to their own routers (ad-service-triage, ir-live-
estate-triage) or out of scope entirely.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
