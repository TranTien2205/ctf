# Step 0: flag location

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Where the flag lives gets recorded at step 0 - it
disqualifies categories before any probe does.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
