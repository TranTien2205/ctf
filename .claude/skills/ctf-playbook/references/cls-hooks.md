# tools/hooks.py

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

The write gate: post-probe verdicts need the response the
evidence was read from; pre-flag is the only path a flag
takes. A timeout is never a confirm.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
