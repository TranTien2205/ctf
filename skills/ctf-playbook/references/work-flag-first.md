# Locate the flag before the class

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Where the flag lives (env, db, file, route, harness) decides which
classes can reach it - record it in the ledger at step 0, before
the first hypothesis.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
